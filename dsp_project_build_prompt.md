# BUILD PROMPT — Load-Adaptive Single-Pole IIR Filtering for Financial Anomaly Detection

*(Paste everything below this line into a coding-capable AI agent — e.g. Claude Code — as a single instruction. It is self-contained: theory, data sources, exact formulas, file structure, and acceptance criteria are all specified.)*

---

## ROLE AND OBJECTIVE

You are building a complete, reproducible Python research project for a Digital Signal Processing university mini-project. The project studies a **single-pole IIR low-pass filter whose pole is driven by a simulated system-load (backpressure) signal**, rather than by any property of the signal being filtered. You will formally characterize this filter in the Z-domain and benchmark it against three established alternatives for real-time anomaly detection on financial tick data.

Build the entire project end-to-end: data acquisition, filter implementations, Z-domain analysis, anomaly injection, detection, evaluation, visualization, and a results README. Use **Python 3.10+, NumPy, SciPy, pandas, matplotlib**. Do not use deep learning. Do not use C++. This must run end-to-end as a standalone Python project with no external services beyond two public, no-auth-required data downloads.

---

## 1. THEORETICAL FOUNDATION (implement exactly as specified)

### 1.1 Fixed-pole EMA as a first-order IIR filter
```
y[n] = α·x[n] + (1-α)·y[n-1]
H(z) = α / (1 - (1-α)z⁻¹)
```
- Pole location: `z_pole = 1 - α`
- Time constant (samples): `τ = -1/ln(1-α)`
- Half-life (samples): `t½ = ln(0.5)/ln(1-α)`
- DC group delay (samples): `τ_g(0) = (1-α)/α` — derive this from the mean of the impulse response `h[n] = α(1-α)ⁿ`, and **numerically verify it against `scipy.signal.group_delay`** at ω→0 in your analysis notebook. State the derivation in a docstring.

### 1.2 The load-adaptive version
Define a normalized backpressure signal `L[n] ∈ [0, 1]` (see Section 4) and map it to a time-varying α:
```
α[n] = α_max - (α_max - α_min) · L[n]
```
Rationale to state explicitly in code comments and the README: **under high backpressure, the filter should widen its effective window (lower α, pole moves toward z=1, more smoothing, less reactivity)** to conserve downstream processing capacity, and narrow it (higher α) when load is low. This is the opposite mapping direction from every *volatility-driven* adaptive filter in the literature (KAMA, adaptive Kalman, AEWMA control charts), which speed up under high signal activity — make this contrast explicit in code comments, since it is the conceptual crux of the project.

Use defaults `α_min = 0.02`, `α_max = 0.30` (configurable).

### 1.3 Slew-rate limit (stability/validity bound)
Because the analysis treats the filter as quasi-static (frozen-pole) at each instant, bound how fast the pole can move:
```
|α[n] - α[n-1]| ≤ Δα_max   (default Δα_max = 0.01 per sample)
```
Clip α[n] to this bound after computing it from L[n]. Always clip final α to `[1e-4, 1-1e-4]` to guarantee `|pole| < 1` (stability) at every step.

---

## 2. PROJECT STRUCTURE TO CREATE

```
load-adaptive-iir/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                  # downloaded LOBSTER + Binance files
│   └── processed/            # cleaned, resampled tick series (parquet/csv)
├── src/
│   ├── __init__.py
│   ├── data_acquisition.py   # Section 3
│   ├── queue_simulator.py    # Section 4
│   ├── filters.py            # Section 5
│   ├── demo_signals.py       # Section 6A
│   ├── zdomain_analysis.py   # Section 6
│   ├── anomaly_injection.py  # Section 7
│   ├── detection.py          # Section 8
│   ├── evaluate.py           # Section 9
│   └── visualize.py          # Section 10
├── notebooks/
│   └── 01_full_pipeline.ipynb   # runs everything end-to-end, calls into src/
├── results/
│   ├── figures/
│   └── tables/
└── tests/
    └── test_filters.py        # Section 12
```
`requirements.txt`: `numpy, scipy, pandas, matplotlib, requests, tqdm, pytest`.

---

## 3. DATA ACQUISITION (`src/data_acquisition.py`)

Use **two free, no-API-key data sources**. Implement both; let the user pick via a config flag.

