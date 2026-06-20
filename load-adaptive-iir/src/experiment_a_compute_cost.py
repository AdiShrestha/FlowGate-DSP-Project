"""
experiment_a_compute_cost.py — Section 3: Controlled Per-Sample Compute Cost.

Measures wall-clock time for each of the six configurations at three input
lengths, using timeit.repeat (repeat=20, number=1) with randomised config
order to spread thermal-throttling drift evenly (Apple M3 Air is fanless).

Run via:  caffeinate -i python -m src.experiment_a_compute_cost

Outputs
-------
results/tables/experiment_a_compute_cost.csv
results/tables/experiment_metadata.json
results/figures/experiment_a_compute_cost.png
"""

from __future__ import annotations

import json
import platform
import random
import subprocess
import sys
import timeit
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Ensure project root is on path when run as a script
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.data_acquisition import load_tick_series
from src.queue_simulator import simulate_backpressure
from src.load_shedding import CONFIGS, compute_processing_mask, apply_shedding
from src.numba_filters import fixed_iir_direct_form_ii, time_varying_first_order_ema  # ensure warmed up


# ---------------------------------------------------------------------------
# Optional powermetrics (macOS/Apple Silicon)
# ---------------------------------------------------------------------------

def _get_cpu_power_mw() -> float | None:
    """Try to sample CPU power via powermetrics. Returns None if unavailable."""
    try:
        out = subprocess.run(
            ["sudo", "-n", "powermetrics", "-n", "1", "--samplers", "cpu_power"],
            capture_output=True, text=True, timeout=8
        )
        for line in out.stdout.splitlines():
            if "CPU Power" in line:
                return float(line.split(":")[1].strip().split()[0])
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Load data once
# ---------------------------------------------------------------------------

