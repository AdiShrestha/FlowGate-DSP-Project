import numpy as np
import pytest
import scipy.signal
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.filters import fixed_ema, load_adaptive_ema, kama, butterworth_lowpass

def test_fixed_ema_constant_convergence():
    x = np.ones(100) * 5.0
    y, _ = fixed_ema(x, alpha=0.1)
    assert np.isclose(y[-1], 5.0)

def test_fixed_ema_pole_location():
    alpha = 0.3
    x = np.zeros(10)
    _, pole = fixed_ema(x, alpha)
    assert np.allclose(pole, 1 - alpha)

def test_load_adaptive_ema_bounds():
    x = np.ones(100)
    # Adversarial L — fixed seed so the test is deterministic
    np.random.seed(0)
    L = np.random.uniform(-2, 3, 100)
    L[10:20] = 0
    L[30:40] = 1

    y, pole = load_adaptive_ema(x, L, alpha_min=0.02, alpha_max=0.30, d_alpha_max=0.01)
    alpha_trace = 1 - pole

    # Allow 1 ULP of floating-point slack (1e-9 << 1e-4) — the clip guarantees
    # alpha ∈ [1e-4, 1-1e-4] internally; the 1-(1-alpha) round-trip can shift by ~1e-16.
    tol = 1e-9
    assert np.all(alpha_trace >= 1e-4 - tol), f"Min alpha = {alpha_trace.min()}"
    assert np.all(alpha_trace <= 1 - 1e-4 + tol), f"Max alpha = {alpha_trace.max()}"


def test_load_adaptive_ema_slew_rate():
    x = np.ones(100)
    # Oscillating L to trigger max slew rate
    L = np.tile([0.0, 1.0], 50)
    d_alpha_max = 0.01
    
    y, pole = load_adaptive_ema(x, L, d_alpha_max=d_alpha_max)
    alpha_trace = 1 - pole
    
    diffs = np.abs(np.diff(alpha_trace))
    assert np.max(diffs) <= d_alpha_max + 1e-9

def test_fixed_ema_group_delay():
    # Section 1.1 numerically verify DC group delay against scipy.signal.group_delay
    alphas = [0.05, 0.1, 0.3]
    for alpha in alphas:
        b = [alpha]
        a = [1, -(1 - alpha)]
        w, gd = scipy.signal.group_delay((b, a), w=[1e-5], fs=1.0)
        expected = (1 - alpha) / alpha
        assert np.isclose(gd[0], expected, rtol=0.01)

def test_kama_and_butterworth_finite_output():
    np.random.seed(42)
    t = np.linspace(0, 10, 500)
    x = np.sin(2 * np.pi * 1.0 * t) + np.random.normal(0, 0.1, len(t))
    
    y_kama, _ = kama(x)
    assert np.all(np.isfinite(y_kama))
    
    y_butter, _ = butterworth_lowpass(x)
    assert np.all(np.isfinite(y_butter))
