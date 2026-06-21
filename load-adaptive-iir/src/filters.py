"""
filters.py — IIR filter implementations for the load-adaptive project.

All four filters now route their recursive step through Numba-JIT-compiled
kernels (see numba_filters.py) so timing comparisons are apples-to-apples
(no compiled-C vs Python-loop confound).

The *coefficient computation* logic (math) is unchanged from the original.
Only the recursive accumulation loop is delegated to the Numba kernels.
"""

import numpy as np
import scipy.signal

from src.numba_filters import (
    fixed_iir_direct_form_ii,
    time_varying_first_order_ema,
    compute_load_adaptive_alpha,
    compute_kama_sc,
)


def fixed_ema(x: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Fixed-pole Exponential Moving Average (first-order IIR low-pass filter).

    Spec §1.1:
        y[n] = alpha*x[n] + (1-alpha)*y[n-1]
        H(z)  = alpha / (1 - (1-alpha)*z⁻¹)
        Pole location: z_pole = 1 - alpha

    DC group delay derivation (§1.1):
        The impulse response is h[n] = alpha*(1-alpha)^n  for n >= 0.
        Group delay at DC is the mean of h[n]:
            tau_g(0) = sum_{n=0}^{inf} n * h[n]
                     = alpha * sum_{n=0}^{inf} n*(1-alpha)^n
                     = alpha * (1-alpha) / alpha^2          [geometric series identity]
                     = (1-alpha) / alpha
        Numerically verified against scipy.signal.group_delay at w→0 in tests/test_filters.py.

    Parameters:
    - x:     Input signal array.
    - alpha: Smoothing factor (0 < alpha < 1).

    Returns:
    - y:               Filtered signal array (same length as x).
    - pole_trajectory: Constant array of pole locations (1 - alpha) for every sample.
    """
    x = np.asarray(x, dtype=np.float64)
    n_samples = len(x)

    # Build a constant alpha trace and delegate to the Numba kernel.
    alpha_trace = np.full(n_samples, alpha, dtype=np.float64)
    y = time_varying_first_order_ema(x, alpha_trace)

    pole_trajectory = np.full(n_samples, 1.0 - alpha)
    return y, pole_trajectory


def load_adaptive_ema(
    x: np.ndarray,
    L: np.ndarray,
    alpha_min: float = 0.02,
    alpha_max: float = 0.30,
    d_alpha_max: float = 0.01
) -> tuple[np.ndarray, np.ndarray]:
    """
    Load-adaptive EMA.
    Section 1.2: alpha[n] = alpha_max - (alpha_max - alpha_min) * L[n]
    Section 1.3: Slew-rate limit |alpha[n] - alpha[n-1]| <= d_alpha_max

    Contrast with volatility-driven filters:
    This filter widens its effective window under high backpressure (lower alpha)
    to conserve downstream processing capacity, rather than speeding up under
    high signal activity like KAMA.
    """
    x = np.asarray(x, dtype=np.float64)
    L = np.asarray(L, dtype=np.float64)

    # --- Coefficient computation via JIT kernel (eliminates Python loop) ---
    alpha = compute_load_adaptive_alpha(
        L, alpha_min, alpha_max, d_alpha_max
    )

    # --- Recursive step via Numba kernel ---
    y = time_varying_first_order_ema(x, alpha)

    # Return pole trajectory directly from alpha to avoid floating-point
    # round-trip error (1 - (1 - alpha) ≠ alpha exactly in IEEE 754).
    pole_trajectory = 1.0 - alpha
    return y, pole_trajectory


def kama(
    x: np.ndarray,
    er_period: int = 10,
    fast_period: int = 2,
    slow_period: int = 30
) -> tuple[np.ndarray, np.ndarray]:
    """
    Kaufman's Adaptive Moving Average (KAMA).
    This is a signal-driven adaptive baseline (volatility/efficiency-driven),
    the conceptual contrast to the load-driven filter.
    """
    x = np.asarray(x, dtype=np.float64)
    fastSC = 2 / (fast_period + 1)
    slowSC = 2 / (slow_period + 1)

    sc_trajectory = compute_kama_sc(x, er_period, fastSC, slowSC)

    # Use sc as alpha_trace; initialise first er_period samples to slowSC
    # (matching original y[:er_period] = x[:er_period] initialisation).
    alpha_trace = sc_trajectory.copy()
    # Force the warm-up region to track input directly (alpha ≈ 1 for 1 step,
    # then follow KAMA).  We replicate: y[:er_period] = x[:er_period] by
    # temporarily setting alpha to 1 for those indices.
    alpha_trace[:er_period] = 1.0

    y = time_varying_first_order_ema(x, alpha_trace)

    pole_trajectory = 1 - sc_trajectory
    return y, pole_trajectory


def butterworth_lowpass(
    x: np.ndarray,
    order: int = 4,
    cutoff_hz: float = 1.0,
    fs: float = 100.0
) -> tuple[np.ndarray, np.ndarray]:
    """
    Butterworth low-pass filter via explicit bilinear transform.
    """
    x = np.asarray(x, dtype=np.float64)

    # 1. Analog prototype design
    omega_c = 2 * np.pi * cutoff_hz
    z_a, p_a, k_a = scipy.signal.butter(order, omega_c, btype='low', analog=True, output='zpk')

    # 2. Bilinear transform: s -> z substitution
    z_d, p_d, k_d = scipy.signal.bilinear_zpk(z_a, p_a, k_a, fs)

    # 3. Convert ZPK to transfer function polynomials (b, a)
    b, a = scipy.signal.zpk2tf(z_d, p_d, k_d)

    # 4. Filter via Numba kernel (Direct Form II Transposed)
    b_f = np.asarray(b, dtype=np.float64)
    a_f = np.asarray(a, dtype=np.float64)
    y = fixed_iir_direct_form_ii(x, b_f, a_f)

    # Trajectory of digital poles (constant for all n)
    n_samples = len(x)
    pole_trajectory = np.tile(p_d, (n_samples, 1))

    return y, pole_trajectory