### 3.1 LOBSTER sample data (equities, NASDAQ)
- Free sample files exist for tickers **AAPL, AMZN, GOOG, INTC, MSFT** at `https://lobsterdata.com` (academic sample download — fetch the page/instructions; if direct programmatic download isn't available without registration, write a loader that reads locally-placed sample CSVs the user downloads manually, and document this clearly in the README).
- **Message file** columns (no header in the raw file — apply these names): `Time, Type, Order_ID, Size, Price, Direction`. `Time` is seconds after midnight (decimal, ms-to-ns precision). `Type` is an integer event code (new limit order, cancellation, deletion, execution visible, execution hidden, trading halt — look up the exact code table in the README shipped with the LOBSTER download and hard-code it in a dict in the loader, with a comment citing the source).
- **Orderbook file** columns repeat per level: `Ask_Price_1, Ask_Size_1, Bid_Price_1, Bid_Size_1, Ask_Price_2, ...`. Price scaling: LOBSTER prices are integers; divide by the documented scale factor (check the README in the downloaded sample — commonly price×10000) to get dollars. Implement this as a configurable constant, not a hard-coded assumption.
- From these two files, construct a **mid-price tick series**: `mid_price[n] = (Ask_Price_1[n] + Bid_Price_1[n]) / 2`, indexed by `Time`.

### 3.2 Binance public bulk data (crypto, no API key, no rate limits)
- Use the public bulk data portal described at `https://github.com/binance/binance-public-data` (data served from `https://data.binance.vision`). Download **daily `trades` ZIP/CSV files** for a liquid pair (default `BTCUSDT`, configurable) for a 1–3 day window.
- Raw trades columns: `trade Id, price, qty, quoteQty, time, isBuyerMaker` (verify exact column order against the README in the downloaded zip, since Binance has changed timestamp units — from Jan 2025 onward SPOT timestamps are in **microseconds**, not milliseconds; handle both by checking the value's magnitude in your loader).
- Build a tick series directly from the `price` and `time` columns.

### 3.3 Output contract
Both loaders must return a `pandas.DataFrame` with columns `['timestamp', 'price']`, sorted, deduplicated, and saved to `data/processed/<source>_<symbol>_<date>.parquet`. Write a `load_tick_series(source: str, symbol: str, date_range: tuple) -> pd.DataFrame` function as the single entry point used by everything downstream.

---

## 4. SYNTHETIC BACKPRESSURE / LOAD SIGNAL (`src/queue_simulator.py`)

Since this is a standalone DSP project (no real stream-processing runtime), simulate backpressure **honestly and defensibly** using a single-server queue model — this mirrors the Active-Queue-Management precedent (RED/Adaptive RED in networking, which also derives an EWMA-style congestion signal from queue occupancy) rather than fabricating an arbitrary signal.

Implement a discrete-event queue simulator:
- **Arrivals**: the tick events themselves (their inter-arrival times from the real data), optionally with an injected synthetic burst multiplier in user-selected sub-intervals (to guarantee the load signal actually varies — real tick data alone may not show enough load variation).
- **Service**: a single server draining the queue at a configurable fixed rate `μ` (events/sec). Choose `μ` so the queue is non-trivially loaded but not permanently saturated (target average utilization ρ = λ/μ ≈ 0.6–0.8; compute λ from the data and report it).
- **State update per event**: `q[n] = max(0, q[n-1] + arrivals_since_last_service - service_capacity_since_last_service)`.
- **Normalize**: `L[n] = clip(q[n] / q_max, 0, 1)` where `q_max` is a configurable buffer capacity (e.g., the 99th percentile of the simulated queue depth over a calibration run).

Output a `pandas.Series` `L[n]` aligned to the same timestamps as the price series. Plot `q[n]` and `L[n]` over time as a sanity check before proceeding (save to `results/figures/queue_simulation.png`).

---

## 5. FILTER IMPLEMENTATIONS (`src/filters.py`)

Implement all four as functions with signature `filter_name(x: np.ndarray, **params) -> np.ndarray`, each returning the filtered series `y[n]` (same length as `x`), plus a parallel function returning the **pole trajectory** `pole[n]` (constant for fixed-pole filters).

1. **`fixed_ema(x, alpha)`** — direct recursive implementation of Section 1.1. This is your fixed-pole baseline at two settings: `alpha=0.06` (RiskMetrics-style, since their λ=0.94 maps to α=1-λ=0.06) and `alpha=0.30` (fast/KAMA-comparable).
2. **`load_adaptive_ema(x, L, alpha_min=0.02, alpha_max=0.30, d_alpha_max=0.01)`** — Section 1.2 + 1.3. This is your novel filter.
3. **`kama(x, er_period=10, fast_period=2, slow_period=30)`** — Kaufman's Adaptive Moving Average:
   - `ER[n] = |x[n] - x[n-er_period]| / Σ_{i=n-er_period+1}^{n} |x[i] - x[i-1]|`
   - `fastSC = 2/(fast_period+1)`, `slowSC = 2/(slow_period+1)`
   - `SC[n] = (ER[n]·(fastSC - slowSC) + slowSC)²`
   - `KAMA[n] = KAMA[n-1] + SC[n]·(x[n] - KAMA[n-1])`
   - This is your **signal-driven adaptive** baseline (volatility/efficiency-driven, the direct conceptual contrast to your load-driven filter).
4. **`butterworth_lowpass(x, order=4, cutoff_hz=..., fs=...)`** — explicitly demonstrate the bilinear transform per the syllabus: design the **analog** prototype with `scipy.signal.butter(order, 2*pi*cutoff_hz, btype='low', analog=True, output='zpk')`, then map to digital with `scipy.signal.bilinear_zpk(z, p, k, fs)`, then `scipy.signal.zpk2tf` to get `b, a` for `scipy.signal.lfilter`. Do not take the shortcut of calling `butter(..., fs=fs)` directly — the point is to show the bilinear-transform step explicitly, with a comment explaining the s→z substitution.

---

## 6. Z-DOMAIN ANALYSIS (`src/zdomain_analysis.py`)

For the load-adaptive filter, treat it as a frozen-time (quasi-static) system at a representative sweep of α values, e.g. `np.linspace(alpha_min, alpha_max, 7)`. For each α in the sweep:
- Build `b = [alpha]`, `a = [1, -(1-alpha)]`.
- Get poles/zeros via `scipy.signal.tf2zpk`.
- Get frequency response via `scipy.signal.freqz(b, a, worN=2048, fs=fs)`; plot magnitude in dB and phase in degrees.
- Get group delay via `scipy.signal.group_delay((b, a), w=..., fs=fs)`; confirm the DC value matches the closed-form `(1-α)/α` from Section 1.1.

Produce:
- **Pole-zero plot**: all 7 poles on the unit circle in one figure, color-coded by α, with the unit circle drawn for reference.
- **Bode-style overlay**: magnitude and phase response for all 7 α values on shared axes (small multiples or overlaid with a colorbar/legend).
- **Pole trajectory over time**: `pole[n] = 1 - α[n]` plotted against the actual backpressure-driven α[n] from a real run (not just the synthetic sweep), overlaid with `L[n]` on a secondary axis, to show the pole physically moving in response to load.
- A short written derivation (as a markdown cell in the notebook or docstring) of why the slew-rate bound in Section 1.3 is necessary for the frozen-time approximation to remain valid — relate this informally to how slowly the pole must move relative to the filter's own time constant `τ` for a frozen-time frequency response to be meaningful at all.

---

## 6A. CANONICAL SIGNAL/SYSTEMS VISUALIZATIONS (`src/demo_signals.py`)

This is a DSP course mini-project, so alongside the financial-data results you must also produce the classic signals-and-systems style demonstrations a DSP audience expects: synthetic test waveforms, impulse/step responses, and spectra — independent of the financial application. Build these on **synthetic signals you construct yourself**, not the tick data (the tick-data spectral views come in 6A.4).

### 6A.1 Synthetic test signal
Construct one canonical demo signal, sampled at a configurable `fs` (default 100 Hz), duration ~10 s:
```
x[n] = A1·sin(2π f1 n/fs)        # slow "trend" component, f1 = 0.2 Hz
     + A2·sin(2π f2 n/fs)        # faster "market noise" component, f2 = 5 Hz
     + A3·sin(2π f3 n/fs)        # high-frequency jitter, f3 = 20 Hz
     + w[n]                      # additive white Gaussian noise
     + spikes[n]                 # a few isolated unit impulses (Dirac-like) at random locations
```
Default amplitudes `A1=1.0, A2=0.3, A3=0.1`, noise std 0.05. This signal exists purely to demonstrate low-pass filtering behavior cleanly: a slow trend that should pass through, faster oscillations that should be progressively attenuated as the pole moves toward `z=1`, and impulses that test transient response.

### 6A.2 Impulse and step response
For `fixed_ema` at 3 representative α values (e.g. 0.3, 0.1, 0.03) and for `load_adaptive_ema` frozen at the same 3 α values:
- **Impulse response**: feed a unit impulse `δ[n]`, plot `h[n] = α(1-α)ⁿ` for ~50 samples per α, all on one axes, legend by α. Annotate each curve's time constant `τ` from Section 1.1.
- **Step response**: feed a unit step `u[n]`, plot the rise to steady state for the same α values, annotate the 90%-rise time and compare visually to `τ` and the half-life formula.
Save as `impulse_response.png` and `step_response.png`.

### 6A.3 Time-domain + spectrum, before/after filtering (synthetic signal)
Apply all 4 filters (Section 5) to the synthetic signal from 6A.1. For each filter, produce a 2×1 figure:
- **Top**: raw `x[n]` and filtered `y[n]` overlaid in the time domain, zoomed to show ~2 seconds clearly (so individual oscillations of f2/f3 are visible being smoothed).
- **Bottom**: magnitude spectrum of `x` vs `y` computed with `scipy.fft.rfft` (or `scipy.signal.welch` for a smoother PSD estimate), x-axis in Hz, y-axis in dB, with vertical dashed lines marking f1, f2, f3 so the viewer can see exactly which components survive and which are attenuated.
Save one combined figure per filter: `spectrum_demo_fixed_ema.png`, `spectrum_demo_load_adaptive.png`, `spectrum_demo_kama.png`, `spectrum_demo_butterworth.png`.

### 6A.4 Spectral view of the real tick data
Repeat the magnitude-spectrum comparison from 6A.3 (raw vs. each filtered output, `scipy.signal.welch` PSD, dB scale) on the **real price series** from Section 3, over a representative window (e.g. 5,000 samples). Save as `psd_comparison_real_data.png`. This connects the synthetic-signal intuition back to the actual financial application.

### 6A.5 Time-varying frequency response (the flagship visualization)
This is the single most important plot for showing what a *moving pole* actually does, and it doesn't exist anywhere in the baseline filters since their poles are fixed. Build it as follows:
- Take a real run of `load_adaptive_ema` with its α[n] trace.
- Downsample α[n] into ~100 equally-spaced time blocks across the run (e.g., one block every N samples).
- For each block's representative α, compute the frozen-time frequency response magnitude `|H(e^{jω})|` in dB via `scipy.signal.freqz`, over a fixed frequency grid.
- Stack these as a 2D array: time blocks (x-axis) × frequency (y-axis), magnitude in dB as color — render with `plt.pcolormesh` or `plt.imshow` as a heatmap, much like a spectrogram, but where the "spectrogram" is of the *filter's own frequency response* over time, not of a signal.
- Overlay the normalized backpressure `L[n]` as a line plot on a secondary y-axis or a thin strip above the heatmap, so the viewer can directly see the filter's passband narrowing (shrinking toward DC) exactly when backpressure rises.
- Save as `time_varying_frequency_response.png`. Label it clearly in the README as the figure that most directly visualizes the project's core contribution.

---

## 7. SYNTHETIC ANOMALY INJECTION (`src/anomaly_injection.py`)

Real tick data has no ground-truth anomaly labels, so inject synthetic ones with known locations (standard practice in the time-series anomaly detection literature, used precisely because labeled real-world anomalies are unavailable or unreliable). Implement three types, each returning `(x_injected, ground_truth_mask)`:

1. **Point anomaly**: single-sample additive spike, magnitude = `k × rolling_std` (default k=8), at randomly chosen indices (seeded).
2. **Level shift**: a sustained step change in mean over a window of `w` samples (default w = 50–200, configurable), magnitude = `k × rolling_std`.
3. **Volatility burst**: locally inflate the noise variance over a window (multiply local returns by a factor, default 5×) without shifting the mean.

Inject a configurable number of each type (default 5 each) at random non-overlapping locations (fixed random seed = 42 for reproducibility) into a clean held-out segment of the real price series. Store `ground_truth_mask` as a boolean array, one per injected interval, plus a combined mask.

---

## 8. DETECTION RULE (`src/detection.py`)

For every filter output `y[n]`, compute the residual `r[n] = x[n] - y[n]`, then a normalized residual `z[n] = r[n] / σ_r[n]` where `σ_r[n]` is a rolling standard deviation of `r` (window default 100 samples, causal/trailing only — no look-ahead). Flag `detected[n] = 1` if `|z[n]| > threshold` (default 3.0, but sweep this for the ROC/PR curves in Section 9). This mirrors EWMA-control-chart-style detection (residual vs. control limits), giving you a fair, identical detection rule across all four filters so differences in results are attributable to the filter, not the detector.

---

## 9. EVALUATION (`src/evaluate.py`)

For each of the 4 filters, on each injected-anomaly test set:
- **Point-wise precision, recall, F1** with a tolerance buffer of `±k` samples around each true anomaly interval (default k=20, to account for filter lag — document this choice and do **not** use full point-adjustment, since the literature has shown point-adjustment artificially inflates scores; state this explicitly as a methodological choice in the README).
- **Detection latency**: for each true anomaly, the number of samples between its onset and the first flagged detection inside the tolerance window (NaN if missed).
- **False positive rate**: flagged detections per 1000 samples outside any true-anomaly tolerance window.
- **ROC-AUC and PR-AUC**: sweep the threshold in Section 8 over a reasonable range (e.g. 1.0 to 6.0) and compute the curve.

Output a single results table (`results/tables/comparison.csv` and a markdown version) with rows = filters, columns = [precision, recall, F1, mean_latency, FP_rate, ROC_AUC, PR_AUC], run separately for each anomaly type and combined.

---

## 10. VISUALIZATION (`src/visualize.py`)

Produce and save (PNG, 150dpi) to `results/figures/`:

**Filter/analysis figures:**
1. `pole_zero_sweep.png` — Section 6 pole-zero plot.
2. `frequency_response_sweep.png` — Section 6 Bode-style overlay.
3. `pole_trajectory_vs_load.png` — Section 6 time-domain pole/load overlay.
4. `queue_simulation.png` — Section 4 sanity check.

**Classic signals-and-systems figures (Section 6A, from `demo_signals.py`):**
5. `impulse_response.png` and `step_response.png` — Section 6A.2.
6. `spectrum_demo_fixed_ema.png`, `spectrum_demo_load_adaptive.png`, `spectrum_demo_kama.png`, `spectrum_demo_butterworth.png` — Section 6A.3, one per filter, each with time-domain (top) and spectrum (bottom) subplots.
7. `psd_comparison_real_data.png` — Section 6A.4.
8. `time_varying_frequency_response.png` — Section 6A.5, the flagship "moving filter" heatmap.

**Application/results figures:**
9. `time_domain_comparison.png` — raw price + all 4 filter outputs + true/detected anomaly markers, on one shared time axis (use subplots if needed for readability).
10. `roc_pr_curves.png` — ROC and PR curves for all 4 filters, side by side.
11. `metrics_bar_comparison.png` — grouped bar chart of F1, latency, FP-rate across the 4 filters.

---

## 11. README.md REQUIREMENTS

Write a README that includes:
- One-paragraph project summary and the precise research question: *does driving a single-pole IIR filter's pole from a system-load/backpressure signal, rather than from the filtered signal's own volatility or error, produce a meaningfully different latency/false-positive trade-off for financial anomaly detection?*
- One paragraph stating that this is a control-driven adaptation, contrasted explicitly with the signal-driven adaptation used by every other adaptive-EMA scheme in the literature (KAMA, adaptive Kalman filtering, AEWMA control charts, VFF-RLS) — and that the closest real-world precedent (Adaptive RED in networking) adapts a downstream parameter, not the filter pole itself, and has no Z-domain treatment.
- Exact setup/run instructions (`pip install -r requirements.txt`, then `python -m src.run_all` or open `notebooks/01_full_pipeline.ipynb`).
- A results summary table (auto-generated from `results/tables/comparison.csv`).
- A short "Limitations" section: backpressure here is simulated (no real stream-processing runtime), the tolerance-window evaluation is a simplification, and the dataset window is limited (state exact symbol/date range used).

---

## 12. TESTS (`tests/test_filters.py`)

Write lightweight `pytest` sanity checks, not a full suite:
- `fixed_ema` with constant input converges to that constant.
- Pole location numerically equals `1 - alpha` for `fixed_ema`.
- `load_adaptive_ema` never produces `alpha` outside `[1e-4, 1-1e-4]` even with adversarial/extreme `L` input (test with `L` containing 0s, 1s, and out-of-range values).
- `load_adaptive_ema` respects the slew-rate bound: `max(abs(diff(alpha_trace))) <= d_alpha_max + 1e-9`.
- DC group delay from `scipy.signal.group_delay` at `w≈0` matches `(1-alpha)/alpha` within 1% for `fixed_ema` at 3 different alpha values.
- `kama` and `butterworth_lowpass` produce finite, non-NaN output on a synthetic noisy sine wave test input.

---

## 13. ACCEPTANCE CRITERIA

The project is complete when:
1. `python -m src.run_all` (or the single notebook) runs start-to-finish with no manual intervention beyond the one-time manual LOBSTER sample download (if programmatic download isn't available) and produces every figure listed in Section 10 (filter/analysis, classic signals-and-systems, and application/results — 11 figures total) plus the results table.
2. `pytest tests/` passes.
3. The README's results table is populated with real numbers from an actual run, not placeholders.
4. Every formula in Section 1 appears in code with a comment citing this spec section number, so a reader can trace implementation back to the theory.

Build this now, file by file, starting with `requirements.txt` and `src/filters.py`, then working outward through data acquisition, the queue simulator, Z-domain analysis, anomaly injection/detection/evaluation, and finally visualization and the README.
