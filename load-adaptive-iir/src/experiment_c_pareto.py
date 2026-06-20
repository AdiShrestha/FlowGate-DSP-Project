"""
experiment_c_pareto.py — Section 5: Detection Quality vs. Compute Cost
Pareto Curve.

Reuses existing ROC-AUC from results/tables/comparison.csv (do NOT recompute).
Adds max stable λ from Experiment B.
Identifies Pareto-optimal frontier and produces honest, numeric conclusion.

Run via:  caffeinate -i python -m src.experiment_c_pareto

Outputs
-------
results/figures/experiment_c_pareto.png
results/compute_benefit_summary.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ---------------------------------------------------------------------------
# ROC-AUC mapping: comparison.csv → config name
# ---------------------------------------------------------------------------

# The existing comparison.csv uses filter names from run_all.py. We need to
# map those to the six configuration names used in Experiments A and B.
# Unmapped configs (those without a detection-quality measurement) will use
# a heuristic fallback explained in the summary.
_AUC_NAME_MAP = {
    "Fixed EMA (0.06)":       "Fixed EMA",
    "Load Adaptive EMA":      "Load-Adaptive EMA",
    "KAMA":                    "KAMA",
    "Butterworth (Default)":  "Butterworth",
    "Butterworth (Matched)":  None,  # skip — not in our 6 configs
}

# For configs that inherit their ROC-AUC from the base filter
# (shedding changes throughput but not detection quality *on processed ticks*,
# though it delays anomaly detection slightly — the shedding delay from Exp B
# is reported but AUC is approximated from the base filter here, with a note).
_AUC_INHERIT = {
    "Fixed EMA + Shedding":       "Fixed EMA",
    "Load-Adaptive EMA + Shedding": "Load-Adaptive EMA",
}


def _load_existing_auc() -> dict[str, float]:
    """
    Load ROC-AUC from results/tables/comparison.csv.
    Returns dict: original_name -> roc_auc.
    """
    csv_path = Path("results/tables/comparison.csv")
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} not found. Run the main pipeline first:\n"
            "  python -m src.run_all"
        )
    df = pd.read_csv(csv_path, index_col=0)
    if "ROC AUC" not in df.columns:
        raise KeyError(f"'ROC AUC' column not in {csv_path}. Available: {list(df.columns)}")
    return dict(zip(df.index, df["ROC AUC"]))


def _load_exp_b() -> dict[str, float]:
    """Load max stable λ per config from Experiment B CSV."""
    csv_path = Path("results/tables/experiment_b_throughput.csv")
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} not found. Run Experiment B first:\n"
            "  python -m src.experiment_b_throughput_stability"
        )
    df = pd.read_csv(csv_path)
    return dict(zip(df["config"], df["max_stable_lambda_events_per_sec"]))


def _pareto_frontier(points: np.ndarray) -> np.ndarray:
    """
    Given (n, 2) array of (x, y) = (throughput, auc), return boolean mask of
    Pareto-optimal points (not strictly dominated by any other on both axes).
    Higher is better on both axes.
    """
    n = len(points)
    pareto = np.ones(n, dtype=bool)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # j strictly dominates i if j is better on both axes
            if points[j, 0] > points[i, 0] and points[j, 1] > points[i, 1]:
                pareto[i] = False
                break
    return pareto


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_experiment_c() -> None:
    print("\n===== Experiment C: Detection Quality vs. Compute Cost Pareto Curve =====")

    # --- Load data ---
    raw_auc = _load_existing_auc()
    print(f"\n  Loaded ROC-AUC from comparison.csv: {raw_auc}")

    exp_b = _load_exp_b()
    print(f"\n  Loaded max stable λ from Experiment B: {exp_b}")

    # --- Build per-config (throughput, auc) pairs ---
    config_names = [
        "Fixed EMA",
        "Fixed EMA + Shedding",
        "KAMA",
        "Butterworth",
        "Load-Adaptive EMA",
        "Load-Adaptive EMA + Shedding",
    ]

    # Build AUC lookup for 6 configs
    config_auc: dict[str, float] = {}
    for c_name in config_names:
        # Direct mapping
        direct = None
        for orig, cfg in _AUC_NAME_MAP.items():
            if cfg == c_name and orig in raw_auc:
                direct = raw_auc[orig]
                break
        if direct is not None:
            config_auc[c_name] = direct
        elif c_name in _AUC_INHERIT:
            # Shedding variant inherits base filter's AUC
            base = _AUC_INHERIT[c_name]
            for orig, cfg in _AUC_NAME_MAP.items():
                if cfg == base and orig in raw_auc:
                    config_auc[c_name] = raw_auc[orig]
                    break
        else:
            config_auc[c_name] = np.nan

    print(f"\n  Resolved ROC-AUC per config: {config_auc}")

    # Filter to configs that have both throughput and AUC
    valid = [(c, exp_b[c], config_auc[c])
             for c in config_names
             if c in exp_b and not np.isnan(config_auc.get(c, np.nan))]

    if len(valid) < 2:
        raise RuntimeError(
            "Not enough configs with both throughput and AUC data to plot Pareto curve. "
            "Check that Experiments A, B and the main pipeline have all been run."
        )

    names  = [v[0] for v in valid]
    thru   = np.array([v[1] for v in valid])  # x-axis: max stable λ
    auc    = np.array([v[2] for v in valid])  # y-axis: ROC-AUC

    points = np.column_stack([thru, auc])
    pareto_mask = _pareto_frontier(points)

    # -----------------------------------------------------------------------
    # Pareto figure
    # -----------------------------------------------------------------------
    fig_dir = Path("results/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    cmap = plt.get_cmap("tab10")
    fig, ax = plt.subplots(figsize=(10, 7))

    # Draw Pareto frontier line through Pareto-optimal points (sorted by x)
    p_pts = points[pareto_mask]
    p_names = [n for n, p in zip(names, pareto_mask) if p]
    if len(p_pts) >= 2:
        sort_idx = np.argsort(p_pts[:, 0])
        ax.plot(p_pts[sort_idx, 0], p_pts[sort_idx, 1],
                color="gold", linewidth=2, linestyle="--",
                zorder=2, label="Pareto frontier")

    for i, (name, point, is_pareto) in enumerate(zip(names, points, pareto_mask)):
        color = cmap(i / len(names))
        marker = "★" if is_pareto else "o"
        size = 220 if is_pareto else 120
        ax.scatter(point[0], point[1], c=[color], s=size,
                   zorder=3, edgecolors="black" if is_pareto else "none",
                   linewidths=1.5)
        offset_x = (thru.max() - thru.min()) * 0.012
        offset_y = (auc.max() - auc.min()) * 0.015
        ax.annotate(
            f"{'★ ' if is_pareto else ''}{name}",
            xy=(point[0], point[1]),
            xytext=(point[0] + offset_x, point[1] + offset_y),
            fontsize=8.5,
            color=color if not is_pareto else "black",
            fontweight="bold" if is_pareto else "normal",
        )

    ax.set_xlabel("Max Stable Arrival Rate λ (events/s)\n← lower throughput headroom    |    more throughput headroom →",
                  fontsize=11)
    ax.set_ylabel("ROC-AUC (Detection Quality)\n← worse detection    |    better detection →", fontsize=11)
    ax.set_title(
        "Experiment C — Detection Quality vs. Throughput Pareto Curve\n"
        "(★ = Pareto-optimal; dashed gold = Pareto frontier)",
        fontsize=13,
    )

    pareto_patch = mpatches.Patch(color="gold", label="Pareto frontier")
    ax.legend(handles=[pareto_patch], fontsize=10, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    pareto_fig_path = fig_dir / "experiment_c_pareto.png"
    fig.savefig(pareto_fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  Saved: {pareto_fig_path}")

    # -----------------------------------------------------------------------
    # Honest numeric conclusion — Section 5 requirement
    # -----------------------------------------------------------------------
    la_shed_name = "Load-Adaptive EMA + Shedding"
    la_shed_on_pareto = pareto_mask[names.index(la_shed_name)] if la_shed_name in names else None
    la_shed_thru  = exp_b.get(la_shed_name, np.nan)
    la_shed_auc   = config_auc.get(la_shed_name, np.nan)
    fixed_thru    = exp_b.get("Fixed EMA", np.nan)
    fixed_auc     = config_auc.get("Fixed EMA", np.nan)

    # Determine dominators
    dominators = []
    if la_shed_name in names:
        la_idx = names.index(la_shed_name)
        for i, n in enumerate(names):
            if n == la_shed_name:
                continue
            if points[i, 0] >= la_shed_thru and points[i, 1] >= la_shed_auc:
                dominators.append(n)

    if la_shed_on_pareto is None:
        pareto_status = "Load-Adaptive EMA + Shedding was not present in valid results."
    elif la_shed_on_pareto and len(dominators) == 0:
        pareto_status = (
            f"**ON the Pareto frontier** — no other configuration simultaneously achieves "
            f"higher throughput AND higher ROC-AUC."
        )
    elif not la_shed_on_pareto and len(dominators) > 0:
        pareto_status = (
            f"**DOMINATED** by: {', '.join(dominators)}. "
            f"These configurations achieve both higher throughput and higher detection quality."
        )
    else:
        pareto_status = (
            f"**PARTIALLY DOMINATED** — sits between dominated and frontier status. "
            f"Potential dominators: {', '.join(dominators) if dominators else 'none identified'}."
        )

    throughput_gain_pct = (
        (la_shed_thru - fixed_thru) / fixed_thru * 100
        if not np.isnan(fixed_thru) and fixed_thru > 0 else np.nan
    )
    auc_diff = la_shed_auc - fixed_auc if not np.isnan(fixed_auc) else np.nan

    pareto_configs_str = ", ".join([n for n, p in zip(names, pareto_mask) if p])

    summary = f"""# Compute Benefit Summary — Load-Adaptive IIR Project

