import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from src.anomaly_injection import inject_anomalies
from src.detection import detect_anomalies
from src.evaluate import evaluate_predictions, compute_auc
from src.filters import fixed_ema, load_adaptive_ema, kama, butterworth_lowpass
from src.rrcf_detector import run_rrcf_streaming
from src.queue_simulator import simulate_backpressure

def process_single_run(idx, row, seed, regime, n_anomalies_per_type, fs_assumed, f_c_matched):
    symbol = row['symbol']
    date_str = row['date']
    
    # Load the data for this specific day
    from src.data_acquisition import load_tick_series
    try:
        df = load_tick_series('binance', symbol, (date_str, date_str))
        # Take up to 50k samples to keep it tractable
        df = df.iloc[:50000].reset_index(drop=True)
    except Exception as e:
        print(f"Failed to load {symbol} {date_str}, skipping. ({e})")
        return None
        
    x_clean = df['price'].values
    
    # Compute backpressure
    bursts = [(int(len(x_clean)*0.2), int(len(x_clean)*0.3)), (int(len(x_clean)*0.6), int(len(x_clean)*0.7))]
    L = simulate_backpressure(df['timestamp'], burst_multiplier=2.0, burst_intervals=bursts).values
    
    # 1. Inject anomalies
    x_injected, mask, anomaly_info = inject_anomalies(
        pd.Series(x_clean), 
        n_each=n_anomalies_per_type, 
        seed=seed
    )
    
    # 2. Run filters
    y_fixed, _ = fixed_ema(x_injected, alpha=0.06)
    y_adaptive, _ = load_adaptive_ema(x_injected, L)
    y_adaptive_bw, _ = load_adaptive_ema(x_injected, L, alpha_min=0.02, alpha_max=0.08253)
    y_kama, _ = kama(x_injected)
    y_butter, _ = butterworth_lowpass(x_injected)
    y_butter_matched, _ = butterworth_lowpass(x_injected, cutoff_hz=f_c_matched, fs=fs_assumed)
    
    # Run RRCF
    rrcf_codisp = run_rrcf_streaming(x_injected, num_trees=20, tree_size=128)
    
    filters_out = {
        'Fixed EMA': y_fixed,
        'Load Adaptive EMA': y_adaptive,
        'Load-Adaptive EMA (BW-Matched)': y_adaptive_bw,
        'KAMA': y_kama,
        'Butterworth (Default)': y_butter,
        'Butterworth (Matched)': y_butter_matched
    }
    
    z_scores = {}
    for name, y in filters_out.items():
        _, z, _ = detect_anomalies(x_injected, y)
        z_scores[name] = z
        
    z_scores['RRCF'] = rrcf_codisp
    
    # Aggregate for DeLong
    y_true_binary = np.zeros_like(mask)
    buffer = 20
    for info in anomaly_info:
        start = max(0, info['start'] - buffer)
        end = min(len(y_true_binary), info['end'] + buffer + 1)
        y_true_binary[start:end] = True
    
    run_results = []
    
    # Evaluate ROC-AUC globally
    for name, z in z_scores.items():
        roc_auc, _, _, _, _, _ = compute_auc(z, anomaly_info, mask)
        run_results.append({
            'regime': regime,
            'symbol': symbol,
            'date': date_str,
            'seed': seed,
            'config': name,
            'anomaly_type': 'all',
            'roc_auc': roc_auc
        })
        
    # Evaluate per anomaly type
    anomaly_types = sorted({info['type'] for info in anomaly_info})
    for atype in anomaly_types:
        type_info = [a for a in anomaly_info if a['type'] == atype]
        type_mask = np.zeros_like(mask)
        for info in type_info:
            type_mask[info['start']:info['end'] + 1] = True
            
        for name, z in z_scores.items():
            roc_auc, _, _, _, _, _ = compute_auc(z, type_info, type_mask)
            run_results.append({
                'regime': regime,
                'symbol': symbol,
                'date': date_str,
                'seed': seed,
                'config': name,
                'anomaly_type': atype,
                'roc_auc': roc_auc
            })
            
    return run_results, y_true_binary, z_scores

def run_multi_seed_evaluation(
    n_seeds: int = 5,
    n_anomalies_per_type: int = 100
) -> pd.DataFrame:
    """
    Runs multi-seed anomaly injection evaluating across different market regimes.
    Picks N=50 random (asset, date) pairs per regime.
    """
    print(f"Running multi-seed evaluation with {n_seeds} runs per regime...")
    
    # Load regimes
    regimes_df = pd.read_csv("results/tables/regime_classification.csv")
    unique_regimes = regimes_df['regime'].unique()
    
    fs_assumed = 100.0
    f_c_matched = 0.06 * fs_assumed / (2 * np.pi)
    
    results = []
    
    # For aggregating scores for DeLong test
    global_mask_list = []
    global_z_scores_dict = {}
    
    for regime in unique_regimes:
        regime_pool = regimes_df[regimes_df['regime'] == regime]
        
        sampled_days = regime_pool.sample(n=n_seeds, replace=True, random_state=42).reset_index(drop=True)
        
        # Run sequentially to avoid Numba/Joblib deadlocks
        for idx, row in tqdm(sampled_days.iterrows(), total=n_seeds, desc=f"Regime: {regime}"):
            out = process_single_run(idx, row, idx, regime, n_anomalies_per_type, fs_assumed, f_c_matched)
            if out is not None:
                run_res, y_true_bin, z_scs = out
                results.extend(run_res)
                global_mask_list.append(y_true_bin)
                for name, z in z_scs.items():
                    if name not in global_z_scores_dict:
                        global_z_scores_dict[name] = []
                    global_z_scores_dict[name].append(z)

    df_results = pd.DataFrame(results)
    
    Path("results/tables").mkdir(parents=True, exist_ok=True)
    df_results.to_csv("results/tables/multi_seed_roc_auc.csv", index=False)
    
    # Compute summary
    summary_list = []
    # By config and anomaly type (ignoring regime for the global summary)
    for (config, atype), group in df_results.groupby(['config', 'anomaly_type']):
        mean_auc = group['roc_auc'].mean()
        std_auc = group['roc_auc'].std()
        ci_95 = 1.96 * std_auc / np.sqrt(len(group))
        summary_list.append({
            'config': config,
            'anomaly_type': atype,
            'mean_roc_auc': mean_auc,
            'std_roc_auc': std_auc,
            'ci_95': ci_95
        })
        
    df_summary = pd.DataFrame(summary_list)
    df_summary.to_csv("results/tables/multi_seed_summary.csv", index=False)
    
    # Run DeLong test
    print("Running DeLong statistical tests on aggregated results...")
    y_true_agg = np.concatenate(global_mask_list)
    z_scores_agg = {k: np.abs(np.concatenate(v)) for k, v in global_z_scores_dict.items()}
    from src.statistical_tests import batch_delong_comparisons
    batch_delong_comparisons(y_true_agg, z_scores_agg)
    
    return df_results, df_summary

if __name__ == "__main__":
    run_multi_seed_evaluation(n_seeds=50, n_anomalies_per_type=100)
