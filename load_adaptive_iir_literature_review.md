# Load-Adaptive Single-Pole IIR Filtering for Financial Anomaly Detection
### Literature Review and Research Gap Analysis

---

## 1. Executive Summary

Every adaptive-smoothing technique surveyed below — across finance, statistics, and classical adaptive filter theory — adapts its parameter using a signal derived **from the series being filtered itself**: forecast error, mean-square error, volatility, an efficiency ratio, or an estimated shift. None of them drive the filter's pole using a signal that is **exogenous to the data** — i.e., a measure of computational/system load, arrival-rate pressure, or backpressure in the processing pipeline. The closest real-world precedent (Active Queue Management in networking) does use a load-like signal, but it adapts a *downstream decision threshold*, not the smoothing filter's pole itself, and it has never been given a formal Z-domain treatment or applied to anomaly detection. This is the gap your mini-project sits in: a single-pole IIR filter whose pole location is driven by a backpressure/load signal, analyzed formally in the Z-domain, and evaluated for anomaly detection on financial tick data.

---

## 2. The Mechanism, Restated in DSP Terms

A standard EMA is a first-order IIR low-pass filter:

```
y[n] = α·x[n] + (1-α)·y[n-1]
H(z) = α / (1 - (1-α)z⁻¹)
```

with a single pole at `z = 1-α`. The pole's distance from the origin sets the filter's effective memory and -3dB cutoff frequency. KLStream-style adaptation makes α a function of a backpressure/load signal `L(t)`, so the pole moves along the real axis in response to *system state*, not signal content. This is structurally a time-varying-pole IIR filter, but with an unusual adaptation driver.

---

## 3. The Literature Landscape

### 3.1 Adaptive moving averages in finance practice

**Kaufman's Adaptive Moving Average (KAMA)**, introduced by Perry Kaufman, adjusts its smoothing behavior to the relative noise or choppiness in market movements, following price faster when movements are efficient and directional and slower when they are choppy or inefficient. The driver is an **Efficiency Ratio**: the ratio represents the absolute change in price over a period relative to the total bar-by-bar change within that period — a value near 1 means efficient, directional movement; near 0 means choppy, inefficient movement.

**RiskMetrics EWMA volatility** (J.P. Morgan, 1994/2006), the industry-standard volatility estimator, uses a **fixed** decay factor: RiskMetrics popularized EWMA with λ = 0.94 for daily data, finding this value produces variance forecasts closest to realized variance across many market variables, with a half-life of a shock at λ = 0.94 of about 11.2 days. Later work has explored optimal fixed λ per forecast horizon, but the recommended RiskMetrics value of 0.97 ranked second with only a very small increase in error compared to the optimal value found empirically — the search has stayed within "best fixed λ" or "λ optimized for forecast accuracy," not load-driven adaptation.

**Driver type: signal-derived (efficiency/volatility of the series itself).**

### 3.2 Classical adaptive filter theory (LMS/RLS family)

**Variable Step-Size LMS (VSS-LMS)**, dating to Kwong & Johnston's 1992 result, adapts the LMS step size using the error signal: the step size increases or decreases as the mean-square error increases or decreases, allowing the adaptive filter to track changes in the system as well as produce a small steady state error. Modern variants (kernel-based, hyperbolic-tangent-based) all preserve this error-driven structure.

**Variable Forgetting Factor RLS (VFF-RLS)** is the closest classical analogue to a "moving pole," since the forgetting factor plays the same role as `1-α` in an EMA. Yet every variant found adapts the forgetting factor from properties of the estimation error: one major line of work computes it from the dynamic equation of the gradient of mean-square error, while gradient-free numeric variants govern the time-varying kernel via a first-order Gauss–Markov stochastic difference equation built from a state-estimation formulation of the tracking problem — still internal to the signal model, not driven by external system load.

**Driver type: error/gradient-derived.**

### 3.3 Adaptive statistical process control (control charts)

