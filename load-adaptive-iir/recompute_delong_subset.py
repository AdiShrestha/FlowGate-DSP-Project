import numpy as np
import pandas as pd
from tqdm import tqdm
from src.multi_seed_evaluation import process_single_run
from src.statistical_tests import batch_delong_comparisons

def main():
    print("Running quick subset to regenerate z-scores in memory for DeLong...")
    regimes_df = pd.read_csv("results/tables/regime_classification.csv")
    unique_regimes = regimes_df['regime'].unique()
    
    fs_assumed = 100.0
    f_c_matched = 0.06 * fs_assumed / (2 * np.pi)
    
    global_mask_list = []
    global_z_scores_dict = {}
    
    # Run 3 seeds per regime (9 total)
    for regime in unique_regimes:
        regime_pool = regimes_df[regimes_df['regime'] == regime]
        sampled_days = regime_pool.sample(n=3, replace=True, random_state=42).reset_index(drop=True)
        
        for idx, row in tqdm(sampled_days.iterrows(), total=3, desc=f"Regime: {regime}"):
            out = process_single_run(idx, row, idx, regime, 100, fs_assumed, f_c_matched)
            if out is not None:
                _, y_true_bin, z_scs = out
                global_mask_list.append(y_true_bin)
                for name, z in z_scs.items():
                    if name not in global_z_scores_dict:
                        global_z_scores_dict[name] = []
                    global_z_scores_dict[name].append(z)

    print("Concatenating and applying np.abs() fix...")
    y_true_agg = np.concatenate(global_mask_list)
    # THE BUG FIX: Wrap with np.abs()
    z_scores_agg = {k: np.abs(np.concatenate(v)) for k, v in global_z_scores_dict.items()}
    
    # Run specific DeLong comparisons
    from src.statistical_tests import run_delong_comparison
    comparisons = [
        ("Load-Adaptive EMA (BW-Matched)", "Fixed EMA"),
        ("Load-Adaptive EMA + Shedding", "Fixed EMA + Shedding"),
        ("RRCF", "Load-Adaptive EMA (BW-Matched)")
    ]
    
    print("\nCorrected DeLong Results (on 9-seed representative subset):")
    for name_A, name_B in comparisons:
        key_A = next((k for k in z_scores_agg if name_A in k), None)
        key_B = next((k for k in z_scores_agg if name_B in k), None)
        if key_A and key_B:
            res = run_delong_comparison(y_true_agg, z_scores_agg[key_A], z_scores_agg[key_B], name_A, name_B)
            print(f"[{name_A} vs {name_B}]")
            print(f"  auc_A={res['auc_A']:.4f}, auc_B={res['auc_B']:.4f}")
            print(f"  delta={res['delta_auc']:.4f}, z={res['z_stat']:.4f}, p={res['p_value']:.2e}")
        else:
            print(f"Could not find {name_A} or {name_B}")

if __name__ == "__main__":
    main()
