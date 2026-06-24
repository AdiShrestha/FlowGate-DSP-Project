import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import scipy.stats

from src.filters import load_adaptive_ema
from src.detection import detect_anomalies
from src.data_acquisition import load_tick_series
from src.queue_simulator import simulate_backpressure
from src.anomaly_injection import inject_anomalies
from src.evaluate import compute_auc

def demonstrate_fp_paradox():
    print("Running FP-rate paradox demonstration...")
    # Load default data
    try:
        df = load_tick_series('binance', 'BTCUSDT', ('2024-01-01', '2024-01-01'))
    except:
        df = pd.DataFrame({'timestamp': np.arange(50000)*0.1, 'price': 40000 + np.cumsum(np.random.normal(0, 5, 50000))})
    
    df = df.iloc[:50000].reset_index(drop=True)
    bursts = [(10000, 15000), (30000, 35000)]
    L = simulate_backpressure(df['timestamp'], burst_multiplier=2.0, burst_intervals=bursts).values
    x_injected, mask, anomaly_info = inject_anomalies(df['price'], seed=42)
    
    valid_windows = np.zeros(len(x_injected), dtype=bool)
    buffer = 20
    for info in anomaly_info:
        start = max(0, info['start'] - buffer)
        end = min(len(x_injected), info['end'] + buffer + 1)
        valid_windows[start:end] = True

    # 4.1 Compute |dα/dt| trace
    y_adaptive_bw, pole_adaptive_bw = load_adaptive_ema(
        x_injected, L, alpha_min=0.02, alpha_max=0.08253
    )
    alpha_trace = 1.0 - pole_adaptive_bw
    dalpha_dt = np.abs(np.diff(alpha_trace))
    dalpha_dt = np.concatenate([[0], dalpha_dt])
    
    # 4.2 Correlate with false positive locations
    _, z, det = detect_anomalies(x_injected, y_adaptive_bw)
    fp_mask = det & ~valid_windows
    
    # Pearson
    r, p_val = scipy.stats.pearsonr(dalpha_dt, fp_mask.astype(float))
    
    # Density comparison
    bins = 100
    n_samples = len(x_injected)
    samples_per_bin = n_samples // bins
    
    bin_dalpha = []
    bin_fp = []
    
    for i in range(bins):
        start = i * samples_per_bin
        end = start + samples_per_bin
        bin_dalpha.append(np.mean(dalpha_dt[start:end]))
        bin_fp.append(np.sum(fp_mask[start:end]))
        
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(bin_dalpha, bin_fp, alpha=0.6)
    
    m, b = np.polyfit(bin_dalpha, bin_fp, 1)
    ax.plot(np.array(bin_dalpha), m*np.array(bin_dalpha) + b, color='red', linestyle='--')
    
    ax.set_xlabel('Mean |dα/dt| per bin')
    ax.set_ylabel('False Positive Count per bin')
    ax.set_title(f'FP Paradox Demonstration (Pearson r = {r:.3f}, p = {p_val:.2e})')
    
    Path("results/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig("results/figures/fp_paradox_demonstration.png", dpi=150)
    plt.close(fig)
    
    # Threshold test
    threshold = np.percentile(dalpha_dt, 75)
    high_mask = dalpha_dt > threshold
    low_mask = dalpha_dt <= threshold
    
    # calculate outside valid windows only
    valid_high = high_mask & ~valid_windows
    valid_low = low_mask & ~valid_windows
    
    fp_rate_high = (np.sum(fp_mask[valid_high]) / np.sum(valid_high)) * 1000 if np.sum(valid_high) > 0 else 0
    fp_rate_low = (np.sum(fp_mask[valid_low]) / np.sum(valid_low)) * 1000 if np.sum(valid_low) > 0 else 0
    
    pd.DataFrame([{
        'pearson_r': r,
        'pearson_p': p_val,
        'threshold_75th': threshold,
        'fp_rate_high_adaptation': fp_rate_high,
        'fp_rate_low_adaptation': fp_rate_low
    }]).to_csv("results/tables/fp_paradox_analysis.csv", index=False)
    
    # 4.3 Slew-rate sensitivity experiment
    # For load_adaptive_ema, we don't have a built-in max slew-rate limit argument yet.
    # We will simulate it by smoothing L or modifying alpha directly. 
    # Actually, load_adaptive_ema formula is alpha[n] = alpha_max - ...
    # We can just write a quick loop here to apply slew-rate limiting to alpha_trace and rerun detection
    slew_rates = [0.001, 0.01, 0.05]
    sens_results = []
    
    alpha_raw = 0.08253 - (0.08253 - 0.02) * L
    
    for max_slew in slew_rates:
        alpha_limited = np.zeros_like(alpha_raw)
        alpha_limited[0] = alpha_raw[0]
        for i in range(1, len(alpha_raw)):
            diff = alpha_raw[i] - alpha_limited[i-1]
            diff = np.clip(diff, -max_slew, max_slew)
            alpha_limited[i] = alpha_limited[i-1] + diff
            
        # Re-run filter with this alpha_limited
        y_lim = np.zeros_like(x_injected)
        y_lim[0] = x_injected[0]
        for i in range(1, len(x_injected)):
            y_lim[i] = alpha_limited[i] * x_injected[i] + (1 - alpha_limited[i]) * y_lim[i-1]
            
        _, z_lim, det_lim = detect_anomalies(x_injected, y_lim)
        fp_mask_lim = det_lim & ~valid_windows
        n_outside = len(x_injected) - np.sum(valid_windows)
        fp_rate = (np.sum(fp_mask_lim) / n_outside) * 1000
        
        roc_auc, _, _, _, _, _ = compute_auc(z_lim, anomaly_info, mask)
        mean_dalpha = np.mean(np.abs(np.diff(alpha_limited)))
        
        sens_results.append({
            'max_slew_rate': max_slew,
            'fp_rate_per_1k': fp_rate,
            'roc_auc': roc_auc,
            'mean_dalpha_dt': mean_dalpha
        })
        
    df_sens = pd.DataFrame(sens_results)
    df_sens.to_csv("results/tables/slew_rate_sensitivity.csv", index=False)
    
    fig, ax1 = plt.subplots(figsize=(8,5))
    ax2 = ax1.twinx()
    
    ax1.plot(df_sens['max_slew_rate'], df_sens['fp_rate_per_1k'], 'bo-', label='FP Rate')
    ax2.plot(df_sens['max_slew_rate'], df_sens['roc_auc'], 'rs-', label='ROC AUC')
    
    ax1.set_xlabel('Max Slew Rate Limit (Δα_max)')
    ax1.set_ylabel('False Positive Rate (per 1k)', color='b')
    ax2.set_ylabel('ROC AUC', color='r')
    
    ax1.set_xscale('log')
    plt.title('Slew-Rate Sensitivity Experiment')
    fig.tight_layout()
    fig.savefig("results/figures/slew_rate_sensitivity.png", dpi=150)
    plt.close(fig)

if __name__ == "__main__":
    demonstrate_fp_paradox()
