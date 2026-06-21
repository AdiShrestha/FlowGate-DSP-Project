"""
load_shedding.py — Composable load-shedding layer for Section 2.

The shedding mechanism is orthogonal to whether a filter's own
pole/coefficient adapts to load. It can be applied to any of the four
filters without modifying them.

Six named configurations are registered in CONFIGS (Section 2.3):

  1. Fixed EMA (baseline)            — no pole adaptation, no shedding
  2. Fixed EMA + Shedding            — no pole adaptation, shedding ON
  3. KAMA (baseline)                 — volatility-driven alpha, no shedding
  4. Butterworth (baseline)          — fixed IIR, no shedding
  5. Load-Adaptive EMA (pole-only)   — load-driven pole, no shedding
  6. Load-Adaptive EMA + Shedding    — load-driven pole AND shedding
"""

from __future__ import annotations

import numpy as np
from typing import Callable

from src.filters import fixed_ema, load_adaptive_ema, kama, butterworth_lowpass
from src.numba_filters import compute_processing_mask_kernel, apply_shedding_forward_fill_y


# ---------------------------------------------------------------------------
# 2.1  Deterministic processing mask
# ---------------------------------------------------------------------------

def compute_processing_mask(L: np.ndarray, shed_max_skip: int = 4) -> np.ndarray:
    """
    Deterministic stride rule: at backpressure L[i] in [0,1] the target
    number of consecutive skips is  round(shed_max_skip * L[i]).
    A tick is processed whenever the number of ticks since the last
    processed tick reaches the (per-tick, possibly changing) target skip.

    Parameters
    ----------
    L             : 1-D array of backpressure values in [0, 1].
    shed_max_skip : Maximum consecutive ticks skipped at L=1.
                    (e.g. 4 → process at least 1 in 5 ticks at max load.)

    Returns
    -------
    process : boolean array, True = process this tick, False = skip it.
    """
    if np.any(np.isnan(L)):
        raise ValueError("compute_processing_mask: L contains NaN — "
                         "caller must sanitise backpressure before shedding.")

    return compute_processing_mask_kernel(L, shed_max_skip)


# ---------------------------------------------------------------------------
# 2.2  Shedding wrapper
# ---------------------------------------------------------------------------