EWMA control charts are a direct industrial-statistics cousin of your mechanism, explicitly used for monitoring and anomaly flagging: control charts, exemplified by the Shewhart chart and variants like the EWMA chart, continuously monitor processes, comparing current observations against historical statistical parameters and signaling anomalies when deviations exceed control limits. A large and very active sub-literature on **Adaptive EWMA (AEWMA)** charts exists — one representative formulation dynamically adjusts the smoothing constant based on a continuous function of the estimated mean shift derived from the EWMA statistic itself, and even machine-learning-based variants follow the same pattern, where a support vector regression model is trained to forecast the smoothing constant's value from the shift size, then used to compute the final EWMA statistic for charting. Across this entire literature, the adaptation target is always the **shift/misadjustment of the monitored quantity**, never an exogenous system signal.

**Driver type: estimated-shift/misadjustment-derived.**

### 3.4 Classical adaptive exponential smoothing (operations research lineage)

This is the oldest branch (1960s operations research forecasting), and it set the pattern every later technique inherited. **Trigg and Leach (1967)** proposed a modification to forecasting systems employing exponential smoothing whereby the response rate is varied and made to depend on the value of a tracking signal, reacting faster to step changes while still filtering random noise. A 2014 survey of the entire lineage that followed (Whybark 1973, Gardner 2006, and others) makes the pattern explicit: the value of the smoothing parameter in the existing adaptive methods depends on the magnitude of the most recent forecasting error.

**Driver type: forecast-error-derived — and explicitly, by the field's own survey literature, this has been the universal pattern for nearly 60 years.**

### 3.5 Adaptive Kalman filtering in finance

The Kalman filter generalizes the EMA with an optimal, time-varying gain; "adaptive" Kalman filtering for trend-following tunes that gain in real time. One representative approach adaptively tunes the filter's process noise covariance based on rolling realized volatility, allowing the filter to become more responsive in volatile periods and smoother in calm ones, motivated by the fact that a steady-state model treats a shift in process and measurement dynamics as a random effect, which produces suboptimal estimates if the change is permanent — adaptive models can adjust to financial time series' inherently time-varying dynamics. In the broader adaptive-Kalman engineering literature outside finance (target tracking, navigation), the same pattern holds: noise covariances are adapted from the cross-correlation between innovation and residual sequences, i.e., internal filter statistics.

**Driver type: volatility/innovation-derived.**

### 3.6 Time-varying-pole IIR filter theory (signal processing literature proper)

This is the only branch that treats a *moving pole* with formal DSP rigor — but in entirely different application domains. One line of work designs a time-varying pole-radius IIR notch filter using a hyperbolic tangent sigmoid function to vary the pole radius, analyzed for stability, for removing power-line interference from ECG signals, with follow-on work extending this to multi-notch filter designs analyzed for stability and tested for transient suppression and selectivity. Other foundational stability work addresses linear time-varying IIR filters with equalized group-delay characteristics, including the non-linear phase response problem that time-varying coefficients introduce. This confirms the *mathematical machinery* your project needs (pole-radius stability proofs, transient-response analysis) is well established — but it has never been applied to a load-driven pole or to financial anomaly detection.

**Driver type: none of these are exogenous-system-driven; they're tuned for a fixed engineering objective (notch sharpness vs. settling time), not adapted online from any external signal.**

### 3.7 Financial time-series anomaly and manipulation detection (the application side)

This is a large, active field, but dominated by two families that are largely orthogonal to your filter-theoretic approach:

