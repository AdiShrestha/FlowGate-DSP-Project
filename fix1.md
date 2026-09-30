# BUILD PROMPT — Compute/Throughput Benefit Experiments for the Load-Adaptive IIR Filtering Project

*(Paste everything below this line into a coding-capable AI agent — e.g. Claude Code, run inside the existing `load-adaptive-iir/` project directory. This EXTENDS the existing project — do not recreate files that already exist; import from and build on top of them. Platform: Apple M3 MacBook Air, macOS 26.5.1, Python 3.12.)*

---

## ROLE AND OBJECTIVE

You are extending an existing, working Python research project that studies a load-adaptive single-pole IIR filter for financial anomaly detection. The project currently has a complete theoretical (Z-domain) analysis and a complete detection-quality comparison against three baselines (Fixed EMA, KAMA, Butterworth), but it has a critical, identified gap: **it has never measured whether load-adaptive filtering actually saves any computational resources**, which is the entire premise the paper rests on (trading detection sensitivity for resource conservation). Your job is to close this gap with three new experiments, built correctly, and produce publication-ready figures and tables.

**Before writing any experiment code, internalize this:** a single-pole EMA recurrence `y[n] = α·x[n] + (1-α)·y[n-1]` costs the same number of FLOPs regardless of α. Changing the smoothing constant alone does **not** save compute. The actual compute-saving mechanism you are adding is **load shedding** — skipping the filter/detector pipeline entirely for some ticks when backpressure is high. Do not skip this step and jump straight to benchmarking the existing filters as-is; that would only confirm there's currently no benefit to measure.

---

## SECTION 1: NEUTRALIZE THE COMPILED-C-VS-PYTHON-LOOP CONFOUND

Currently, Fixed EMA and Butterworth likely use `scipy.signal.lfilter` (compiled C internally), while KAMA and Load-Adaptive EMA require a Python loop (their coefficients change every sample, so `lfilter`'s fixed-coefficient path doesn't apply). **Any timing comparison across these implementations right now would measure language/compilation tier, not algorithmic cost.** Fix this by reimplementing the recursive core of **all four filters** as Numba-JIT-compiled functions, so every comparison in this prompt is apples-to-apples.

Create `src/numba_filters.py`:

```python
import numpy as np
from numba import njit

@njit(cache=True)
def fixed_iir_direct_form_ii(x, b, a):
    """
    Generic fixed-coefficient Direct Form II Transposed IIR filter,
    matching scipy.signal.lfilter's algorithm exactly (a[0] assumed 1.0,
    normalize b,a by a[0] before calling if not).
    Used for: Butterworth (any order), and as a validation path for Fixed EMA.
    """
    order = max(len(a), len(b)) - 1
    z = np.zeros(order)
    y = np.empty_like(x)
    b_pad = np.zeros(order + 1); b_pad[:len(b)] = b
    a_pad = np.zeros(order + 1); a_pad[:len(a)] = a
    for n in range(len(x)):
        y[n] = b_pad[0] * x[n] + (z[0] if order > 0 else 0.0)
        for i in range(order - 1):
            z[i] = b_pad[i+1] * x[n] + z[i+1] - a_pad[i+1] * y[n]
        if order > 0:
            z[order-1] = b_pad[order] * x[n] - a_pad[order] * y[n]
    return y

@njit(cache=True)
def time_varying_first_order_ema(x, alpha_trace):
    """
    First-order IIR with a per-sample, precomputed alpha[n].
    Used for: KAMA and Load-Adaptive EMA (alpha_trace computed once,
    vectorized, BEFORE calling this — only the unavoidable recursive
    accumulation happens inside the njit loop).
    """
    y = np.empty_like(x)
    y[0] = x[0]
    for n in range(1, len(x)):
        a = alpha_trace[n]
        y[n] = a * x[n] + (1.0 - a) * y[n-1]
    return y
```

Refactor the existing filter functions in `src/filters.py` so each one:
1. Computes its coefficient(s) — fixed `(b,a)` for Butterworth, or a precomputed `alpha_trace` array for Fixed EMA (constant array), KAMA, and Load-Adaptive EMA — using the EXISTING logic already in the project (do not change the math).
2. Calls the appropriate Numba kernel above to do the actual recursive filtering.

**Validation requirement (do this before anything else in this prompt):** for each filter, compare the Numba-kernel output against the existing (currently-deployed) implementation's output on the same input, and assert `np.allclose(old_output, new_output, atol=1e-9)`. Add this as `tests/test_numba_parity.py`. Do not proceed to any benchmarking until all four pass.

**Warm-up requirement:** call every Numba function once on a small dummy array immediately after import, before any timed region in any experiment below, so JIT compilation time is never counted as algorithmic cost.

---

## SECTION 2: ADD THE ACTUAL COMPUTE-SAVING MECHANISM — LOAD SHEDDING

This is the single most important addition in this prompt. Create `src/load_shedding.py`.

### 2.1 Mechanism
Given the existing normalized backpressure signal `L[n] ∈ [0,1]` from `queue_simulator.py`, decide, per sample, whether to actually run the filter+detector pipeline on that tick or skip it (carry the last output forward, do not invoke the filter or detector).

