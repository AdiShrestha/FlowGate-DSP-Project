# Load-Adaptive Single-Pole IIR Filtering for Financial Anomaly Detection

**Project Goal**: This project investigates whether driving a single-pole IIR filter's pole from a system-load (backpressure) signal, rather than from the filtered signal's own volatility or error, produces a meaningfully different latency/false-positive trade-off for financial anomaly detection.

### Core Concept: Control-Driven Adaptation
Unlike standard adaptive filters (such as KAMA, adaptive Kalman filters, AEWMA control charts, or VFF-RLS) which use signal-driven adaptation (speeding up or slowing down based on the signal's volatility or efficiency), this project employs **control-driven adaptation**. The filter dynamically widens its effective window (lowers α) under high system backpressure to conserve downstream processing capacity. The closest real-world precedent to this is Adaptive RED in networking, which adapts a downstream decision threshold rather than the smoothing filter's pole itself, and has no formal Z-domain treatment.

### Requirements & Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > **Note:** `numba` is required for the Numba-JIT filter kernels used in Experiments A/B. On Apple Silicon, Numba uses the LLVM backend — first-run JIT compilation takes a few seconds; cached thereafter.
3. Run the complete pipeline end-to-end:
   ```bash
   # Make sure you are in the project root directory
   python -m src.run_all
   ```

---

## Compute Benefit Experiments (Sections A–C)

These three experiments close the critical gap in the paper: the project previously had a complete theoretical (Z-domain) analysis and detection-quality comparison, but had **never measured whether load-adaptive filtering actually saves computational resources** — which is the paper's core premise.

### What Each Experiment Does

| Experiment | Script | What it shows |
|---|---|---|
| **A — Per-Sample Compute Cost** | `src/experiment_a_compute_cost.py` | Apples-to-apples wall-clock timing of all 6 configurations via Numba JIT (removes the compiled-C vs Python-loop confound). Produces median ± IQR per 1,000 samples. |
| **B — Throughput Stability** | `src/experiment_b_throughput_stability.py` | The centerpiece. Sweeps arrival rate λ from empirical (≈8.66 ev/s) to 10×, checking analytically and empirically whether each config's queue stays bounded. Shows the "money shot": Fixed EMA's queue blowing up at a λ where Load-Adaptive + Shedding stays stable. |
| **C — Pareto Curve** | `src/experiment_c_pareto.py` | Plots all 6 configs on (throughput, ROC-AUC) axes, identifies the Pareto-optimal frontier, and writes an **honest numeric conclusion** to `results/compute_benefit_summary.md` — whatever the numbers actually show. |

### The Six Configurations

Splitting "pole adaptation" and "shedding" into orthogonal axes lets you attribute benefit to each mechanism independently:

| Config | Pole adapts to load? | Shedding? |
|---|---|---|
| Fixed EMA | No | No |
| Fixed EMA + Shedding | No | Yes |
| KAMA | No (volatility-driven) | No |
| Butterworth | No | No |
| Load-Adaptive EMA | Yes | No |
| Load-Adaptive EMA + Shedding | Yes | Yes |

### Running the Compute Experiments

**Run on a relatively idle machine for clean timing.** The M3 Air is fanless; sustained compute can throttle partway through a session. Wrap with `caffeinate -i` to prevent sleep/power management:

```bash
# Recommended: run from the project root directory
caffeinate -i python -m src.run_all --with-compute-experiments
```

This does, in order:
1. **Hard gate**: runs `pytest tests/test_numba_parity.py` — if any Numba kernel output deviates from the reference Python loop by more than 1e-9, the experiments abort. Every downstream timing number would be meaningless otherwise.
2. Experiment A (≈5–15 min depending on machine)
3. Experiment B (depends on A's CSV)
4. Experiment C (depends on B's CSV + existing `comparison.csv`)

### New Outputs

| File | Description |
|---|---|
| `results/tables/experiment_a_compute_cost.csv` | Median ± IQR timing per config per input length |
| `results/tables/experiment_metadata.json` | Platform, Python version, trial count — for paper transparency |
| `results/figures/experiment_a_compute_cost.png` | Grouped bar chart (error bars = IQR) |
| `results/tables/experiment_b_throughput.csv` | Max stable λ and ρ per config |
| `results/figures/experiment_b_queue_stability.png` | Money-shot: queue depth at overload λ |
| `results/figures/experiment_b_max_throughput_bar.png` | Max stable throughput bar chart |
| `results/figures/experiment_c_pareto.png` | Pareto curve scatter with frontier |
| `results/compute_benefit_summary.md` | Numeric, non-hedged Pareto conclusion |

---

### Results Summary
Running the pipeline produces 11 key figures in `results/figures/` and a benchmark table in `results/tables/comparison.csv`.

| Filter | Precision | Recall | F1 | Mean Latency | FP Rate (per 1k) | ROC AUC | PR AUC |
|---|---|---|---|---|---|---|---|
| Fixed EMA (0.06) | 0.1730 | 0.0718 | 0.1014 | 1.4000 | 12.1774 | 0.1133 | 0.0540 |
| Load Adaptive EMA | 0.2265 | 0.0519 | 0.0845 | 0.5333 | 6.2958 | 0.0701 | 0.0409 |
| KAMA | 0.4701 | 0.0688 | 0.1201 | 1.3333 | 2.7544 | 0.0995 | 0.0753 |
| Butterworth | 0.0762 | 0.0881 | 0.0817 | 3.7333 | 37.8992 | 0.1772 | 0.0388 |

### Limitations & Methodological Choices
- **Evaluation Methodology**: Point-wise precision, recall, and F1 use a tolerance buffer (±20 samples) around each true anomaly to account for natural filter lag. Full point-adjustment is explicitly **not** used — the literature has shown it artificially inflates scores. Results are reported both **combined** (`results/tables/comparison.csv`) and **per anomaly type** (`comparison_point.csv`, `comparison_level_shift.csv`, `comparison_volatility_burst.csv`).
- **Simulated Backpressure**: Since this is a standalone DSP project with no real stream-processing runtime, backpressure is simulated using a discrete-event single-server queue model — directly analogous to Active Queue Management (RED/Adaptive RED) in networking.
- **Dataset Scope**: Tested on **Binance BTCUSDT daily trade data, 2024-01-01**, sampled at an average arrival rate of ≈8.66 events/s. Results on other dates, symbols, or tick densities may differ.
- **No deep learning**: All filters are classical IIR designs; no neural networks, no learned features. The anomaly detector is a simple rolling-σ z-score threshold, identical across all four filters.
- **Shedding AUC approximation**: ROC-AUC for shedding variants is approximated from their base filter's AUC. Shedding can delay anomaly detection by up to `shed_max_skip` ticks when an onset falls on a skipped tick; this delay is reported explicitly in Experiment B as a genuine, reportable cost.
- **powermetrics caveat**: If `avg_cpu_power_mw` appears in Experiment A's CSV, those values are appropriate for **same-machine, same-session comparison only** (per Apple's own documentation). Do not use them for cross-device claims.