- **Deep learning approaches** — e.g., a PCA-plus-neural-network method extracts key features from high-dimensional financial time series via dimensionality reduction, then applies neural networks to identify anomalies that could otherwise cause calibration errors in risk models; reinforcement-learning-based model-selection frameworks pick among base anomaly detectors per time step.
- **Wavelet/spectral approaches** — a generative-adversarial method using continuous wavelet transforms achieved strong results: training a discriminator as an anomaly detector for manipulative trading activities achieved an average AUC of 0.99 while maintaining low false alarm rates across market conditions, building on the fact that wavelet transform helps detect features that are easy to interpret and integrating continuous-wavelet-transform features into a CNN framework enhances adaptability to manipulation patterns at varying time scales. Wavelet modulus-maxima methods are also used specifically because they overcome the localized limitation of traditional Fourier analysis in time and frequency domains, capturing the singular points of unusual stock fluctuations quickly and accurately.

Neither family treats the *smoothing/detrending filter itself* as the object of study with a Z-domain stability and frequency-response analysis — they treat it as a black-box preprocessing step (if used at all) and focus model complexity on the detector. This is a meaningful gap for a DSP-focused (rather than ML-focused) mini-project to fill: a rigorous filter-theoretic treatment of the smoothing stage itself.

### 3.8 Stream-processing systems: backpressure-driven adaptive windowing (the closest conceptual relative)

This is the systems-literature side, and it's where the *idea* of load-driven adaptation already exists — just not as a formally analyzed DSP filter.

- **ASWB (2026)**, in distributed stream processing, proposes an adaptive sampling rate algorithm driven by backpressure signals that dynamically controls the stream sampling rate to avoid prediction bottlenecks and alleviate workload imbalance, paired with a variable-size window to reduce hash collisions and improve frequency estimation.
- **Spark Streaming's dynamic batch sizing** is based on a fixed-point iteration numerical technique that lets the system adapt window size when incoming data varies too much, minimizing end-to-end latency while keeping the system stable based on statistics from the last two completed batches.
- **GOVERNOR**, a more recent controller for stream processing, uses smarter backpressure handling than naive PID approaches, evaluated specifically on throughput stability under varying checkpointing overhead and parallelism.
- **Active Queue Management (RED/Adaptive RED)** in networking is the closest real-world structural analog: RED averages queue length using an exponentially weighted moving average and calculates drop probability via a linear mapping function, and Adaptive RED (ARED) was developed to automatically adjust RED's parameters using a target queue size, employing an additive-increase/multiplicative-decrease approach. Critically, however, the EWMA *weight itself* (`w_q`, i.e., the pole) is conventionally held fixed in RED/ARED — what's adapted is a *downstream* drop-probability parameter, not the smoothing filter's pole.

**Driver type: this branch is the only one using an exogenous, system-state signal (queue depth, backpressure) — but none of it is given a Z-domain pole/frequency-response treatment, and none of it targets anomaly detection in a financial signal.**

---

## 4. Synthesis Table

| Technique family | Adaptation driver | Exogenous to signal? | Z-domain/pole treatment? | Anomaly detection target? |
|---|---|---|---|---|
| KAMA / efficiency-ratio MAs | Price efficiency ratio | No | No | No (trend-following) |
| VSS-LMS | Mean-square error | No | Partial (convergence analysis) | No |
| VFF-RLS | MSE gradient / state-space error | No | Partial | No |
| AEWMA control charts | Estimated shift/misadjustment | No | No | Yes (process monitoring) |
| Trigg-Leach lineage | Forecast tracking signal | No | No | No (forecasting) |
| Adaptive Kalman (finance) | Realized volatility / innovation | No | No | No (trend-following) |
| Time-varying-pole IIR (ECG/notch) | Fixed design objective | No | **Yes** | No |
| Wavelet/DL anomaly detection | N/A (black-box features) | N/A | No | **Yes** |
| Adaptive RED / AQM | Queue length / backpressure | **Yes** | No | No (congestion control) |
| **Your project** | **Backpressure/load signal** | **Yes** | **Yes** | **Yes** |

No existing branch occupies the bottom-right cell.

---

## 5. The Research Gap, Stated Precisely