Generated by `src/experiment_c_pareto.py` using actual measured numbers.
Do not edit this file manually — re-run Experiment C to update.

## Pareto Analysis: Detection Quality vs. Throughput

### Data Used
- **Throughput (x-axis):** Max stable arrival rate λ (events/s) from Experiment B.
- **Detection quality (y-axis):** ROC-AUC from the main pipeline's comparison.csv.
- **Six configurations evaluated:** {', '.join(names)}.

### Pareto-Optimal Frontier
The following configurations are **NOT strictly dominated** by any other on both axes:

**{pareto_configs_str}**

### Where Does Load-Adaptive EMA + Shedding Land?

| Metric | Load-Adaptive EMA + Shedding | Fixed EMA (baseline) |
|---|---|---|
| Max stable λ (ev/s) | {la_shed_thru:.2f} | {fixed_thru:.2f} |
| ROC-AUC | {la_shed_auc:.4f} | {fixed_auc:.4f} |
| Throughput gain vs. Fixed EMA | {throughput_gain_pct:+.1f}% | — |
| AUC change vs. Fixed EMA | {auc_diff:+.4f} | — |

**Pareto status:** {pareto_status}

### Interpretation (Honest, Numeric)

{"Load-Adaptive EMA + Shedding achieves a throughput of **" + f"{la_shed_thru:.2f} events/s** compared to the Fixed EMA baseline's **{fixed_thru:.2f} events/s** ({throughput_gain_pct:+.1f}%). " if not np.isnan(throughput_gain_pct) else ""}{"The detection quality (ROC-AUC) " + ("is **higher** at " if auc_diff > 0 else "is **lower** at " if auc_diff < 0 else "is **equal** at ") + f"{la_shed_auc:.4f} versus {fixed_auc:.4f} for Fixed EMA ({auc_diff:+.4f} absolute difference)." if not np.isnan(auc_diff) else "Detection quality data unavailable."}

