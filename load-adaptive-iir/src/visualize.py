import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def plot_time_domain_comparison(
    timestamps, 
    x_injected, 
    filter_outputs, 
    anomaly_info, 
    detections, 
    out_path="results/figures/time_domain_comparison.png"
):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    
    n_filters = len(filter_outputs)
    fig, axes = plt.subplots(n_filters, 1, figsize=(15, 3 * n_filters), sharex=True)
    if n_filters == 1: axes = [axes]
    
    for ax, (name, y) in zip(axes, filter_outputs.items()):
        ax.plot(timestamps, x_injected, color='lightgray', label='Raw (with anomalies)')
        ax.plot(timestamps, y, color='blue', linewidth=1.5, label=f'Filtered ({name})')
        
        # Plot true anomalies
        first_anomaly = True
        for info in anomaly_info:
            start_t = timestamps.iloc[info['start']]
            end_t = timestamps.iloc[info['end']]
            ax.axvspan(start_t, end_t, color='red', alpha=0.2, label='True Anomaly' if first_anomaly else "")
            first_anomaly = False
            
        # Plot detections
        det = detections[name]
        det_idx = np.where(det)[0]
        if len(det_idx) > 0:
            ax.plot(timestamps.iloc[det_idx], x_injected[det_idx], 'rx', markersize=6, label='Detection')
            
        ax.set_title(name)
        ax.set_ylabel("Price")
        
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper left')
        ax.grid(True, alpha=0.3)
        
    axes[-1].set_xlabel("Time")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def plot_roc_pr_curves(
    auc_data, 
    out_path="results/figures/roc_pr_curves.png"
):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for (name, data), color in zip(auc_data.items(), colors):
        roc_auc, pr_auc, fprs, tprs, precs, _ = data
        
        # ROC
        ax1.plot(fprs, tprs, color=color, label=f"{name} (AUC = {roc_auc:.2f})")
        
        # PR
        ax2.plot(tprs, precs, color=color, label=f"{name} (AUC = {pr_auc:.2f})")
        
    ax1.plot([0, 1], [0, 1], 'k--', alpha=0.5)
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.05])
    ax1.set_xlabel('False Positive Rate')
    ax1.set_ylabel('True Positive Rate (Recall)')
    ax1.set_title('ROC Curve')
    ax1.legend(loc="lower right")
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlim([0.0, 1.0])
    ax2.set_ylim([0.0, 1.05])
    ax2.set_xlabel('Recall (TPR)')
    ax2.set_ylabel('Precision')
    ax2.set_title('Precision-Recall Curve')
    ax2.legend(loc="lower left")
    ax2.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def plot_metrics_bar_comparison(
    results_df: pd.DataFrame, 
    out_path="results/figures/metrics_bar_comparison.png"
):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    filters = results_df.index
    x = np.arange(len(filters))
    width = 0.6
    
    ax1.bar(x, results_df['F1'], width, color='skyblue')
    ax1.set_title('F1 Score')
    ax1.set_xticks(x)
    ax1.set_xticklabels(filters, rotation=45, ha='right')
    ax1.set_ylim(0, 1)
    ax1.grid(True, axis='y', alpha=0.3)
    
    ax2.bar(x, results_df['Mean Latency'], width, color='salmon')
    ax2.set_title('Mean Detection Latency (samples)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(filters, rotation=45, ha='right')
    ax2.grid(True, axis='y', alpha=0.3)
    
    ax3.bar(x, results_df['FP Rate (per 1k)'], width, color='lightgreen')
    ax3.set_title('False Positive Rate (per 1k)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(filters, rotation=45, ha='right')
    ax3.grid(True, axis='y', alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