Use a **deterministic** stride rule (not random skipping) so throughput results are reproducible without needing to average over random seeds:

```python
def compute_processing_mask(L, shed_max_skip=4):
    """
    L: array of backpressure values in [0,1].
    shed_max_skip: maximum number of consecutive ticks that may be skipped
                   at L=1 (e.g. 4 means process at least 1 in 5 ticks under
                   max load).
    Returns: boolean array, True = process this tick, False = skip it.
    """
    n = len(L)
    process = np.zeros(n, dtype=np.bool_)
    ticks_since_processed = 0
    for i in range(n):
        target_skip = int(round(shed_max_skip * L[i]))   # 0 at L=0, shed_max_skip at L=1
        if ticks_since_processed >= target_skip:
            process[i] = True
            ticks_since_processed = 0
        else:
            ticks_since_processed += 1
    return process
```

### 2.2 How a skipped tick is handled downstream
- The filter is **not invoked** on a skipped tick (this is what saves the compute — the Numba kernel call itself doesn't happen for that index; implement this as: run the filter only on the subsequence of processed ticks, then forward-fill the output array at skipped indices to the last processed value).
- The detector only evaluates `|r/σ|>3` on processed ticks. A skipped tick cannot trigger a detection.
- **Important and worth reporting honestly**: if a true anomaly's onset falls on a skipped tick, detection of it is delayed until the next processed tick. Track and report this explicitly as a metric: "mean additional delay attributable to shedding" (separate from the filter's own lag), since this is a genuine, reportable cost of the mechanism, not something to hide.

### 2.3 Shedding as an independent, composable layer
Shedding must be implemented so it can be applied to **any** of the four filters, independently of whether that filter's own pole/coefficient also adapts to load. This gives you the configurations needed for Experiment C's Pareto plot:

| Configuration | Pole/coefficient adapts to load? | Shedding applied? |
|---|---|---|
| Fixed EMA (baseline) | No | No |
| Fixed EMA + Shedding | No | Yes |
| KAMA (baseline) | No (adapts to volatility, not load) | No |
| Butterworth (baseline) | No | No |
| Load-Adaptive EMA (existing, pole-only) | Yes | No |
| Load-Adaptive EMA + Shedding | Yes | Yes |

Implement all six as named configurations available to every experiment below (extend whatever config/registry structure `src/evaluate.py` currently uses, do not duplicate logic).

---

## SECTION 3: EXPERIMENT A — Controlled Per-Sample Compute Cost

Create `src/experiment_a_compute_cost.py`.

For each of the six configurations in Section 2.3, on the real tick data already loaded by the project, at minimum 3 input lengths (10k, 100k, and the full available series):

1. Warm up (one untimed call).
2. Use `timeit.repeat(stmt, repeat=20, number=1)` (NOT a single `timeit.timeit()` call) to collect 20 independent timings.
3. **Randomize the order in which configurations are timed** across the full run (do not time all of config A's repeats, then all of config B's — interleave them), to spread any thermal-throttling drift evenly rather than systematically penalizing whichever filter runs last. (The M3 Air is fanless; sustained heavy loops can throttle partway through a long benchmark session.)
4. Report the **median** time (not mean — minimum/median is the standard recommendation for microbenchmarks since the mean gets dragged upward by occasional OS scheduling noise) per 1,000 samples, plus the interquartile range.
5. Run the whole script wrapped with `caffeinate -i` (note this in the README run instructions) to prevent the Mac from sleeping/power-managing mid-benchmark.
6. Save `platform.platform()`, `platform.processor()`, Python version, and trial count to `results/tables/experiment_metadata.json` for transparency in the paper.

Save results to `results/tables/experiment_a_compute_cost.csv` with columns: `config, samples, median_time_per_1k_ms, iqr_ms`.

Produce `results/figures/experiment_a_compute_cost.png`: grouped bar chart, one group per input length, bars colored by configuration, error bars from IQR.

---

## SECTION 4: EXPERIMENT B — Sustainable Throughput Under Overload (the centerpiece)

Create `src/experiment_b_throughput_stability.py`. This is the experiment that can actually demonstrate a benefit, because it tests system-level stability, not raw filter speed.

### 4.1 Method
1. From Experiment A, derive each configuration's effective **service rate** `μ_config = 1 / median_time_per_sample_seconds`.
2. For shedding-enabled configurations, the *effective* service rate at a given load level is higher than the raw per-sample rate, because some ticks aren't processed at all — compute this properly: `μ_effective(L) = μ_raw / (1 - shed_fraction(L))`, where `shed_fraction(L)` is the empirical fraction of ticks skipped at backpressure level `L` under the rule from Section 2.1.
3. Sweep a synthetic arrival rate λ from the real data's empirical rate (≈8.66 events/s) up to at least 10× that, in increments (e.g., 10 points log-spaced).
4. For each λ and each configuration, compute utilization `ρ = λ / μ_effective`. Run the existing queue simulator forward for a fixed simulated duration at this λ and confirm whether simulated queue depth stays bounded or diverges (standard M/M/1-style instability check: flag unstable if `ρ ≥ 1` analytically, AND confirm empirically that the simulated queue depth trends upward without bound over the run rather than reaching a steady state).
5. Record, per configuration, the **maximum stable λ** (the breaking point).