Across finance (KAMA, RiskMetrics, adaptive Kalman), statistics (AEWMA control charts), and classical adaptive filtering (VSS-LMS, VFF-RLS), the smoothing/adaptation parameter is always computed from a property of the monitored signal itself — its volatility, its forecast error, its efficiency, or its estimated shift. The one literature that adapts a smoothing parameter from a genuinely exogenous, system-state signal — Active Queue Management's use of backpressure/queue depth — does so for a different parameter (the drop-probability mapping, not the EWMA pole) and for a different purpose (congestion control, not anomaly detection), with no formal frequency-domain characterization. Meanwhile, the signal-processing literature that *does* analyze moving poles formally (time-varying-pole IIR notch filters) does so for fixed engineering trade-offs (transient suppression vs. selectivity), not online adaptation from any external signal.

**The gap:** a single-pole IIR filter whose pole is driven by a load/backpressure signal exogenous to the filtered data, characterized formally in the Z-domain (pole trajectory, instantaneous frequency response, group delay, stability bounds on how fast the pole is allowed to move), and evaluated for anomaly-detection performance against the dominant signal-derived alternatives (fixed RiskMetrics-style EWMA, KAMA, and a standard Butterworth/Chebyshev IIR design via bilinear transform) on real tick data.

---

## 6. How This Maps to a Standalone Mini-Project

This gives you a clean, self-contained scope that doesn't depend on KLStream's codebase or the IT4D paper:

1. **Derive** `H(z)` for the fixed-α EMA, establish the pole-at-`1-α` result, and show the cutoff-frequency/half-life relationship (ties to Sec. 5 of your syllabus).
2. **Define** a load/backpressure proxy from your tick data itself (e.g., inter-arrival rate, a synthetic "processing load" you simulate, or order-flow intensity from LOBSTER message rates) and drive α(t) from it.
3. **Analyze** the resulting time-varying-pole system: pole trajectory, frozen-time frequency response at several α values, and a stability/rate-of-change bound (how fast can the pole move before the frozen-pole approximation breaks down) — directly modeled on the stability methodology used in the ECG/notch-filter literature above (Sec. 3.6).
4. **Benchmark** against: (a) fixed RiskMetrics-style EWMA (λ=0.94), (b) KAMA (signal-driven adaptive EMA), (c) a Butterworth low-pass via bilinear transform (Sec. 7 of your syllabus) — on anomaly-detection precision/recall or detection latency.
5. **Conclude** with a clear positioning statement: this is a control-driven adaptation paradigm, distinct from the error/volatility-driven adaptation that dominates existing literature.

---

## 7. Suggested Datasets

- **LOBSTER** — academic limit-order-book data: an online tool providing easy-to-use, high-quality limit order book data, acting as a data provider for the academic community since 2013, with access to reconstructed limit order book data for the entire universe of NASDAQ-traded stocks. Free sample files are available for AAPL, AMZN, GOOG, INTC, MSFT at millisecond resolution — sufficient for a mini-project without needing a paid subscription.
- **Binance public REST/WebSocket API** — free, high-frequency crypto tick/trade data, useful if you want a bursty, 24/7 stream with more visible load variation than equities (which have clean open/close boundaries).

---

## 8. References

