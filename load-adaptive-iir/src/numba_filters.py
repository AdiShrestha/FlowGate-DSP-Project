"""
numba_filters.py — Numba-JIT-compiled IIR filter kernels.

All four filters (Fixed EMA, Load-Adaptive EMA, KAMA, Butterworth) are routed
through these kernels so every timing comparison in Experiments A/B is
apples-to-apples (no compiled-C vs Python-loop confound).

Warm-up is performed at module import time so JIT compilation latency is never
counted as algorithmic cost in any timed region.
"""

import numpy as np
from numba import njit


# ---------------------------------------------------------------------------
# Kernel 1: Fixed-coefficient Direct Form II Transposed IIR
# ---------------------------------------------------------------------------

@njit(cache=True)
def fixed_iir_direct_form_ii(x: np.ndarray, b: np.ndarray, a: np.ndarray) -> np.ndarray:
    """
    Generic fixed-coefficient Direct Form II Transposed IIR filter.

    Matches scipy.signal.lfilter's algorithm exactly (a[0] assumed 1.0;
    normalise b, a by a[0] before calling if necessary).

    Used for: Butterworth (any order), and as a validation path for Fixed EMA.

    Parameters
    ----------
    x : 1-D float64 array   Input signal.
    b : 1-D float64 array   Numerator coefficients.
    a : 1-D float64 array   Denominator coefficients (a[0] == 1.0).

    Returns
    -------
    y : 1-D float64 array   Filtered output, same length as x.
    """
    order = max(len(a), len(b)) - 1
    z = np.zeros(order)
    y = np.empty(len(x))

    # Zero-pad to length order+1
    b_pad = np.zeros(order + 1)
    a_pad = np.zeros(order + 1)
    for i in range(len(b)):
        b_pad[i] = b[i]
    for i in range(len(a)):
        a_pad[i] = a[i]

    for n in range(len(x)):
        y[n] = b_pad[0] * x[n] + (z[0] if order > 0 else 0.0)
        for i in range(order - 1):
            z[i] = b_pad[i + 1] * x[n] + z[i + 1] - a_pad[i + 1] * y[n]
        if order > 0:
            z[order - 1] = b_pad[order] * x[n] - a_pad[order] * y[n]

    return y


# ---------------------------------------------------------------------------
# Kernel 2: Time-varying first-order EMA
# ---------------------------------------------------------------------------

@njit(cache=True)
def time_varying_first_order_ema(x: np.ndarray, alpha_trace: np.ndarray) -> np.ndarray:
    """
    First-order IIR with a per-sample, precomputed alpha[n].

    Used for: Fixed EMA (constant alpha_trace), KAMA (sc_trajectory as alpha),
    and Load-Adaptive EMA (slew-rate-limited alpha_trace).

    Only the unavoidable recursive accumulation runs inside the njit loop;
    all vectorisable coefficient computation is done outside before calling.

    Parameters
    ----------
    x           : 1-D float64 array   Input signal.
    alpha_trace : 1-D float64 array   Per-sample smoothing factor, same length as x.

    Returns
    -------
    y : 1-D float64 array   Filtered output, same length as x.
    """
    n = len(x)
    y = np.empty(n)
    y[0] = x[0]
    for i in range(1, n):
        a = alpha_trace[i]
        y[i] = a * x[i] + (1.0 - a) * y[i - 1]
    return y


# ---------------------------------------------------------------------------
# Module-level warm-up — runs once at import time so JIT compile cost is
# never inside a timed region.
# ---------------------------------------------------------------------------

def _warmup():
    _dummy = np.zeros(16, dtype=np.float64)
    _b = np.array([0.1], dtype=np.float64)
    _a = np.array([1.0, -0.9], dtype=np.float64)
    fixed_iir_direct_form_ii(_dummy, _b, _a)

    _alpha = np.full(16, 0.1, dtype=np.float64)
    time_varying_first_order_ema(_dummy, _alpha)


_warmup()
