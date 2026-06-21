"""
test_numba_parity.py — Section 1 validation requirement.

For each of the four filters, compares the Numba-kernel output against the
*original* (pre-refactor) implementation on the same input and asserts
np.allclose(old_output, new_output, atol=1e-9).

The original implementations are inlined below (copied verbatim from the
pre-refactor filters.py) so this test file is self-contained and does not
depend on having the old file on disk.

These tests MUST pass before any benchmarking runs. In run_all.py the
--with-compute-experiments path calls pytest on this file as a hard gate.
"""

import numpy as np
import pytest
import scipy.signal
import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.numba_filters import fixed_iir_direct_form_ii, time_varying_first_order_ema
from src.filters import fixed_ema, load_adaptive_ema, kama, butterworth_lowpass


# ---------------------------------------------------------------------------
# Reference implementations (verbatim pre-refactor logic)
# ---------------------------------------------------------------------------

def _ref_fixed_ema(x, alpha):
    x = np.asarray(x)
    n_samples = len(x)
    y = np.zeros(n_samples)
    y[0] = x[0]
    for n in range(1, n_samples):
        y[n] = alpha * x[n] + (1 - alpha) * y[n - 1]
    pole_trajectory = np.full(n_samples, 1 - alpha)
    return y, pole_trajectory


def _ref_load_adaptive_ema(x, L, alpha_min=0.02, alpha_max=0.30, d_alpha_max=0.01):
    x = np.asarray(x)
    L = np.asarray(L)
    n_samples = len(x)
    alpha = np.zeros(n_samples)
    a_init = alpha_max - (alpha_max - alpha_min) * L[0]
    alpha[0] = np.clip(a_init, 1e-4, 1 - 1e-4)
    for n in range(1, n_samples):
        target_a = alpha_max - (alpha_max - alpha_min) * L[n]
        diff = target_a - alpha[n - 1]
        diff = np.clip(diff, -d_alpha_max, d_alpha_max)
        alpha[n] = np.clip(alpha[n - 1] + diff, 1e-4, 1 - 1e-4)
    y = np.zeros(n_samples)
    y[0] = x[0]
    for n in range(1, n_samples):
        y[n] = alpha[n] * x[n] + (1 - alpha[n]) * y[n - 1]
    pole_trajectory = 1.0 - alpha
    return y, pole_trajectory


def _ref_kama(x, er_period=10, fast_period=2, slow_period=30):
    x = np.asarray(x)
    n_samples = len(x)
    y = np.zeros(n_samples)
    sc_trajectory = np.zeros(n_samples)
    fastSC = 2 / (fast_period + 1)
    slowSC = 2 / (slow_period + 1)
    y[:er_period] = x[:er_period]
    sc_trajectory[:er_period] = slowSC
    change = np.abs(np.diff(x, prepend=x[0]))
    for n in range(er_period, n_samples):
        dir_change = abs(x[n] - x[n - er_period])
        volatility = np.sum(change[n - er_period + 1: n + 1])
        er = dir_change / volatility if volatility != 0 else 0
        sc = (er * (fastSC - slowSC) + slowSC) ** 2
        sc_trajectory[n] = sc
        y[n] = y[n - 1] + sc * (x[n] - y[n - 1])
    pole_trajectory = 1 - sc_trajectory
    return y, pole_trajectory


def _ref_butterworth_lowpass(x, order=4, cutoff_hz=1.0, fs=100.0):
    x = np.asarray(x, dtype=np.float64)
    omega_c = 2 * np.pi * cutoff_hz
    z_a, p_a, k_a = scipy.signal.butter(order, omega_c, btype='low', analog=True, output='zpk')
    z_d, p_d, k_d = scipy.signal.bilinear_zpk(z_a, p_a, k_a, fs)
    b, a = scipy.signal.zpk2tf(z_d, p_d, k_d)
    b = np.asarray(b, dtype=np.float64)
    a = np.asarray(a, dtype=np.float64)
    # Use warm initial state to match the fixed pipeline (cold-start fix).
    zi = scipy.signal.lfilter_zi(b, a)
    z0 = (zi * x[0]).astype(np.float64)
    y, _ = scipy.signal.lfilter(b, a, x, zi=z0)
    n_samples = len(x)
    pole_trajectory = np.tile(p_d, (n_samples, 1))
    return y, pole_trajectory


