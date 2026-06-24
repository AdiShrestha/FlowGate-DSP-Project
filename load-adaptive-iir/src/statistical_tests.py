import numpy as np
import pandas as pd
from pathlib import Path
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
