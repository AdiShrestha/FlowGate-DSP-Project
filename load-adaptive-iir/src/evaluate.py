import numpy as np
import pandas as pd
from sklearn.metrics import auc
from pathlib import Path

def evaluate_predictions(
    y_true: np.ndarray, 
    y_pred: np.ndarray, 
    anomaly_info: list, 
    buffer: int = 20
):
    """
    Evaluates binary predictions against ground truth using a tolerance buffer.
    """
    n_samples = len(y_true)
    
    # 1. Expand ground truth to include buffer for valid detections
    valid_windows = np.zeros(n_samples, dtype=bool)
    for info in anomaly_info:
        start = max(0, info['start'] - buffer)
        end = min(n_samples, info['end'] + buffer + 1)
        valid_windows[start:end] = True
        
    # TP: predicted true AND inside a valid window
    # FP: predicted true AND outside all valid windows
    TP_mask = y_pred & valid_windows
    FP_mask = y_pred & ~valid_windows
    
    TP_points = np.sum(TP_mask)
    FP_points = np.sum(FP_mask)
    
    precision = TP_points / (TP_points + FP_points) if (TP_points + FP_points) > 0 else 0.0
    recall = min(1.0, TP_points / np.sum(y_true)) if np.sum(y_true) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Latency: for each anomaly, distance from start to first detection in [start, end+buffer]
    latencies = []
    for info in anomaly_info:
        start = info['start']
        end = min(n_samples, info['end'] + buffer + 1)
        
        preds_in_window = np.where(y_pred[start:end])[0]
        if len(preds_in_window) > 0:
            first_pred_idx = start + preds_in_window[0]
            latency = max(0, first_pred_idx - start)
            latencies.append(latency)
    
    mean_latency = np.mean(latencies) if latencies else np.nan
    
    # FP rate: false positives per 1000 samples outside valid windows
    n_outside = n_samples - np.sum(valid_windows)
    fp_rate = (FP_points / n_outside) * 1000 if n_outside > 0 else 0.0
    
    return precision, recall, f1, mean_latency, fp_rate

def compute_auc(z_scores: np.ndarray, anomaly_info: list, mask: np.ndarray, buffer: int = 20):
    """
    Computes ROC and PR curves by sweeping the detection threshold.
    """
    n_samples = len(z_scores)
    valid_windows = np.zeros(n_samples, dtype=bool)
    for info in anomaly_info:
        start = max(0, info['start'] - buffer)
        end = min(n_samples, info['end'] + buffer + 1)
        valid_windows[start:end] = True
        
    abs_z = np.abs(z_scores)
    thresholds = np.sort(np.unique(abs_z))[::-1]
    if len(thresholds) > 200:
        thresholds = thresholds[np.linspace(0, len(thresholds)-1, 200).astype(int)]
        
    tprs, fprs, precs = [], [], []
    
    total_pos = np.sum(mask)
    total_neg = n_samples - np.sum(valid_windows)
    
    if total_pos == 0 or total_neg == 0:
         return 0.0, 0.0, [], [], [], []
         
    for th in thresholds:
        y_pred = abs_z >= th
        
        TP = np.sum(y_pred & valid_windows)
        FP = np.sum(y_pred & ~valid_windows)
        
        tpr = min(1.0, TP / total_pos)
        fpr = min(1.0, FP / total_neg)
        prec = TP / (TP + FP) if (TP + FP) > 0 else 1.0
        
        tprs.append(tpr)
        fprs.append(fpr)
        precs.append(prec)
        
    if fprs[-1] < 1.0:
        fprs.append(1.0)
        tprs.append(1.0)
        precs.append(total_pos / (total_pos + total_neg))
        
    roc_auc = auc(fprs, tprs)
    pr_auc = auc(tprs, precs)
    
    return roc_auc, pr_auc, fprs, tprs, precs, thresholds

def format_results_table(results_dict, out_path="results/tables/comparison.csv"):
    """
    Saves the results dictionary to a CSV and returns a pandas DataFrame.
    """
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame.from_dict(results_dict, orient='index')
    cols = ['Precision', 'Recall', 'F1', 'Mean Latency', 'FP Rate (per 1k)', 'ROC AUC', 'PR AUC', 'PR Baseline']
    df = df[cols]
    df.to_csv(out_path)
    return df


def evaluate_by_type(
    mask: np.ndarray,
    detections: dict,
    z_scores: dict,
    anomaly_info: list,
    out_dir: str = "results/tables"
) -> dict:
    """
    §9: Runs evaluation separately for each anomaly type (point, level_shift,
    volatility_burst) and saves one CSV per type.

    Returns a dict mapping anomaly_type → results DataFrame.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    anomaly_types = sorted({info['type'] for info in anomaly_info})
    per_type_results = {}

    for atype in anomaly_types:
        # Filter anomaly_info and mask to this type only
        type_info = [a for a in anomaly_info if a['type'] == atype]

        # Build a type-specific ground-truth mask
        n_samples = len(mask)
        type_mask = np.zeros(n_samples, dtype=bool)
        for info in type_info:
            type_mask[info['start']:info['end'] + 1] = True

        results_dict = {}
        for name, z in z_scores.items():
            det = detections[name]
            prec, rec, f1, lat, fpr = evaluate_predictions(type_mask, det, type_info)
            roc_auc, pr_auc, fprs, tprs, precs, ths = compute_auc(z, type_info, type_mask)
            results_dict[name] = {
                'Precision':        prec,
                'Recall':           rec,
                'F1':               f1,
                'Mean Latency':     lat,
                'FP Rate (per 1k)': fpr,
                'ROC AUC':          roc_auc,
                'PR AUC':           pr_auc,
                'PR Baseline':      np.sum(type_mask) / n_samples,
            }

        df = pd.DataFrame.from_dict(results_dict, orient='index')
        cols = ['Precision', 'Recall', 'F1', 'Mean Latency', 'FP Rate (per 1k)', 'ROC AUC', 'PR AUC', 'PR Baseline']
        df = df[cols]
        safe_name = atype.replace(' ', '_')
        df.to_csv(f"{out_dir}/comparison_{safe_name}.csv")
        per_type_results[atype] = df

    return per_type_results