{"The load-adaptive configuration **does** sit on the Pareto frontier, meaning it offers a genuinely better tradeoff than all baselines on at least one axis without being worse on the other." if la_shed_on_pareto else "The load-adaptive configuration **does not** sit on the Pareto frontier — the numbers show it is dominated. The claim that it offers a resource-saving benefit is not supported by these measurements."}

### Notes on AUC for Shedding Variants
AUC for Fixed EMA + Shedding and Load-Adaptive EMA + Shedding is **approximated** from
their base filter's AUC from the existing comparison.csv. Shedding changes throughput but
the detection quality on processed ticks is identical to the base filter; what changes is
that anomaly detection can be delayed by up to `shed_max_skip` ticks when the onset falls
on a skipped tick. This delay is reported separately in Experiment B.

### Energy Measurement Caveat
If `avg_cpu_power_mw` values appear in `experiment_a_compute_cost.csv`, note that
`powermetrics` power values are appropriate for **same-machine, same-session comparison
only** (per Apple's own documentation). Do not use them for cross-device claims.
"""

    summary_path = Path("results/compute_benefit_summary.md")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary)
    print(f"  Saved: {summary_path}")

    print("\n--- Pareto Summary ---")
    print(f"  Pareto-optimal configs: {pareto_configs_str}")
    print(f"  Load-Adaptive EMA + Shedding on Pareto frontier: {la_shed_on_pareto}")
    print(f"  {pareto_status}")
    print("\n===== Experiment C Complete =====")


if __name__ == "__main__":
    run_experiment_c()
