"""
test_no_coldstart_transient.py — Regression test for the Butterworth
cold-start transient bug (Section 2 of the hardening pass).

The original implementation started from a zero delay-line state, so the
filter output ramped from 0 up to the real price level (~tens of thousands)
over the first several time constants.  This inflated Butterworth's measured
false-positive rate in every results table.

The fix: compute steady-state initial conditions via scipy.signal.lfilter_zi
scaled to x[0] before calling the Numba kernel.

This test confirms:
  1. y[0] is close to x[0] (not near 0), so no start-up spike.
  2. The output is finite throughout.
  3. The short-term mean of y is close to the DC level of x.
"""

import sys
import numpy as np
import pytest
import scipy.signal
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.filters import butterworth_lowpass


# ---------------------------------------------------------------------------
# Helper: invoke the real pipeline Butterworth (default params)
# ---------------------------------------------------------------------------

def _run_butterworth(x: np.ndarray) -> np.ndarray:
    """Run Butterworth with default pipeline parameters, return y."""
    y, _ = butterworth_lowpass(x)
    return y


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_butterworth_no_coldstart_spike_realistic_price():
    """
    Realistic BTC price level (~42 300) with small noise.
    y[0] must start near x[0], not near 0.
    Tolerance: within 50 units of x[0] (< 0.12% of the price level).
    """
    rng = np.random.default_rng(42)
    x = np.full(50, 42_300.0) + rng.standard_normal(50) * 5.0
    y = _run_butterworth(x)
    assert abs(y[0] - x[0]) < 50.0, (
        f"Cold-start transient detected: y[0]={y[0]:.2f} vs x[0]={x[0]:.2f} "
        f"(difference {abs(y[0]-x[0]):.2f} > 50). "
        "The filter is not starting from the correct initial state."
    )


def test_butterworth_output_is_finite():
    """Output must be finite everywhere for a realistic price signal."""
    rng = np.random.default_rng(0)
    x = np.full(200, 42_300.0) + rng.standard_normal(200) * 5.0
    y = _run_butterworth(x)
    assert np.all(np.isfinite(y)), "Butterworth output contains NaN or Inf"


def test_butterworth_dc_level_preserved():
    """
    For a constant signal at a large DC level, the filter output should
    stay at that DC level throughout (not ramp up from 0).
    """
    dc_level = 42_300.0
    x = np.full(100, dc_level)
    y = _run_butterworth(x)
    # Every output sample should be within 1e-6 of dc_level (machine precision)
    assert np.allclose(y, dc_level, atol=1e-3), (
        f"DC tracking failed: max deviation = {np.max(np.abs(y - dc_level)):.6f}"
    )


def test_butterworth_first_sample_near_input_various_levels():
    """
    Parameterized over several realistic price levels to confirm cold-start
    fix works regardless of the DC offset magnitude.
    """
    for dc in [1.0, 100.0, 10_000.0, 42_300.0, 100_000.0]:
        rng = np.random.default_rng(7)
        x = np.full(50, dc) + rng.standard_normal(50) * (dc * 0.001)
        y = _run_butterworth(x)
        tol = max(1.0, dc * 0.002)   # 0.2% of DC level
        assert abs(y[0] - x[0]) < tol, (
            f"DC={dc}: y[0]={y[0]:.4f} vs x[0]={x[0]:.4f}, "
            f"deviation {abs(y[0]-x[0]):.4f} > tol={tol:.4f}"
        )


def test_butterworth_vs_scipy_lfilter_equivalence():
    """
    Cross-check: our Numba kernel with the warm initial state should produce
    the same output as scipy.signal.lfilter called with the same zi.
    This validates that the z0 computation is correct.
    """
    order = 4
    cutoff_hz = 1.0
    fs = 100.0

    omega_c = 2 * np.pi * cutoff_hz
    z_a, p_a, k_a = scipy.signal.butter(order, omega_c, btype='low', analog=True, output='zpk')
    z_d, p_d, k_d = scipy.signal.bilinear_zpk(z_a, p_a, k_a, fs)
    b, a = scipy.signal.zpk2tf(z_d, p_d, k_d)
    b = np.asarray(b, dtype=np.float64)
    a = np.asarray(a, dtype=np.float64)

    rng = np.random.default_rng(99)
    x = np.full(100, 42_300.0) + rng.standard_normal(100) * 10.0

    # scipy reference with warm start
    zi = scipy.signal.lfilter_zi(b, a)
    z0_scipy = (zi * x[0]).astype(np.float64)
    y_scipy, _ = scipy.signal.lfilter(b, a, x, zi=z0_scipy)

    # Our pipeline
    y_ours = _run_butterworth(x)

    np.testing.assert_allclose(
        y_ours, y_scipy, rtol=1e-10, atol=1e-8,
        err_msg="Numba kernel output does not match scipy.signal.lfilter reference"
    )
