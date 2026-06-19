import pandas as pd
import numpy as np
from src.queue_simulator import simulate_backpressure
from src.anomaly_injection import inject_anomalies
from src.detection import detect_anomalies
from src.evaluate import compute_auc

def main():
    print("--- 1. Queue Simulator Debug ---")
    df = pd.read_parquet("data/processed/binance_BTCUSDT_20240101_20240101.parquet")
    df = df.iloc[:50000].reset_index(drop=True)
    t = df['timestamp']
    print(f"Raw dtype: {t.dtype}")
    print(f"First 5: {t.head().values}")
    print(f"Last 5: {t.tail().values}")
    
    # To determine if t is ms, s, or ns:
    t_seconds = t / 1000.0
    duration_s = t_seconds.iloc[-1] - t_seconds.iloc[0]
    count = len(t)
    
    diffs = t.diff().dropna()
    old_lambda = 1.0 / diffs.mean() if diffs.mean() > 0 else 0
    new_lambda = count / duration_s if duration_s > 0 else 0
    
    print(f"Computed total duration (raw diff): {t.iloc[-1] - t.iloc[0]}")
    print(f"Computed total duration in assumed seconds (t/1000): {duration_s}")
    print(f"Raw event count: {count}")
    print(f"Old λ (1/mean(diff)): {old_lambda}")
    print(f"New λ (count/duration_s): {new_lambda}")
    
    print("\n--- 2. Anomaly Injection Debug ---")
    x_injected, mask, anomaly_info = inject_anomalies(df['price'])
    for info in anomaly_info:
        print(f"Anomaly {info['type']} injected at index {info['start']} to {info['end']}")
        
    print("\n--- 3 & 4. Detection / Evaluate Debug ---")
    from src.filters import fixed_ema
    y, _ = fixed_ema(x_injected, alpha=0.06)
    residual, z, detected = detect_anomalies(x_injected, y)
    
    print(f"len(mask): {len(mask)}")
    print(f"len(z_scores): {len(z)}")
    
    first_idx = anomaly_info[0]['start']
    slice_start = max(0, first_idx - 5)
    slice_end = min(len(z), first_idx + 5)
    print(f"Slice around index {first_idx}:")
    for i in range(slice_start, slice_end):
        print(f"idx: {i}, mask: {mask[i]}, raw_score (z): {z[i]}, abs(z): {np.abs(z[i])}")
        
    roc_auc, pr_auc, fprs, tprs, precs, ths = compute_auc(z, anomaly_info)
    print(f"\nROC AUC computed with abs(z_scores)? Yes, src/evaluate.py line 53 uses np.abs(z_scores) > th")
    
if __name__ == "__main__":
    main()