def apply_shedding(
    y_full: np.ndarray,
    x: np.ndarray,
    process_mask: np.ndarray,
    filter_fn: Callable,
    filter_kwargs: dict,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run filter_fn only on the sub-sequence of processed ticks, then
    forward-fill at skipped indices to the last processed value.

    This is what actually saves the compute — the filter kernel is never
    called for skipped indices.

    Parameters
    ----------
    y_full        : Pre-allocated output array (will be written in-place).
    x             : Full input signal.
    process_mask  : Boolean mask from compute_processing_mask.
    filter_fn     : One of the four filter functions (fixed_ema, etc.).
    filter_kwargs : Keyword arguments for filter_fn, adapted to sub-sequence.

    Returns
    -------
    y             : Output signal with forward-fill at skipped ticks.
    pole_traj     : Pole trajectory (only at processed ticks; NaN elsewhere).
    """
    n = len(x)
    y = np.empty(n)
    pole_traj = np.full(n, np.nan)

    processed_indices = np.where(process_mask)[0]
    if len(processed_indices) == 0:
        y[:] = x[0]
        return y, pole_traj

    x_sub = x[processed_indices]

    # Adapt L to sub-sequence if present in kwargs
    kwargs_sub = {}
    for k, v in filter_kwargs.items():
        if k == 'L':
            kwargs_sub[k] = np.asarray(v)[processed_indices]
        else:
            kwargs_sub[k] = v

    y_sub, pole_sub = filter_fn(x_sub, **kwargs_sub)

    # Numba vectorised forward fill for y
    y = apply_shedding_forward_fill_y(process_mask, y_sub, x[0])
    
    # Vectorised pole scatter (NO forward fill for poles)
    if pole_sub.ndim == 1:
        pole_traj[process_mask] = pole_sub

    return y, pole_traj


# ---------------------------------------------------------------------------
# 2.3 Shedding-delay metric
# ---------------------------------------------------------------------------

def compute_shedding_delay(
    anomaly_info: list[dict],
    process_mask: np.ndarray,
) -> float:
    """
    For each anomaly, find the first onset tick that is processed.
    Return the mean additional samples of delay attributable to shedding
    (i.e. how many ticks from the anomaly's start until the first processed
    tick at or after that start).

    This is a genuine, reportable cost of the mechanism — not hidden.

    Returns
    -------
    mean_delay : float   Mean additional delay in samples (0.0 if all onset
                         ticks happen to be processed).
    """
    delays = []
    for info in anomaly_info:
        onset = info['start']
        # Find first processed tick at or after onset
        if onset >= len(process_mask):
            continue
        for j in range(onset, len(process_mask)):
            if process_mask[j]:
                delays.append(j - onset)
                break
    return float(np.mean(delays)) if delays else 0.0


# ---------------------------------------------------------------------------
# Configuration registry (Section 2.3)
# ---------------------------------------------------------------------------

# Each entry is a dict describing how to run the configuration.
# Keys:
#   label       : human-readable name (for tables/figures)
#   filter_fn   : which filter function to call
#   filter_kwargs_factory : callable(x, L, alpha) -> dict of kwargs
#   shedding    : bool — whether load-shedding is applied
#   shed_max_skip : int — parameter for compute_processing_mask (ignored if not shedding)

CONFIGS = {
    "Fixed EMA": {
        "label": "Fixed EMA",
        "filter_fn": fixed_ema,
        "filter_kwargs_factory": lambda x, L, alpha=0.06: {"alpha": alpha},
        "shedding": False,
        "shed_max_skip": 4,
    },
    "Fixed EMA + Shedding": {
        "label": "Fixed EMA + Shedding",
        "filter_fn": fixed_ema,
        "filter_kwargs_factory": lambda x, L, alpha=0.06: {"alpha": alpha},
        "shedding": True,
        "shed_max_skip": 4,
    },
    "KAMA": {
        "label": "KAMA",
        "filter_fn": kama,
        "filter_kwargs_factory": lambda x, L: {},
        "shedding": False,
        "shed_max_skip": 4,
    },
    "Butterworth": {
        "label": "Butterworth",
        "filter_fn": butterworth_lowpass,
        "filter_kwargs_factory": lambda x, L: {},
        "shedding": False,
        "shed_max_skip": 4,
    },
    "Load-Adaptive EMA": {
        "label": "Load-Adaptive EMA",
        "filter_fn": load_adaptive_ema,
        "filter_kwargs_factory": lambda x, L: {"L": L},
        "shedding": False,
        "shed_max_skip": 4,
    },
    "Load-Adaptive EMA + Shedding": {
        "label": "Load-Adaptive EMA + Shedding",
        "filter_fn": load_adaptive_ema,
        "filter_kwargs_factory": lambda x, L: {"L": L},
        "shedding": True,
        "shed_max_skip": 4,
    },
}


def run_config(
    config_name: str,
    x: np.ndarray,
    L: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """
    Run a named configuration on signal x with backpressure L.

    Returns
    -------
    y             : Filtered output (full length, forward-filled where skipped).
    pole_traj     : Pole trajectory.
    process_mask  : Boolean mask (None if shedding is off).
    """
    cfg = CONFIGS[config_name]
    fn = cfg["filter_fn"]
    kwargs = cfg["filter_kwargs_factory"](x, L)

    if not cfg["shedding"]:
        y, pole_traj = fn(x, **kwargs)
        return y, pole_traj, None

    # Shedding path
    process_mask = compute_processing_mask(L, shed_max_skip=cfg["shed_max_skip"])
    y = np.empty(len(x))
    y, pole_traj = apply_shedding(y, x, process_mask, fn, kwargs)
    return y, pole_traj, process_mask
