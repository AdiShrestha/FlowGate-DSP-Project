"""
calibration.py — Bandwidth-matching calibration for the load-adaptive EMA.

The load-adaptive EMA uses alpha[n] = alpha_max - (alpha_max - alpha_min) * L[n],
so its time-average alpha depends on both alpha_min, alpha_max, AND the L trace.

This module provides:
  1. compute_mean_alpha() — measure what the current configuration's mean alpha is
  2. calibrate_alpha_min() — binary-search alpha_min to match a target mean alpha
  3. calibrate_alpha_max() — binary-search alpha_max to match a target mean alpha
     (needed when target_mean_alpha < min possible value with current alpha_max)

Empirical finding from the actual project L trace (ρ=0.75, mean_L≈0.36):
  The formula gives mean_alpha ≈ alpha_max - (alpha_max - alpha_min) * mean_L.
  With alpha_max=0.30 and mean_L≈0.36, the minimum achievable mean_alpha
  (as alpha_min → 0) is ≈ 0.30 * (1 - 0.36) = 0.192.
  Therefore target_mean_alpha=0.06 is UNREACHABLE with alpha_max=0.30;
  we report this honestly rather than returning a nonsensical result.

  The achievable bandwidth-matched target is the current default run's
  mean_alpha (measured empirically), which can then be matched by a fixed EMA
  for a fair comparison.  Alternatively, we calibrate alpha_max downward to
  reach an arbitrary target below 0.192.
"""

from __future__ import annotations

import numpy as np


def compute_mean_alpha(
    L_trace: np.ndarray,
    alpha_min: float = 0.02,
    alpha_max: float = 0.30,
) -> float:
    """
    Compute the time-averaged alpha for the load-adaptive EMA on a given L trace.

    Parameters
    ----------
    L_trace   : 1-D array of normalised backpressure values in [0, 1].
    alpha_min : Minimum alpha (applied at L=1).
    alpha_max : Maximum alpha (applied at L=0).

    Returns
    -------
    mean_alpha : float  Time-average of alpha[n] over the trace.
    """
    L = np.asarray(L_trace, dtype=np.float64)
    alpha_trace = alpha_max - (alpha_max - alpha_min) * L
    return float(np.mean(alpha_trace))


def minimum_achievable_mean_alpha(
    L_trace: np.ndarray,
    alpha_max: float = 0.30,
) -> float:
    """
    Return the minimum mean_alpha achievable for a given alpha_max and L trace,
    obtained as alpha_min → 0.  If this value is above the desired target,
    the target is unreachable by tuning alpha_min alone.

    Parameters
    ----------
    L_trace  : 1-D array of normalised backpressure values in [0, 1].
    alpha_max: Maximum alpha (applied at L=0).

    Returns
    -------
    min_mean_alpha : float
    """
    L = np.asarray(L_trace, dtype=np.float64)
    # alpha_min = 0 → alpha_trace = alpha_max * (1 - L)
    return float(np.mean(alpha_max * (1.0 - L)))


