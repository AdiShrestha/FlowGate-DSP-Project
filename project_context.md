# Load-Adaptive IIR Filtering — Project Context & Handoff Document

This document was auto-generated to preserve the complete context, history, architectural decisions, and empirical findings of the "Load-Adaptive IIR Filtering" DSP project. If a new AI agent takes over the project, reading this file will provide 100% of the necessary context.

## 1. Project Objective & Narrative
The goal of this project is to produce a submission-ready IEEE conference paper evaluating whether dynamically adapting an IIR filter's pole (smoothing coefficient $\alpha$) in response to streaming system load can preserve detection quality while enabling downstream load shedding.

### **The Final Validated Narrative:**
Across 5 assets, 3 market regimes, and 150 independent trials, **load-driven pole adaptation produces no statistically significant change in detection quality compared to Fixed EMA (ΔAUC = 0.0002, p = 0.67)**. The performance degradation observed in early single-day tests was noise. Combined with load shedding, the load-adaptive configuration achieves a massive throughput gain over Fixed EMA at *zero* average detection-quality cost. 

By contrast, signal-driven filters like KAMA achieve significantly higher AUC (+0.077, p < 0.001) but cannot be dynamically coupled with exogenous system load shedding. This establishes the distinct architectural tradeoff of our proposed system.

## 2. Infrastructure & Codebase Architecture
The project is built in Python 3.12 (with a `.myenv` virtual environment) and relies heavily on pandas, numpy, scipy, and numba.

**Core Pipeline Files (`src/`):**
- `run_all.py`: The master orchestration script that executes data extraction, multi-seed evaluations, and the three main compute experiments (A, B, C).
- `multi_seed_evaluation.py`: Runs the core pipeline across 50 seeds per regime (150 total), applying anomaly injection, executing the DSP filters, and computing ROC-AUC. 
- `evaluate.py` & `detection.py`: Computes local windowed ROC-AUC around anomalies to prevent massive true-negative background noise from destroying the rank-ordering.
- `statistical_tests.py` & `delong.py`: Executes paired DeLong tests and t-tests to evaluate the statistical significance of AUC differences.
- `rrcf_detector.py`: Implements the Robust Random Cut Forest (RRCF) baseline using the `rrcf` library.
- `fp_paradox.py`: Computes Pearson correlation between local phase velocity ($|d\alpha/dt|$) and false positive rates.
- `downstream_cost_measurement.py`: Measures true I/O latency using a UDP loopback socket.

## 3. Key Findings & Empirical Results
The full 150-seed pipeline generated the following verifiable data (saved in `results/tables/`):
1. **Throughput / Downstream Cost**: Real UDP loopback latency measured at **p50 = 3.38µs** (replaces the modeled 5µs).
2. **Detection Quality (Paired t-test over 150 seeds)**:
   - Load-Adaptive EMA (BW-Matched) vs Fixed EMA: `ΔAUC = 0.0002, p = 0.67` (Not Significant).
   - KAMA vs Fixed EMA: `ΔAUC = 0.0768, p < 0.001` (Highly Significant).
   - RRCF vs Fixed EMA: `ΔAUC = 0.0472, p < 0.001` (Highly Significant).
3. **FP-Rate Paradox**: Pearson correlation of `r = -0.034` (p < 10⁻¹³). This formally *refutes* the hypothesis that rapid phase-lag adaptation is the primary driver of false positives.
4. **Pareto Frontier**: Load-Adaptive EMA + Shedding sits strictly on the Pareto frontier, doubling throughput over Fixed EMA without statistically sacrificing ROC-AUC.

## 4. Resolved Bugs & Technical Gotchas
If maintaining this code, be aware of the following resolved issues:
- **DeLong Test Global Concatenation Bug**: Passing raw, globally concatenated z-scores (7.5 million ticks) to a global `roc_auc_score` function yields an AUC of ~0.50. Why? Because z-score baselines vary wildly across assets/days, destroying the global rank order. The actual detection AUC (0.83) is evaluated *locally* around valid anomaly windows. For cross-run statistical significance, we use a paired t-test on the per-seed AUCs instead of a global DeLong test.
- **DeLong Signed Z-Score Bug**: The `detect_anomalies` function returns *signed* Z-scores. To evaluate AUC properly, you must wrap the z-scores in `np.abs()` before scoring, otherwise negative price drops yield ~0.50 AUCs. This was fixed in `multi_seed_evaluation.py`.
- **Multiprocessing Deadlock**: Parallelizing the 150-seed loop via `joblib` caused silent deadlocks on macOS Apple Silicon because of conflicts with Numba JIT compiling inside the workers. The loop is now strictly sequential.
- **Python 3.12 `pkg_resources` Missing**: The `rrcf` library crashes in Python 3.12 because `setuptools` removed `pkg_resources`. The virtual environment must have `setuptools<81` installed (`pip install "setuptools<81"`).

## 5. Next Steps
The Python engineering, data generation, and statistical testing are 100% complete and pushed to Git. All results, tables, and figures reside in `results/`. The only remaining task is for the user (or Claude) to transcribe these exact statistical figures into the LaTeX draft (`report_v2.tex`) for final submission.
