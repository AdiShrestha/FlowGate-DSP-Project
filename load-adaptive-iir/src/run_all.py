import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

from src.data_acquisition import load_tick_series
from src.queue_simulator import simulate_backpressure
from src.filters import fixed_ema, load_adaptive_ema, kama, butterworth_lowpass
from src.demo_signals import (
    generate_synthetic_signal, plot_impulse_and_step_responses,
    plot_synthetic_filtering, plot_real_data_psd, plot_time_varying_frequency_response
)
from src.zdomain_analysis import (
    analyze_frozen_zdomain, plot_pole_zero_sweep, plot_frequency_response_sweep,
    plot_pole_trajectory_vs_load
)
from src.anomaly_injection import inject_anomalies
from src.detection import detect_anomalies
from src.evaluate import evaluate_predictions, compute_auc, format_results_table
from src.visualize import plot_time_domain_comparison, plot_roc_pr_curves, plot_metrics_bar_comparison

def main():
    print("--- 1. Canonical Signals and Z-Domain Demonstrations ---")
    
    # 6A.1 & 6A.2 Synthetic Signals & Responses
    print("Generating impulse and step responses...")
    plot_impulse_and_step_responses()
    
    t_syn, x_syn = generate_synthetic_signal()
    
    # 6A.3 Filter synthetic signals
    print("Filtering synthetic signals...")
    plot_synthetic_filtering(t_syn, x_syn, fixed_ema, "Fixed EMA", alpha=0.3)
    L_syn = np.linspace(0, 1, len(x_syn))
    plot_synthetic_filtering(t_syn, x_syn, load_adaptive_ema, "Load Adaptive EMA", L=L_syn)
    plot_synthetic_filtering(t_syn, x_syn, kama, "KAMA")
    plot_synthetic_filtering(t_syn, x_syn, butterworth_lowpass, "Butterworth")
    
    # 6 Z-Domain Analysis
    print("Running Z-Domain analysis sweep...")
    z_results = analyze_frozen_zdomain()
    plot_pole_zero_sweep(z_results)
    plot_frequency_response_sweep(z_results)
    
    print("\n--- 2. Real Data Pipeline ---")
    
    # Data Acquisition
    print("Loading tick series (Binance BTCUSDT 2024-01-01)...")
    try:
        df = load_tick_series('binance', 'BTCUSDT', ('2024-01-01', '2024-01-01'))
    except Exception as e:
        print(f"Data loading failed: {e}. Are you offline? Generating dummy data for demonstration.")
        t_dummy = np.arange(50000) * 0.1
        p_dummy = 40000.0 + np.cumsum(np.random.normal(0, 5, 50000))
        df = pd.DataFrame({'timestamp': t_dummy, 'price': p_dummy})
    
    # Take first 50k samples for speed
    df = df.iloc[:50000].reset_index(drop=True)
    
    print("Simulating backpressure...")
    bursts = [(10000, 15000), (30000, 35000)]
    L = simulate_backpressure(df['timestamp'], burst_multiplier=2.0, burst_intervals=bursts)
    
    Path("results/figures").mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['timestamp'], L, color='red')
    ax.set_title("Simulated Backpressure L[n]")
    ax.set_xlabel("Timestamp")
    fig.savefig("results/figures/queue_simulation.png", dpi=150)
    plt.close(fig)
    
    print("Injecting synthetic anomalies...")
    x_injected, mask, anomaly_info = inject_anomalies(df['price'])
    
    n_samples = len(x_injected)
    valid_windows = np.zeros(n_samples, dtype=bool)
    buffer = 20
    for info in anomaly_info:
        start = max(0, info['start'] - buffer)
        end = min(n_samples, info['end'] + buffer + 1)
        valid_windows[start:end] = True
        
    import scipy.stats
    corr, p = scipy.stats.pearsonr(L.values, valid_windows.astype(float))
    print(f"Pearson correlation between L[n] and near-anomaly indicator: {corr:.4f} (p={p:.4e})")
    
    fig_corr, ax_corr = plt.subplots(figsize=(10, 4))
    ax_corr.plot(df['timestamp'], L.values, label='Load L[n]', color='red', alpha=0.7)
    ax_corr.fill_between(df['timestamp'], 0, 1, where=valid_windows, color='grey', alpha=0.3, label='Anomaly Window')
    ax_corr.set_title(f"Load vs Anomaly Injection (Pearson r = {corr:.4f})")
    ax_corr.legend()
    fig_corr.savefig("results/figures/load_vs_anomaly_correlation.png", dpi=150)
    plt.close(fig_corr)
    
    print("Running filters...")
    y_fixed, pole_fixed = fixed_ema(x_injected, alpha=0.06) 
    y_adaptive, pole_adaptive = load_adaptive_ema(x_injected, L.values)
    y_kama, pole_kama = kama(x_injected)
    y_butter, pole_butter = butterworth_lowpass(x_injected)
    
    fs_assumed = 100.0
    f_c_matched = 0.06 * fs_assumed / (2 * np.pi)
    y_butter_matched, pole_butter_matched = butterworth_lowpass(x_injected, cutoff_hz=f_c_matched, fs=fs_assumed)
    
    filters_out = {
        'Fixed EMA (0.06)': y_fixed,
        'Load Adaptive EMA': y_adaptive,
        'KAMA': y_kama,
        'Butterworth (Default)': y_butter,
        'Butterworth (Matched)': y_butter_matched
    }
    
    print("Running detection robustness check on Fixed EMA...")
    import time
    t0 = time.time()
    _, _, det_std_100 = detect_anomalies(x_injected, y_fixed, window=100, estimator='std')
    _, _, det_std_300 = detect_anomalies(x_injected, y_fixed, window=300, estimator='std')
    print(f"FP rate (STD, w=100): {(np.sum(det_std_100 & ~valid_windows) / np.sum(~valid_windows)) * 1000:.2f} per 1k")
    print(f"FP rate (STD, w=300): {(np.sum(det_std_300 & ~valid_windows) / np.sum(~valid_windows)) * 1000:.2f} per 1k")
    _, _, det_mad_100 = detect_anomalies(x_injected, y_fixed, window=100, estimator='mad')
    print(f"FP rate (MAD, w=100): {(np.sum(det_mad_100 & ~valid_windows) / np.sum(~valid_windows)) * 1000:.2f} per 1k")
    print(f"Robustness check took {time.time() - t0:.1f}s")
    
    print("Generating real data PSD...")
    plot_real_data_psd(x_injected, fs=1.0, y_dict=filters_out)
    
    print("Generating time-varying filter visualizations...")
    plot_pole_trajectory_vs_load(L.values, pole_adaptive, df['timestamp'].values)
    alpha_trace = 1 - pole_adaptive
    plot_time_varying_frequency_response(alpha_trace, L.values, fs=1.0)
    
    print("Running detection logic...")
    detections = {}
    z_scores = {}
    for name, y in filters_out.items():
        _, z, det = detect_anomalies(x_injected, y)
        detections[name] = det
        z_scores[name] = z
        
    print("Evaluating models...")
    results_dict = {}
    auc_data = {}
    
    for name, z in z_scores.items():
        prec, rec, f1, lat, fpr = evaluate_predictions(mask, detections[name], anomaly_info)
        roc_auc, pr_auc, fprs, tprs, precs, ths = compute_auc(z, anomaly_info, mask)
        
        results_dict[name] = {
            'Precision': prec,
            'Recall': rec,
            'F1': f1,
            'Mean Latency': lat,
            'FP Rate (per 1k)': fpr,
            'ROC AUC': roc_auc,
            'PR AUC': pr_auc,
            'PR Baseline': np.sum(mask) / len(mask)
        }
        auc_data[name] = (roc_auc, pr_auc, fprs, tprs, precs, ths)
        
    print("Saving results table...")
    results_df = format_results_table(results_dict)
    
    # Auto-update README
    readme_path = Path("README.md")
    if readme_path.exists():
        content = readme_path.read_text()
        marker = "*(Results will be populated here after running the pipeline)*"
        if marker in content:
            headers = ["Filter"] + list(results_df.columns)
            header_str = "| " + " | ".join(headers) + " |"
            sep_str = "|" + "|".join(["---" for _ in headers]) + "|"
            rows = []
            for idx, row in results_df.iterrows():
                row_str = f"| {idx} | " + " | ".join([f"{x:.4f}" for x in row]) + " |"
                rows.append(row_str)
            md_table = "\n".join([header_str, sep_str] + rows)
            
            content = content.replace(marker, md_table)
            readme_path.write_text(content)
            print("README.md updated with results table.")
    
    print("Generating application results figures...")
    plot_time_domain_comparison(df['timestamp'], x_injected, filters_out, anomaly_info, detections)
    plot_roc_pr_curves(auc_data)
    plot_metrics_bar_comparison(results_df)
    
    print("\n--- Pipeline Completed Successfully ---")
    print(results_df)

if __name__ == "__main__":
    main()