# ---------------------------------------------------------------------------
# Shared test signal
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def test_signal():
    np.random.seed(42)
    n = 5000
    t = np.linspace(0, 50, n)
    x = (
        np.sin(2 * np.pi * 0.1 * t)
        + 0.5 * np.sin(2 * np.pi * 1.5 * t)
        + np.random.normal(0, 0.3, n)
    )
    return x.astype(np.float64)


@pytest.fixture(scope="module")
def load_signal():
    np.random.seed(7)
    n = 5000
    L = np.clip(np.cumsum(np.random.normal(0, 0.02, n)), 0, 1)
    L = np.abs(np.sin(np.linspace(0, 6 * np.pi, n))) * 0.8
    return L.astype(np.float64)


# ---------------------------------------------------------------------------
# Parity tests
# ---------------------------------------------------------------------------

def test_fixed_ema_numba_parity(test_signal):
    """Numba Fixed EMA must match reference Python loop within atol=1e-9."""
    alpha = 0.06
    y_ref, _ = _ref_fixed_ema(test_signal, alpha)
    y_new, _ = fixed_ema(test_signal, alpha)
    assert np.allclose(y_ref, y_new, atol=1e-9), (
        f"Fixed EMA parity failed. Max diff = {np.max(np.abs(y_ref - y_new)):.2e}"
    )


def test_load_adaptive_ema_numba_parity(test_signal, load_signal):
    """Numba Load-Adaptive EMA must match reference Python loop within atol=1e-9."""
    y_ref, _ = _ref_load_adaptive_ema(test_signal, load_signal)
    y_new, _ = load_adaptive_ema(test_signal, load_signal)
    assert np.allclose(y_ref, y_new, atol=1e-9), (
        f"Load-Adaptive EMA parity failed. Max diff = {np.max(np.abs(y_ref - y_new)):.2e}"
    )


def test_kama_numba_parity(test_signal):
    """Numba KAMA must match reference Python loop within atol=1e-9."""
    y_ref, _ = _ref_kama(test_signal)
    y_new, _ = kama(test_signal)
    assert np.allclose(y_ref, y_new, atol=1e-9), (
        f"KAMA parity failed. Max diff = {np.max(np.abs(y_ref - y_new)):.2e}"
    )


def test_butterworth_numba_parity(test_signal):
    """
    Numba Butterworth must match scipy.signal.lfilter within atol=1e-9.
    Both now use the same warm initial state (lfilter_zi * x[0]) to align
    with the cold-start fix (Section 2 of the hardening pass).
    """
    y_ref, _ = _ref_butterworth_lowpass(test_signal)
    y_new, _ = butterworth_lowpass(test_signal)
    assert np.allclose(y_ref, y_new, atol=1e-9), (
        f"Butterworth parity failed. Max diff = {np.max(np.abs(y_ref - y_new)):.2e}"
    )


def test_all_four_filters_produce_finite_output(test_signal, load_signal):
    """All four Numba-backed filters must produce finite outputs."""
    for name, fn, kwargs in [
        ("Fixed EMA",         fixed_ema,            {"alpha": 0.06}),
        ("Load-Adaptive EMA", load_adaptive_ema,    {"L": load_signal}),
        ("KAMA",              kama,                  {}),
        ("Butterworth",       butterworth_lowpass,   {}),
    ]:
        y, _ = fn(test_signal, **kwargs)
        assert np.all(np.isfinite(y)), f"{name} produced non-finite values."