1. Kaufman's Adaptive Moving Average — TradingView / StockCharts ChartSchool — https://www.tradingview.com/support/solutions/43000773012-kaufman-s-adaptive-moving-average-kama/
2. A variable forgetting factor RLS adaptive filtering algorithm — IEEE / ResearchGate — https://ieeexplore.ieee.org/document/5355946/
3. Gradient based variable forgetting factor RLS algorithm — ScienceDirect — https://www.sciencedirect.com/science/article/abs/pii/S0165168403000379
4. A variable step size LMS algorithm (Kwong & Johnston) — IEEE Xplore — https://ieeexplore.ieee.org/abstract/document/143435/
5. A Survey of Deep Anomaly Detection in Multivariate Time Series — MDPI Sensors — https://www.mdpi.com/1424-8220/25/1/190
6. Adaptive EWMA control charts with time-varying smoothing parameter (Capizzi & Masarotto lineage) — Int'l J. Advanced Manufacturing Technology — https://link.springer.com/article/10.1007/s00170-017-0792-1
7. Machine learning based parameter-free adaptive EWMA control chart — PMC — https://pmc.ncbi.nlm.nih.gov/articles/PMC11682192/
8. Time series anomaly detection via temporal relationship graphs and adaptive smoothing — ScienceDirect — https://www.sciencedirect.com/science/article/pii/S156849462500609X
9. Exponential Smoothing with an Adaptive Response Rate (Trigg & Leach, 1967) — J. Operational Research Society — https://link.springer.com/article/10.1057/jors.1967.5
10. A new adaptive exponential smoothing method for non-stationary time series with level shifts — J. Industrial Engineering International — https://link.springer.com/article/10.1007/s40092-014-0075-5
11. Navigating Market Regimes: An Adaptive Kalman Filter Tuned by Realized Volatility — Medium/PyQuantLab — https://pyquantlab.medium.com/navigating-market-regimes-an-adaptive-kalman-filter-tuned-by-realized-volatility-99bb4f8c1d7f
12. Trend-Following Filters Parts 4–5 — alphaarchitect.com — https://alphaarchitect.com/2022/01/trend-following-filters-part-4 / https://alphaarchitect.com/trend-following-filters-part-5/
13. A pole-radius-varying IIR notch filter with enhanced post-transient performance — ScienceDirect — https://www.sciencedirect.com/science/article/abs/pii/S1746809416302270
14. Time-Varying Pole-Radius IIR Multi-Notch Filters with Improved Performance — Arabian J. Science and Engineering / Springer — https://link.springer.com/article/10.1007/s13369-019-03814-w
15. Stability analysis of linear time-varying IIR filter with equalized group delay characteristic — IEEE Xplore — https://ieeexplore.ieee.org/document/6669879
16. WALDATA: Wavelet transform based adversarial learning for detection of anomalous trading activities — ScienceDirect — https://www.sciencedirect.com/science/article/abs/pii/S0957417424015963
17. Stock Fluctuations Anomaly Detection Based on Wavelet Modulus Maxima — IEEE Xplore — https://ieeexplore.ieee.org/document/5208866
18. Adaptive sampling-driven workload balancing for distributed data stream processing (ASWB) — ETRI Journal / Wiley — https://onlinelibrary.wiley.com/doi/10.4218/etrij.2025-0175
19. Spark Streaming Backpressure for Data-Intensive Pipelines — Encyclopedia MDPI — https://encyclopedia.pub/entry/25073
20. GOVERNOR: Smoother Stream Processing Through Smarter Backpressure — UC Santa Cruz / ICAC — https://people.ucsc.edu/~lhu82/Biobibnet/17ICAC_Governor.pdf
21. Adaptive RED: An Algorithm for Increasing the Robustness of RED's Active Queue Management (Floyd, Gummadi, Shenker) — https://www.academia.edu/33251203/
22. Active queue management algorithm considering queue and load states — ScienceDirect — https://www.sciencedirect.com/science/article/abs/pii/S0140366406004026
23. Active Queue Management — overview — ScienceDirect Topics — https://www.sciencedirect.com/topics/computer-science/active-queue-management
24. RiskMetrics 2006 Methodology (Zumbach) — MSCI — https://www.msci.com/resources/research/technical_documentation/RM2006.pdf
25. EWMA & GARCH Volatility Calculator — Ryan O'Connell, CFA — https://ryanoconnellfinance.com/calculators/ewma-volatility-calculator/
26. LOBSTER — academic limit order book data — https://data.lobsterdata.com/info/WhatIsLOBSTER.php

---

*Compiled for COMP 407 (Digital Signal Processing) mini-project scoping, June 2026.*
