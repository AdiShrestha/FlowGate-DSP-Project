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
    recall = TP_points / np.sum(valid_windows) if np.sum(valid_windows) > 0 else 0.0
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

def compute_auc(z_scores: np.ndarray, anomaly_info: list, buffer: int = 20):
    """
    Computes ROC and PR curves by sweeping the detection threshold.
    """
    n_samples = len(z_scores)
    valid_windows = np.zeros(n_samples, dtype=bool)
    for info in anomaly_info:
        start = max(0, info['start'] - buffer)
        end = min(n_samples, info['end'] + buffer + 1)
        valid_windows[start:end] = True
        
    thresholds = np.linspace(1.0, 6.0, 50)
    tprs, fprs, precs = [], [], []
    
    total_pos = np.sum(valid_windows)
    total_neg = n_samples - total_pos
    
    if total_pos == 0 or total_neg == 0:
         return 0.0, 0.0, [], [], [], []
         
    for th in thresholds:
        y_pred = np.abs(z_scores) > th
        
        TP = np.sum(y_pred & valid_windows)
        FP = np.sum(y_pred & ~valid_windows)
        
        tpr = TP / total_pos
        fpr = FP / total_neg
        prec = TP / (TP + FP) if (TP + FP) > 0 else 1.0
        
        tprs.append(tpr)
        fprs.append(fpr)
        precs.append(prec)
        
    # auc function expects x to be monotonically increasing
    # Since higher threshold means lower FPR, we reverse the arrays
    fprs_rev = fprs[::-1]
    tprs_rev = tprs[::-1]
    roc_auc = auc(fprs_rev, tprs_rev)
    
    # PR AUC
    # tprs (recall) is decreasing with higher threshold, so reverse to make it increasing
    pr_auc = auc(tprs_rev, precs[::-1])
    
    return roc_auc, pr_auc, fprs, tprs, precs, thresholds

def format_results_table(results_dict, out_path="results/tables/comparison.csv"):
    """
    Saves the results dictionary to a CSV and returns a pandas DataFrame.
    """
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame.from_dict(results_dict, orient='index')
    # columns = [precision, recall, F1, mean_latency, FP_rate, ROC_AUC, PR_AUC]
    cols = ['Precision', 'Recall', 'F1', 'Mean Latency', 'FP Rate (per 1k)', 'ROC AUC', 'PR AUC']
    df = df[cols]
    df.to_csv(out_path)
    return df
