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

*(Results will be populated here after running the pipeline)*

### Limitations
- **Simulated Backpressure**: Since this is a standalone DSP project, backpressure is simulated using a discrete-event queue model rather than extracted from a real stream-processing runtime.
- **Evaluation Methodology**: The tolerance-window evaluation metric simplifies real-world continuous monitoring. Point-adjustment was explicitly avoided as it can artificially inflate scores.
- **Dataset Scope**: Tested primarily on a short window of Binance BTCUSDT tick data.
