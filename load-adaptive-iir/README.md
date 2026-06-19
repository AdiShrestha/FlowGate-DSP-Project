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
3. Run the complete pipeline end-to-end:
   ```bash
   # Make sure you are in the project root directory
   python -m src.run_all
   ```

### Results Summary
Running the pipeline produces 11 key figures in `results/figures/` and a benchmark table in `results/tables/comparison.csv`.

| Filter | Precision | Recall | F1 | Mean Latency | FP Rate (per 1k) | ROC AUC | PR AUC |
|---|---|---|---|---|---|---|---|
| Fixed EMA (0.06) | 0.1730 | 0.0718 | 0.1014 | 1.4000 | 12.1774 | 0.1133 | 0.0540 |
| Load Adaptive EMA | 0.2265 | 0.0519 | 0.0845 | 0.5333 | 6.2958 | 0.0701 | 0.0409 |
| KAMA | 0.4701 | 0.0688 | 0.1201 | 1.3333 | 2.7544 | 0.0995 | 0.0753 |
| Butterworth | 0.0762 | 0.0881 | 0.0817 | 3.7333 | 37.8992 | 0.1772 | 0.0388 |

### Limitations & Methodological Choices
- **Evaluation Methodology**: The model uses point-wise precision, recall, and F1 scoring with a tolerance buffer ($\pm 20$ samples) around each true anomaly to account for natural filter lag. We explicitly **do not** use full point-adjustment (where any detection inside the window counts all points in the window as detected). The literature has shown point-adjustment artificially inflates performance scores, so we use strict buffering as a defensible methodological choice.
- **Simulated Backpressure**: Since this is a standalone DSP project, backpressure is simulated using a discrete-event queue model rather than extracted from a real stream-processing runtime.
- **Dataset Scope**: Tested primarily on a short window of Binance BTCUSDT tick data.
