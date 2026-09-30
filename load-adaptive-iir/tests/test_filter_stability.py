"""
test_filter_stability.py — Stability and adversarial tests for filters.py.

Covers the gap identified in the gap analysis: no test verifies that the
load-adaptive filter stays finite/bounded when alpha oscillates at the
maximum slew rate near the stability boundary.
"""

import sys
import numpy as np
import pytest
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.filters import load_adaptive_ema, fixed_ema


# ---------------------------------------------------------------------------
# Stability under adversarial L (full slew-rate oscillation)
# ---------------------------------------------------------------------------

def test_load_adaptive_ema_stable_under_full_oscillation():
    """
    Output must stay finite and bounded when L oscillates maximally (0→1→0...),
    driving alpha between alpha_min and alpha_max at every step.
    This verifies the filter does not diverge near the stability boundary.
    """
    n = 5_000   # small enough not to stress RAM
    x = np.ones(n) * 100.0
    L = np.tile([0.0, 1.0], n // 2)  # max oscillation
    y, _ = load_adaptive_ema(x, L, alpha_min=1e-4, alpha_max=0.99, d_alpha_max=0.01)
    assert np.all(np.isfinite(y)), "Filter diverged under full oscillation"
    assert np.all(np.abs(y) < 1e9), f"Filter output exploded: max={np.max(np.abs(y)):.2e}"


def test_load_adaptive_ema_stable_with_step_input():
    """
    A large step change in the input (DC offset) must not destabilize the filter.
    """
    n = 2_000
    x = np.concatenate([np.zeros(n // 2), np.ones(n // 2) * 1e6])
    L = np.random.default_rng(5).uniform(0, 1, n)
    y, _ = load_adaptive_ema(x, L)
    assert np.all(np.isfinite(y))


def test_load_adaptive_ema_stable_with_noisy_price():
    """Realistic noisy price input must not cause filter divergence."""
    rng = np.random.default_rng(42)
    n = 3_000
    x = 42_000.0 + np.cumsum(rng.standard_normal(n) * 5.0)
    L = np.abs(np.sin(np.linspace(0, 4 * np.pi, n)))  # smooth load cycle
    y, _ = load_adaptive_ema(x, L)
    assert np.all(np.isfinite(y))
    # Output must track within a reasonable range of input DC level
    assert np.all(np.abs(y - 42_000.0) < 5_000.0), "Filter drifted too far from DC level"


# ---------------------------------------------------------------------------
# Fixed EMA stability (baseline sanity)
# ---------------------------------------------------------------------------

def test_fixed_ema_stable_under_large_input():
    """Fixed EMA must stay bounded for a large-amplitude sinusoidal input."""
    n = 2_000
    t = np.linspace(0, 20, n)
    x = 1e8 * np.sin(2 * np.pi * 0.5 * t)
    y, _ = fixed_ema(x, alpha=0.1)
    assert np.all(np.isfinite(y))
    assert np.max(np.abs(y)) <= np.max(np.abs(x)) + 1.0  # stable filter can't amplify


# ---------------------------------------------------------------------------
# Alpha trace validity (guard for regression)
# ---------------------------------------------------------------------------

def test_pole_trajectory_strictly_inside_unit_circle():
    """
    Pole = 1 - alpha must always be in (-1, 1) exclusive for all alpha values.
    Checks the full pole trajectory under adversarial L.
    """
    n = 2_000
    x = np.ones(n)
    L = np.tile([0.0, 1.0], n // 2)
    _, pole = load_adaptive_ema(x, L, alpha_min=1e-4, alpha_max=0.9999, d_alpha_max=0.05)
    assert np.all(pole > -1.0), f"Pole went below -1: min={pole.min():.6f}"
    assert np.all(pole < 1.0),  f"Pole hit or exceeded 1: max={pole.max():.6f}"
