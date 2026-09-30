import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from src.delong import delong_roc_test, delong_roc_variance

def run_delong_comparison(y_true, scores_A, scores_B, name_A, name_B):
    """
    Run DeLong's test comparing two correlated ROC curves.
    Returns: dict with auc_A, auc_B, delta_auc, z_stat, p_value, significant (bool)
    """
    # compute AUCs and their variances
    auc_A, var_A = delong_roc_variance(y_true, scores_A)
    auc_B, var_B = delong_roc_variance(y_true, scores_B)
    
    auc_A = auc_A[0] if isinstance(auc_A, np.ndarray) else auc_A
    auc_B = auc_B[0] if isinstance(auc_B, np.ndarray) else auc_B
    var_A = var_A[0,0] if isinstance(var_A, np.ndarray) else var_A
    var_B = var_B[0,0] if isinstance(var_B, np.ndarray) else var_B
    
    delta_auc = auc_A - auc_B
    
    # run test to get log10 p-value
    z_stat_array, log10_p_array = delong_roc_test(y_true, scores_A, scores_B)
    log10_p = log10_p_array[0,0] if isinstance(log10_p_array, np.ndarray) else log10_p_array
    z_stat = z_stat_array[0,0] if isinstance(z_stat_array, np.ndarray) else z_stat_array
    
    p_value = 10 ** log10_p

    return {
        'name_A': name_A,
        'name_B': name_B,
        'auc_A': float(auc_A),
        'auc_B': float(auc_B),
        'delta_auc': float(delta_auc),
        'z_stat': float(z_stat),
        'p_value': float(p_value),
        'significant_05': p_value < 0.05,
        'significant_01': p_value < 0.01
    }

def batch_delong_comparisons(y_true, scores_dict):
    """
    Run the 3 key DeLong comparisons:
    1. Load-Adaptive EMA (BW-Matched) vs. Fixed EMA
    2. Load-Adaptive EMA + Shedding vs. Fixed EMA + Shedding
    3. Load-Adaptive EMA + Shedding vs. Butterworth
    """
    comparisons = [
        ("Load-Adaptive EMA (BW-Matched)", "Fixed EMA"),
        ("Load-Adaptive EMA + Shedding", "Fixed EMA + Shedding"),
        ("RRCF", "Load-Adaptive EMA (BW-Matched)")
    ]
    
    results = []
    for name_A, name_B in comparisons:
        # Check if they exist (handling slight naming differences)
        key_A = next((k for k in scores_dict if name_A in k), None)
        key_B = next((k for k in scores_dict if name_B in k), None)
        
        if key_A and key_B:
            res = run_delong_comparison(y_true, scores_dict[key_A], scores_dict[key_B], name_A, name_B)
            results.append(res)
        else:
            print(f"Warning: Could not find scores for comparison {name_A} vs {name_B}")
            
    df = pd.DataFrame(results)
    Path("results/tables").mkdir(parents=True, exist_ok=True)
    out_path = Path("results/tables/delong_test_results.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved DeLong test results to {out_path}")
    return df


# ---------------------------------------------------------------------------
# Paired t-test (primary statistical method for the multi-seed evaluation)
# ---------------------------------------------------------------------------

def run_paired_ttest(
    aucs_A: np.ndarray,
    aucs_B: np.ndarray,
    name_A: str,
    name_B: str,
) -> dict:
    """
    Paired two-sided t-test on per-seed ROC-AUC arrays.

    Both arrays must have the same length (one value per seed, same seed order).
    Uses scipy.stats.ttest_rel — the correct test for paired observations that
    share randomness (same seed → same anomaly locations → correlated AUCs).

    This is the primary statistical test used to generate the paper's headline
    results (e.g., ΔAUC = 0.0002, p = 0.67 for Load-Adaptive BW-Matched vs Fixed EMA).
    """
    aucs_A = np.asarray(aucs_A, dtype=float)
    aucs_B = np.asarray(aucs_B, dtype=float)
    assert len(aucs_A) == len(aucs_B), "AUC arrays must be the same length (one per seed)"

    t_stat, p_value = stats.ttest_rel(aucs_A, aucs_B)
    delta = float(np.mean(aucs_A) - np.mean(aucs_B))
    n = len(aucs_A)
    # 95% confidence interval on the mean difference
    se = float(np.std(aucs_A - aucs_B, ddof=1) / np.sqrt(n))
    ci_95 = 1.96 * se

    return {
        'name_A':        name_A,
        'name_B':        name_B,
        'mean_auc_A':    float(np.mean(aucs_A)),
        'mean_auc_B':    float(np.mean(aucs_B)),
        'delta_auc':     delta,
        'ci_95':         ci_95,
        't_stat':        float(t_stat),
        'p_value':       float(p_value),
        'significant_05': bool(p_value < 0.05),
        'significant_01': bool(p_value < 0.01),
        'n_seeds':       n,
    }


def batch_paired_ttests(
    csv_path: str = "results/tables/multi_seed_roc_auc.csv",
    reference: str = "Fixed EMA",
    anomaly_type: str = "all",
) -> pd.DataFrame:
    """
    Loads the per-seed multi-seed CSV and runs paired t-tests for every config
    vs. the reference config, restricted to the given anomaly_type row.

    Saves results to results/tables/paired_ttest_results.csv.
    """
    df = pd.read_csv(csv_path)
    df_type = df[df['anomaly_type'] == anomaly_type].copy()

    configs = [c for c in df_type['config'].unique() if c != reference]
    ref_series = df_type[df_type['config'] == reference].sort_values('seed')['roc_auc'].values

    results = []
    for cfg in configs:
        cfg_series = df_type[df_type['config'] == cfg].sort_values('seed')['roc_auc'].values
        # Guard: skip if seed counts don't match (data integrity issue)
        min_len = min(len(ref_series), len(cfg_series))
        if min_len < 2:
            print(f"  Warning: not enough seeds for {cfg} vs {reference}, skipping.")
            continue
        result = run_paired_ttest(cfg_series[:min_len], ref_series[:min_len], cfg, reference)
        results.append(result)

    df_out = pd.DataFrame(results)
    out_path = Path("results/tables/paired_ttest_results.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_path, index=False)
    print(f"Saved paired t-test results to {out_path}")
    return df_out
