"""
experiment_b_throughput_stability.py — Section 4: Sustainable Throughput
Under Overload.

This is the paper's centerpiece experiment. It demonstrates system-level
stability rather than raw filter speed: shedding-enabled configurations
remain stable at arrival rates that cause the plain Fixed EMA baseline's
queue to blow up.

Method
------
1. Read μ_raw per config from Experiment A's CSV.
2. For shedding configs, compute μ_effective(L) = μ_raw / (1 - shed_fraction(L)).
3. Sweep λ from empirical arrival rate up to 10× in 10 log-spaced steps.
4. For each (config, λ): check stability analytically (ρ = λ/μ_eff < 1)
   AND empirically (queue depth doesn't trend upward over a simulated run).
5. Record max stable λ per config.

Run via:  caffeinate -i python -m src.experiment_b_throughput_stability

Outputs
-------
results/tables/experiment_b_throughput.csv
results/figures/experiment_b_queue_stability.png   (money-shot figure)
results/figures/experiment_b_max_throughput_bar.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.data_acquisition import load_tick_series
from src.queue_simulator import simulate_backpressure
from src.load_shedding import CONFIGS, compute_processing_mask


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_data() -> tuple[np.ndarray, np.ndarray, float]:
    """Returns (x, L, empirical_lambda_events_per_sec)."""
    try:
        df = load_tick_series('binance', 'BTCUSDT', ('2024-01-01', '2024-01-01'))
    except Exception:
        print("[Experiment B] Data load failed — using synthetic data.")
        n = 50_000
        rng = np.random.default_rng(0)
        t = np.arange(n) * (1.0 / 8.66)
        p = 40_000.0 + np.cumsum(rng.normal(0, 5, n))
        df = pd.DataFrame({'timestamp': t, 'price': p})

    df = df.iloc[:50_000].reset_index(drop=True)
    bursts = [(10_000, 15_000), (30_000, 35_000)]
    L = simulate_backpressure(df['timestamp'], burst_multiplier=2.0, burst_intervals=bursts)
    x = df['price'].to_numpy(dtype=np.float64)
    L_arr = L.to_numpy(dtype=np.float64)

    total_time = df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]
    empirical_lambda = len(df) / total_time if total_time > 0 else 8.66
    print(f"[Experiment B] Empirical arrival rate λ = {empirical_lambda:.3f} events/s")
    return x, L_arr, empirical_lambda


def _compute_shed_fraction(L: np.ndarray, shed_max_skip: int) -> float:
    """Empirical fraction of ticks skipped under the shedding rule."""
    mask = compute_processing_mask(L, shed_max_skip=shed_max_skip)
    return 1.0 - float(np.mean(mask))


def _mu_effective(mu_raw: float, shed_fraction: float) -> float:
    """
    Effective service rate for a shedding config.
    μ_eff = μ_raw / (1 - shed_fraction)
    If shed_fraction == 0, returns mu_raw unchanged.
    """
    if shed_fraction >= 1.0:
        return float("inf")
    return mu_raw / (1.0 - shed_fraction)


def _simulate_queue_depth(
    lam: float,
    mu_eff: float,
    n_ticks: int = 20_000,
    seed: int = 42,
) -> np.ndarray:
    """
    Simulate a single-server M/M/1-style queue for n_ticks events at arrival
    rate λ and effective service rate μ_eff. Returns queue depth trace.
    """
    rng = np.random.default_rng(seed)
    q = 0.0
    depths = np.empty(n_ticks)
    for i in range(n_ticks):
        inter_arrival = rng.exponential(1.0 / lam)
        service_time = 1.0 / mu_eff  # deterministic service (M/D/1 for simplicity)
        q = max(0.0, q + 1.0 - service_time / inter_arrival)
        depths[i] = q
    return depths


def _is_stable(
    lam: float,
    mu_eff: float,
    n_ticks: int = 20_000,
    seed: int = 42,
) -> tuple[bool, float, np.ndarray]:
    """
    Returns (stable, rho, queue_depth_trace).

    Analytical: ρ = λ/μ_eff.
    Empirical:  stable if queue depth in second half is not trending upward.
    A system is flagged stable only if ρ < 1 AND empirical slope ≤ 0.
    """
    rho = lam / mu_eff if mu_eff > 0 else float("inf")

    depths = _simulate_queue_depth(lam, mu_eff, n_ticks=n_ticks, seed=seed)

    # Empirical trend: linear fit over second half
    half = n_ticks // 2
    second_half = depths[half:]
    x_idx = np.arange(len(second_half), dtype=float)
    slope = float(np.polyfit(x_idx, second_half, 1)[0])

    analytical_stable = rho < 1.0
    empirical_stable = slope <= 0.05  # small positive tolerance for noise
    stable = analytical_stable and empirical_stable

    return stable, rho, depths


def downstream_sensitivity_sweep(df_a_10k: pd.DataFrame, empirical_lambda: float, L: np.ndarray, config_names: list, config_shedding_fracs: dict):
    costs = [1e-6, 5e-6, 10e-6, 25e-6, 50e-6, 100e-6]
    print("\n===== Running Downstream Sensitivity Sweep =====")
    results_sens = []
    
    for cost in costs:
        df_a_copy = df_a_10k.copy()
        df_a_copy["sec_per_sample"] = (df_a_copy["median_time_per_1k_ms"] / 1e6) + cost
        df_a_copy["mu_raw"] = 1.0 / df_a_copy["sec_per_sample"]
        config_mu = dict(zip(df_a_copy["config"], df_a_copy["mu_raw"]))
        
        for c_name in config_names:
            mu_raw = config_mu.get(c_name, empirical_lambda * 2.0)
            shed_frac = config_shedding_fracs.get(c_name, 0.0)
            mu_eff = _mu_effective(mu_raw, shed_frac)
            
            # Re-run a faster sweep to find max stable lambda
            lambda_sweep = np.logspace(np.log10(empirical_lambda), np.log10(mu_eff * 1.2), num=20)
            max_stable_lam = empirical_lambda
            for lam in lambda_sweep:
                stable, _, _ = _is_stable(lam, mu_eff, n_ticks=10000)
                if stable:
                    max_stable_lam = lam
            
            results_sens.append({
                "downstream_cost_us": cost * 1e6,
                "config": c_name,
                "max_stable_lambda": max_stable_lam
            })
            
    df_sens = pd.DataFrame(results_sens)
    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "experiment_b_sensitivity.csv"
    df_sens.to_csv(out_csv, index=False)
    print(f"  Saved: {out_csv}")
    
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    for c_name in config_names:
        subset = df_sens[df_sens["config"] == c_name]
        ax.plot(subset["downstream_cost_us"], subset["max_stable_lambda"], marker="o", label=c_name)
    
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel("Downstream Cost (µs)")
    ax.set_ylabel("Max Stable λ (events/s)")
    ax.set_title("Sensitivity of Max Stable Throughput to Downstream Cost")
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, which="both", ls="--", alpha=0.5)
    fig.tight_layout()
    out_fig = Path("results/figures/experiment_b_sensitivity.png")
    out_fig.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_fig, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out_fig}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_experiment_b() -> pd.DataFrame:
    """
    Run Experiment B, return results DataFrame, save outputs.
    """
    print("\n===== Experiment B: Sustainable Throughput Under Overload =====")

    x, L, empirical_lambda = _load_data()

    # Load Experiment A results for μ_raw
    csv_a = Path("results/tables/experiment_a_compute_cost.csv")
    if not csv_a.exists():
        raise FileNotFoundError(
            f"{csv_a} not found. Run Experiment A first:\n"
            "  python -m src.experiment_a_compute_cost"
        )

    df_a = pd.read_csv(csv_a)
    # Use the 10k timing rows for μ (most representative per-sample cost)
    df_a_10k = df_a[df_a["samples"] == df_a["samples"].min()].copy()

    # -----------------------------------------------------------------------
    # Downstream Cost: Realistic system overhead (deserialisation, DB write, etc.)
    # We load the measured p50 UDP latency.
    # -----------------------------------------------------------------------
    import json
    cost_file = Path("results/tables/downstream_cost_measurement.json")
    if cost_file.exists():
        with open(cost_file, "r") as f:
            DOWNSTREAM_COST_S = json.load(f)["p50_us"] * 1e-6
        print(f"  Loaded measured DOWNSTREAM_COST_S: {DOWNSTREAM_COST_S*1e6:.2f}µs")
    else:
        DOWNSTREAM_COST_S = 5e-6
        print(f"  Fallback DOWNSTREAM_COST_S: {DOWNSTREAM_COST_S*1e6:.2f}µs")

    # median_time_per_1k_ms → seconds per sample
    # ms/1k → s/sample: divide by 1000 (ms→s), divide by 1000 (per 1k)
    df_a_10k["sec_per_sample"] = (df_a_10k["median_time_per_1k_ms"] / 1e6) + DOWNSTREAM_COST_S
    df_a_10k["mu_raw"] = 1.0 / df_a_10k["sec_per_sample"]

    config_mu = dict(zip(df_a_10k["config"], df_a_10k["mu_raw"]))
    print("\n  Raw service rates (events/s):")
    for k, v in config_mu.items():
        print(f"    {k:40s}: μ_raw = {v:,.0f}")



    config_names = list(CONFIGS.keys())
    results = []

    # For each config, compute μ_effective considering shedding
    config_mu_eff = {}
    config_shedding_fracs = {}
    for c_name in config_names:
        cfg = CONFIGS[c_name]
        mu_raw = config_mu.get(c_name, empirical_lambda * 2.0)  # fallback if missing

        if cfg["shedding"]:
            shed_frac = _compute_shed_fraction(L, shed_max_skip=cfg["shed_max_skip"])
            mu_eff = _mu_effective(mu_raw, shed_frac)
            config_shedding_fracs[c_name] = shed_frac
            print(f"  {c_name}: shed_fraction={shed_frac:.3f}, μ_eff={mu_eff:,.0f}")
        else:
            mu_eff = mu_raw
            config_shedding_fracs[c_name] = 0.0
            print(f"  {c_name}: no shedding, μ_eff=μ_raw={mu_eff:,.0f}")

        config_mu_eff[c_name] = mu_eff

    # λ sweep: empirical rate → 20% past the fastest effective service rate
    # This guarantees the sweep crosses the ρ=1 instability threshold for ALL configs.
    # Use 100 points so we have enough resolution to see the difference between
    # the shedding and non-shedding configs' breaking points.
    max_mu_eff = max(config_mu_eff.values()) if config_mu_eff else empirical_lambda * 10.0
    lambda_sweep = np.logspace(
        np.log10(empirical_lambda),
        np.log10(max_mu_eff * 1.2),
        num=100
    )
    print(f"\n  λ sweep: {lambda_sweep[0]:.2f} → {lambda_sweep[-1]:.2f} events/s (100 points)")

    # Stability sweep
    print("\n  Running stability sweep...")
    stability_matrix = {}  # (config, lam) -> (stable, rho)
    queue_traces = {}       # (config, lam) -> depths trace

    for c_name in config_names:
        mu_eff = config_mu_eff[c_name]
        stability_matrix[c_name] = {}
        queue_traces[c_name] = {}
        for lam in lambda_sweep:
            stable, rho, depths = _is_stable(lam, mu_eff)
            stability_matrix[c_name][lam] = (stable, rho)
            queue_traces[c_name][lam] = depths

    # Derive max stable λ per config
    for c_name in config_names:
        mu_eff = config_mu_eff[c_name]
        rho_at_empirical = empirical_lambda / mu_eff

        max_stable_lam = empirical_lambda  # conservative default
        for lam in sorted(stability_matrix[c_name].keys()):
            stable, _ = stability_matrix[c_name][lam]
            if stable:
                max_stable_lam = lam

        results.append({
            "config": c_name,
            "max_stable_lambda_events_per_sec": max_stable_lam,
            "rho_at_empirical_lambda": rho_at_empirical,
            "mu_raw_events_per_sec": config_mu.get(c_name, np.nan),
            "mu_eff_events_per_sec": mu_eff,
        })

    df_results = pd.DataFrame(results).sort_values(
        "max_stable_lambda_events_per_sec", ascending=False
    ).reset_index(drop=True)

    # Save CSV
    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "experiment_b_throughput.csv"
    df_results.to_csv(csv_path, index=False)
    print(f"\n  Saved: {csv_path}")
    print(df_results.to_string(index=False))

    # -----------------------------------------------------------------------
    # Money-shot figure: queue depth over time
    # -----------------------------------------------------------------------
    # Pick λ that is unstable for Fixed EMA but stable for Load-Adaptive+Shedding
    fig_dir = Path("results/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    mu_fixed = config_mu_eff.get("Fixed EMA", empirical_lambda * 2)
    mu_la_shed = config_mu_eff.get("Load-Adaptive EMA + Shedding", empirical_lambda * 5)

    # Find a λ where Fixed EMA is unstable (ρ_fixed >= 1) and LA+Shed is stable (ρ_la < 1)
    money_lam = None
    for lam in sorted(lambda_sweep):
        rho_fixed = lam / mu_fixed
        rho_la = lam / mu_la_shed
        if rho_fixed >= 1.0 and rho_la < 1.0:
            money_lam = lam
            break

    # Fallback: use 2× empirical lambda
    if money_lam is None:
        money_lam = 2.0 * empirical_lambda
        print(f"  [Note] No λ found that splits Fixed EMA vs LA+Shed cleanly; "
              f"using fallback λ = {money_lam:.2f}")

    n_ticks_money = 25_000
    depths_fixed = _simulate_queue_depth(money_lam, mu_fixed, n_ticks=n_ticks_money)
    depths_la_shed = _simulate_queue_depth(money_lam, mu_la_shed, n_ticks=n_ticks_money)

    fig, ax = plt.subplots(figsize=(11, 5))
    tick_axis = np.arange(n_ticks_money)
    ax.plot(tick_axis, depths_fixed, color="#e74c3c", linewidth=0.8,
            label="Fixed EMA (no shedding)", alpha=0.9)
    ax.plot(tick_axis, depths_la_shed, color="#2ecc71", linewidth=0.8,
            label="Load-Adaptive EMA + Shedding", alpha=0.9)
    ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
    ax.set_xlabel("Simulation Tick", fontsize=12)
    ax.set_ylabel("Queue Depth (items)", fontsize=12)
    ax.set_title(
        f"Experiment B — Queue Depth Over Time at λ = {money_lam:.1f} events/s\n"
        f"(Fixed EMA ρ = {money_lam/mu_fixed:.2f}   |   "
        f"Load-Adaptive + Shedding ρ = {money_lam/mu_la_shed:.2f})",
        fontsize=12,
    )
    ax.legend(fontsize=11)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    q_fig_path = fig_dir / "experiment_b_queue_stability.png"
    fig.savefig(q_fig_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {q_fig_path}")

    # -----------------------------------------------------------------------
    # Max throughput bar chart
    # -----------------------------------------------------------------------
    cmap = plt.get_cmap("tab10")
    fig2, ax2 = plt.subplots(figsize=(11, 5))
    bar_configs = df_results["config"].tolist()
    bar_vals = df_results["max_stable_lambda_events_per_sec"].tolist()
    colors = [cmap(i / len(bar_configs)) for i in range(len(bar_configs))]

    bars = ax2.barh(bar_configs, bar_vals, color=colors, alpha=0.88, height=0.6)
    ax2.axvline(empirical_lambda, color="black", linestyle="--", linewidth=1.5,
                label=f"Empirical λ = {empirical_lambda:.2f} ev/s")
    for bar, val in zip(bars, bar_vals):
        ax2.text(val + empirical_lambda * 0.02, bar.get_y() + bar.get_height() / 2,
                 f"{val:.1f}", va="center", fontsize=9)
    ax2.set_xlabel("Max Stable Arrival Rate λ (events/s)", fontsize=12)
    ax2.set_title(
        "Experiment B — Maximum Stable Throughput by Configuration",
        fontsize=13,
    )
    ax2.legend(fontsize=10)
    ax2.grid(axis="x", alpha=0.3)
    fig2.tight_layout()
    bar_fig_path = fig_dir / "experiment_b_max_throughput_bar.png"
    fig2.savefig(bar_fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig2)
    print(f"  Saved: {bar_fig_path}")

    print(f"  Saved: {bar_fig_path}")

    # Run the sensitivity sweep
    downstream_sensitivity_sweep(df_a_10k, empirical_lambda, L, config_names, config_shedding_fracs)

    print("\n===== Experiment B Complete =====")
    return df_results


if __name__ == "__main__":
    run_experiment_b()
