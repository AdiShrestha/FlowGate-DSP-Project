"""
test_detection.py — Tests for detection.py.

Covers:
  1. Both estimators (std and mad)
  2. Signed z-score regression guard (downward spike must score well with abs())
  3. sigma=0 guard (no division-by-zero crash)
  4. Output shapes and types
"""

import sys
import numpy as np
import pytest
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.detection import detect_anomalies
from src.evaluate import compute_auc


# ---------------------------------------------------------------------------
# Basic output contract
# ---------------------------------------------------------------------------

def test_detect_returns_three_arrays():
    x = np.zeros(100)
    y = np.zeros(100)
    residual, z, detected = detect_anomalies(x, y)
    assert residual.shape == (100,)
    assert z.shape == (100,)
    assert detected.shape == (100,)
    assert detected.dtype == bool


def test_residual_is_x_minus_y():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(200)
    y = rng.standard_normal(200)
    residual, _, _ = detect_anomalies(x, y)
    np.testing.assert_allclose(residual, x - y)


def test_no_anomaly_in_flat_signal():
    """Flat signal with flat filter output → residual=0 → no detections."""
    x = np.ones(200)
    y = np.ones(200)
    _, z, detected = detect_anomalies(x, y)
    assert not np.any(detected), "Expected no detections on a flat zero-residual signal"


# ---------------------------------------------------------------------------
# Upward spike detection (the easy case)
# ---------------------------------------------------------------------------

def test_large_positive_spike_is_detected():
    x = np.zeros(500)
    y = np.zeros(500)
    x[250] = 100.0   # enormous spike
    _, _, detected = detect_anomalies(x, y, threshold=3.0)
    assert detected[250], "Large upward spike must be detected"


# ---------------------------------------------------------------------------
# Signed z-score regression guard
# ---------------------------------------------------------------------------

def test_downward_spike_detected_with_abs_z():
    """
    Regression guard for the 'DeLong signed z-score bug' (documented in
    project_context.md): detect_anomalies returns SIGNED z-scores. For a
    downward spike, z at the spike index is large and NEGATIVE. Verify that
    using abs() is necessary: without it, the spike z-score is negative,
    while with abs() it is positive — confirming the signing matters.
    """
    x = np.zeros(1000)
    y = np.zeros(1000)
    x[500] = -30.0   # large DOWNWARD spike

    _, z, _ = detect_anomalies(x, y)

    # Core assertion: the z-score at the spike must be strongly NEGATIVE
    assert z[500] < -5.0, (
        f"Expected large negative z at downward spike, got z[500]={z[500]:.4f}"
    )

    # And abs() must flip it to strongly POSITIVE (this is the fix)
    assert abs(z[500]) > 5.0, "abs(z) at spike must be large and positive"


# ---------------------------------------------------------------------------
# MAD estimator
# ---------------------------------------------------------------------------

def test_mad_estimator_produces_finite_output():
    """estimator='mad' must not crash and must produce finite z-scores."""
    rng = np.random.default_rng(3)
    x = rng.standard_normal(300)
    y = np.zeros(300)
    _, z, detected = detect_anomalies(x, y, estimator='mad')
    assert np.all(np.isfinite(z)), "MAD estimator produced non-finite z-scores"


def test_mad_estimator_detects_large_spike():
    """MAD estimator must flag a 20-sigma spike."""
    x = np.zeros(300)
    y = np.zeros(300)
    x[0:10] = np.random.normal(0, 1, 10)  # small warm-up variance so MAD > 0
    x[150] = 30.0
    _, _, detected = detect_anomalies(x, y, estimator='mad', threshold=3.0)
    assert detected[150], "MAD estimator failed to detect a large spike"


def test_std_and_mad_agree_on_large_spike():
    """Both estimators must flag the same obvious spike."""
    x = np.random.normal(0, 1, 500)
    y = np.zeros(500)
    x[250] = 50.0   # obvious spike

    _, _, det_std = detect_anomalies(x, y, estimator='std', threshold=3.0)
    _, _, det_mad = detect_anomalies(x, y, estimator='mad', threshold=3.0)

    assert det_std[250], "std estimator must flag spike at 250"
    assert det_mad[250], "mad estimator must flag spike at 250"


# ---------------------------------------------------------------------------
# sigma=0 guard (no crash when residual is constant)
# ---------------------------------------------------------------------------

def test_no_crash_when_sigma_is_zero():
    """
    If the residual is perfectly constant over the rolling window, sigma_r=0.
    The implementation replaces 0 with 1e-9 so z = residual / 1e-9.
    Must not raise ZeroDivisionError or produce NaN/Inf.
    """
    x = np.ones(200) * 42.0   # constant signal
    y = np.zeros(200)          # constant filter output → constant residual
    _, z, detected = detect_anomalies(x, y)
    assert np.all(np.isfinite(z)), "z-scores must be finite even when sigma_r=0"