def _load_data(n_target: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns (x, L) arrays of length min(n_target, available) if n_target is
    given, else full length.
    """
    try:
        df = load_tick_series('binance', 'BTCUSDT', ('2024-01-01', '2024-01-01'))
    except Exception:
        print("[Experiment A] Data load failed — using synthetic data.")
        n = n_target or 150_000
        rng = np.random.default_rng(0)
        t = np.arange(n) * (1 / 8.66)
        p = 40_000.0 + np.cumsum(rng.normal(0, 5, n))
        df = pd.DataFrame({'timestamp': t, 'price': p})

    if n_target is not None:
        df = df.iloc[:n_target].reset_index(drop=True)

    bursts = [(len(df) // 5, len(df) // 5 + len(df) // 10),
              (3 * len(df) // 5, 3 * len(df) // 5 + len(df) // 10)]
    L = simulate_backpressure(df['timestamp'], burst_multiplier=2.0, burst_intervals=bursts)
    x = df['price'].to_numpy(dtype=np.float64)
    L_arr = L.to_numpy(dtype=np.float64)
    return x, L_arr


# ---------------------------------------------------------------------------
# Per-config timing runner
# ---------------------------------------------------------------------------

def _time_config(
    config_name: str,
    x: np.ndarray,
    L: np.ndarray,
    repeat: int = 20,
) -> list[float]:
    """
    Returns `repeat` wall-clock times (seconds) for running config_name on x, L.
    Each measurement is one full end-to-end call (warmup already done).
    """
    cfg = CONFIGS[config_name]
    fn = cfg["filter_fn"]
    kwargs = cfg["filter_kwargs_factory"](x, L)

    if not cfg["shedding"]:
        def stmt():
            fn(x, **kwargs)
    else:
        process_mask = compute_processing_mask(L, shed_max_skip=cfg["shed_max_skip"])
        y_buf = np.empty(len(x))

        def stmt():
            apply_shedding(y_buf, x, process_mask, fn, kwargs)

    # One untimed warmup call
    stmt()

    times = timeit.repeat(stmt, repeat=repeat, number=1)
    return times


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_experiment_a(repeat: int = 20) -> pd.DataFrame:
    """
    Run Experiment A and return results DataFrame.
    Also saves CSV, JSON metadata, and PNG figure.
    """
    print("\n===== Experiment A: Controlled Per-Sample Compute Cost =====")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python: {sys.version}")

    # Input lengths to test
    LENGTHS = [10_000, 100_000, None]  # None = full available series

    # Load full data once
    x_full, L_full = _load_data(n_target=None)
    full_len = len(x_full)
    LENGTHS_RESOLVED = [min(10_000, full_len), min(100_000, full_len), full_len]
    print(f"Full data length: {full_len:,} samples")

    config_names = list(CONFIGS.keys())

    # Build the randomised job list: (config, samples_index) pairs
    jobs = []
    for s_idx, n_samples in enumerate(LENGTHS_RESOLVED):
        for c_name in config_names:
            jobs.append((c_name, s_idx, n_samples))

    # Randomise order across configs (not within a config) to spread thermal drift
    random.seed(2024)
    random.shuffle(jobs)

    # Storage: dict keyed by (config, n_samples) -> list of times
    raw_times: dict[tuple[str, int], list[float]] = {}

    total = len(jobs)
    for step, (c_name, s_idx, n_samples) in enumerate(jobs, 1):
        x_sub = x_full[:n_samples]
        L_sub = L_full[:n_samples]
        print(f"  [{step}/{total}] {c_name:35s}  n={n_samples:>7,} ...", end=" ", flush=True)
        times = _time_config(c_name, x_sub, L_sub, repeat=repeat)
        raw_times[(c_name, n_samples)] = times
        med = np.median(times) / n_samples * 1000 * 1000  # ms per 1k samples
        print(f"median={med:.4f} ms/1k")

    # Optional power measurement (best-effort, single shot at end)
    print("\n  Attempting CPU power measurement via powermetrics...")
    power_readings: dict[str, float | None] = {}
    for c_name in config_names:
        n_samples = LENGTHS_RESOLVED[0]  # quick measurement at 10k
        x_sub = x_full[:n_samples]
        L_sub = L_full[:n_samples]
        p_before = _get_cpu_power_mw()
        _time_config(c_name, x_sub, L_sub, repeat=5)
        p_after = _get_cpu_power_mw()
        if p_before is not None and p_after is not None:
            power_readings[c_name] = (p_before + p_after) / 2
        else:
            power_readings[c_name] = None

    if all(v is None for v in power_readings.values()):
        print("  powermetrics unavailable (sudo not granted non-interactively); skipping power column.")

    # Build results dataframe
    rows = []
    for (c_name, n_samples), times in raw_times.items():
        times_ms_per_1k = [t / n_samples * 1000 * 1000 for t in times]
        median_ms = float(np.median(times_ms_per_1k))
        q25, q75 = np.percentile(times_ms_per_1k, [25, 75])
        iqr_ms = float(q75 - q25)
        rows.append({
            "config": c_name,
            "samples": n_samples,
            "median_time_per_1k_ms": median_ms,
            "iqr_ms": iqr_ms,
            "avg_cpu_power_mw": power_readings.get(c_name),
        })

    df = pd.DataFrame(rows).sort_values(["samples", "config"]).reset_index(drop=True)

    # Save CSV
    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "experiment_a_compute_cost.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  Saved: {csv_path}")

    # Save metadata JSON
    metadata = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "trial_count_per_config_per_length": repeat,
        "input_lengths_tested": LENGTHS_RESOLVED,
        "config_names": config_names,
        "note": "Timing is wall-clock, median over repeat trials. "
                "Run wrapped with `caffeinate -i` for best results on Apple Silicon.",
    }
    meta_path = out_dir / "experiment_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved: {meta_path}")

    # -----------------------------------------------------------------------
    # Figure: grouped bar chart
    # -----------------------------------------------------------------------
    fig_dir = Path("results/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    lengths_label = [f"{n//1000}k" if n < 1_000_000 else f"{n/1_000_000:.1f}M"
                     for n in LENGTHS_RESOLVED]

    cmap = plt.get_cmap("tab10")
    fig, ax = plt.subplots(figsize=(13, 6))

    x_positions = np.arange(len(LENGTHS_RESOLVED))
    n_configs = len(config_names)
    width = 0.8 / n_configs
    offsets = np.linspace(-(n_configs - 1) / 2, (n_configs - 1) / 2, n_configs) * width

    for c_idx, c_name in enumerate(config_names):
        medians = []
        iqrs = []
        for n_samples in LENGTHS_RESOLVED:
            row = df[(df["config"] == c_name) & (df["samples"] == n_samples)]
            if len(row) == 0:
                medians.append(0); iqrs.append(0)
            else:
                medians.append(row["median_time_per_1k_ms"].values[0])
                iqrs.append(row["iqr_ms"].values[0])

        bars = ax.bar(
            x_positions + offsets[c_idx], medians,
            width=width,
            label=c_name,
            color=cmap(c_idx / n_configs),
            alpha=0.88,
            yerr=iqrs,
            capsize=3,
            error_kw={"elinewidth": 1.2, "alpha": 0.7},
        )

    ax.set_xticks(x_positions)
    ax.set_xticklabels([f"{l}\n({n:,} samples)" for l, n in zip(lengths_label, LENGTHS_RESOLVED)],
                       fontsize=10)
    ax.set_xlabel("Input Length", fontsize=12)
    ax.set_ylabel("Median Time per 1,000 Samples (ms)", fontsize=12)
    ax.set_title(
        "Experiment A — Per-Sample Compute Cost by Configuration\n"
        "(Error bars = IQR over 20 trials; all implementations via Numba JIT)",
        fontsize=13,
    )
    ax.legend(title="Configuration", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    fig_path = fig_dir / "experiment_a_compute_cost.png"
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {fig_path}")

    print("\n===== Experiment A Complete =====")
    print(df.to_string(index=False))
    return df


if __name__ == "__main__":
    run_experiment_a()