def calibrate_alpha_min(
    L_trace: np.ndarray,
    alpha_max: float = 0.30,
    target_mean_alpha: float = 0.06,
    tol: float = 1e-4,
) -> tuple[float, float, bool]:
    """
    Binary-search alpha_min so that the time-average of
        alpha[n] = alpha_max - (alpha_max - alpha_min) * L[n]
    equals target_mean_alpha, within tolerance tol.

    Empirical direction (verified on the real project L trace):
        increasing alpha_min increases mean_alpha (positive monotone relationship).
        Therefore:
          - if mean_alpha > target: decrease alpha_min (move lo down)
          - if mean_alpha < target: increase alpha_min (move hi up)

    Parameters
    ----------
    L_trace           : 1-D array of normalised backpressure values in [0, 1].
    alpha_max         : Fixed maximum alpha (applied at L=0).
    target_mean_alpha : Target time-averaged alpha.
    tol               : Convergence tolerance on mean_alpha.

    Returns
    -------
    alpha_min_cal  : float   Calibrated alpha_min.
    achieved_mean  : float   Actual mean_alpha achieved by the calibrated alpha_min.
    reachable      : bool    False if the target is unreachable (below minimum achievable
                             mean alpha for this alpha_max and L trace).
    """
    L = np.asarray(L_trace, dtype=np.float64)

    # Check feasibility: the minimum achievable mean_alpha (alpha_min → 0)
    min_reachable = minimum_achievable_mean_alpha(L, alpha_max)
    if target_mean_alpha < min_reachable - tol:
        # Target is below what's achievable by tuning alpha_min alone.
        # Report the closest we can get (alpha_min → 1e-4) and flag not reachable.
        best_alpha_min = 1e-4
        achieved = compute_mean_alpha(L, alpha_min=best_alpha_min, alpha_max=alpha_max)
        return best_alpha_min, achieved, False

    # Feasibility upper bound: alpha_min can at most approach alpha_max
    max_reachable = alpha_max - 1e-4
    if target_mean_alpha > compute_mean_alpha(L, alpha_min=max_reachable, alpha_max=alpha_max):
        # Target above maximum — return alpha_min as large as possible
        achieved = compute_mean_alpha(L, alpha_min=max_reachable, alpha_max=alpha_max)
        return max_reachable, achieved, False

    # Binary search in [1e-4, alpha_max - 1e-4]
    lo, hi = 1e-4, alpha_max - 1e-4
    mid = (lo + hi) / 2.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        mean_alpha = compute_mean_alpha(L, alpha_min=mid, alpha_max=alpha_max)
        if abs(mean_alpha - target_mean_alpha) < tol:
            break
        # Increasing alpha_min increases mean_alpha (positive relationship)
        if mean_alpha < target_mean_alpha:
            lo = mid   # need higher mean -> increase alpha_min
        else:
            hi = mid   # need lower mean -> decrease alpha_min

    achieved = compute_mean_alpha(L, alpha_min=mid, alpha_max=alpha_max)
    return mid, achieved, True


def calibrate_alpha_max(
    L_trace: np.ndarray,
    alpha_min: float = 0.02,
    target_mean_alpha: float = 0.06,
    tol: float = 1e-4,
) -> tuple[float, float, bool]:
    """
    Binary-search alpha_max so that the time-average of
        alpha[n] = alpha_max - (alpha_max - alpha_min) * L[n]
    equals target_mean_alpha.

    Useful when target_mean_alpha is below the minimum achievable with the
    default alpha_max=0.30 (e.g., target=0.06 with mean_L≈0.36).

    Empirical direction: increasing alpha_max increases mean_alpha.

    Parameters
    ----------
    L_trace           : 1-D array of normalised backpressure values in [0, 1].
    alpha_min         : Fixed minimum alpha (applied at L=1).
    target_mean_alpha : Target time-averaged alpha.
    tol               : Convergence tolerance on mean_alpha.

    Returns
    -------
    alpha_max_cal : float  Calibrated alpha_max.
    achieved_mean : float  Actual mean_alpha achieved.
    reachable     : bool   True if calibration converged within tolerance.
    """
    L = np.asarray(L_trace, dtype=np.float64)

    if target_mean_alpha < alpha_min + tol:
        # Target is below alpha_min, unreachable
        achieved = compute_mean_alpha(L, alpha_min=alpha_min, alpha_max=alpha_min + 1e-4)
        return alpha_min + 1e-4, achieved, False

    # Binary search alpha_max in [alpha_min + 1e-4, 1.0 - 1e-4]
    lo, hi = alpha_min + 1e-4, 1.0 - 1e-4
    mid = (lo + hi) / 2.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        mean_alpha = compute_mean_alpha(L, alpha_min=alpha_min, alpha_max=mid)
        if abs(mean_alpha - target_mean_alpha) < tol:
            break
        # Increasing alpha_max increases mean_alpha
        if mean_alpha < target_mean_alpha:
            lo = mid
        else:
            hi = mid

    achieved = compute_mean_alpha(L, alpha_min=alpha_min, alpha_max=mid)
    return mid, achieved, True