### 4.2 Output
- `results/tables/experiment_b_throughput.csv`: columns `config, max_stable_lambda_events_per_sec, rho_at_empirical_lambda`.
- `results/figures/experiment_b_queue_stability.png`: pick one λ value that is unstable for the plain Fixed EMA baseline but stable for Load-Adaptive EMA + Shedding; plot simulated queue depth over time for both configurations on the same axes — this should be the paper's "money shot" figure, making the tradeoff visually obvious in one glance.
- `results/figures/experiment_b_max_throughput_bar.png`: bar chart of max stable λ per configuration.

---

## SECTION 5: EXPERIMENT C — Detection Quality vs. Compute Cost Pareto Curve

Create `src/experiment_c_pareto.py`.

For each of the six configurations:
- x-axis: max stable λ from Experiment B (higher = more throughput headroom = "cheaper").
- y-axis: combined ROC-AUC from the existing detection-quality evaluation (already computed elsewhere in the project — reuse it, do not recompute).

Plot all six as a scatter, label each point, and **identify and visually highlight the Pareto-optimal frontier** (configurations not strictly dominated by any other point on both axes — i.e., no other configuration has both higher throughput AND higher ROC-AUC). Save as `results/figures/experiment_c_pareto.png`.

Write a short, plain-language interpretation to `results/compute_benefit_summary.md`: state explicitly, using the actual numbers produced, whether Load-Adaptive EMA + Shedding lands on the Pareto frontier (genuinely better tradeoff than all baselines), is dominated by some combination of baselines (no advantage demonstrated), or sits in between. **Do not pre-write or assume this conclusion — report whatever the numbers actually show.**

---

## SECTION 6: OPTIONAL ENERGY MEASUREMENT (macOS/Apple Silicon specific)

If `sudo` access is available in the environment (try it; if it prompts and isn't available non-interactively, skip gracefully and log a note rather than failing the whole experiment), wrap Experiment A/B with `powermetrics` logging:

```python
import subprocess
def get_cpu_power_mw():
    try:
        out = subprocess.run(
            ["sudo", "powermetrics", "-n", "1", "--samplers", "cpu_power"],
            capture_output=True, text=True, timeout=5
        )
        for line in out.stdout.splitlines():
            if "CPU Power" in line:
                return float(line.split(":")[1].strip().split()[0])
    except Exception:
        return None
```
Log average CPU power per configuration during Experiment A as a secondary column in `experiment_a_compute_cost.csv` (`avg_cpu_power_mw`, nullable). Explicitly caveat in `compute_benefit_summary.md` that `powermetrics` power values are appropriate for same-machine, same-session comparison only (per Apple's own documentation), not for cross-device claims.

---

## SECTION 7: TESTS

Add to `tests/`:
- `test_numba_parity.py` (Section 1): Numba kernels match existing implementations within `atol=1e-9` for all four filters.
- `test_load_shedding.py`: `compute_processing_mask` returns all-True at `L=0` everywhere (no shedding at zero load), returns the expected stride pattern at `L=1` everywhere, never produces a gap longer than `shed_max_skip+1` ticks, and runs without error on edge-case inputs (`L` containing NaN should raise, not silently misbehave).
- `test_queue_stability_sanity.py`: a synthetic case with `λ ≫ μ` must be flagged unstable; a synthetic case with `λ ≪ μ` must be flagged stable — sanity-checks the stability-detection logic itself before trusting it on real configurations.

---

## SECTION 8: INTEGRATION

- Add a `--with-compute-experiments` flag to the existing `src/run_all.py` entry point (these experiments take longer than the rest of the pipeline; keep them opt-in rather than always-on).
- Update the project's `README.md` with: what these three experiments are, why they exist (the gap they close), exact run command including the `caffeinate -i` wrapper, and a note to run them on a relatively idle machine for clean timing.
- Do not modify or remove any existing detection-quality results, figures, or tables — this is a strict addition.

---

## SECTION 9: ACCEPTANCE CRITERIA

The work is complete when:
1. `pytest tests/` passes, including the three new test files.
2. `python -m src.run_all --with-compute-experiments` (wrapped in `caffeinate -i`) runs to completion and produces all 6 new files listed in Sections 3–5 (3 figures, 2 CSVs, 1 metadata JSON) plus `results/compute_benefit_summary.md`.
3. `compute_benefit_summary.md` contains a specific, numeric, non-hedged statement of where Load-Adaptive EMA + Shedding actually lands relative to the Pareto frontier — not a restatement of the methodology, an actual reported finding.
4. Every new figure is captioned-ready (clear title, axis labels, legend) so it can be dropped directly into the existing IEEE LaTeX report's Results section with minimal editing.

Build this now, starting with Section 1 (Numba parity, with tests passing before moving on), then Section 2 (load shedding), then Experiments A, B, C in that order, then Sections 6–8.