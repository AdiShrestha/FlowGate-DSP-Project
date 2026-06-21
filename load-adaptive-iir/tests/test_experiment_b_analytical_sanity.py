"""
test_experiment_b_analytical_sanity.py — Regression test for Experiment B
(Section 4.1 of the hardening pass).

The original bug was comparing nanosecond-scale JIT arithmetic against
second-scale arrival rates — a ~7-8 order of magnitude unit mismatch that
made every configuration appear stable at any arrival rate.

This test constructs synthetic configurations with KNOWN service times
and verifies that compute_max_stable_lambda returns a value within 5%
of the analytical prediction (1/service_time_s).  Any future regression
of the same shape would be caught immediately.
"""

import sys
import numpy as np
import pytest
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import stability internals directly from Experiment B
from src.experiment_b_throughput_stability import _is_stable, _simulate_queue_depth


# ---------------------------------------------------------------------------
# Helper: compute max stable lambda from a known service time
# ---------------------------------------------------------------------------

def compute_max_stable_lambda(service_time_s: float, n_sweep: int = 100) -> float:
    """
    Given a known per-event service time in seconds, sweep lambda from
    0.1 × mu to 2 × mu (log-spaced) and return the highest lambda for
    which _is_stable() returns True.

    Uses the same _is_stable() logic as Experiment B so this is a direct
    regression guard on that function's behaviour.

    Parameters
    ----------
    service_time_s : float   Per-event service time in seconds.
    n_sweep        : int     Number of lambda values to sweep.

    Returns
    -------
    max_stable_lam : float   Highest lambda at which the system is stable.
    """
    mu = 1.0 / service_time_s
    lam_sweep = np.logspace(np.log10(mu * 0.1), np.log10(mu * 2.0), n_sweep)

    max_stable = lam_sweep[0]
    for lam in lam_sweep:
        stable, _, _ = _is_stable(lam, mu)
        if stable:
            max_stable = lam

    return max_stable


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_max_stable_lambda_matches_analytical_prediction_10us():
    """
    service_time = 10 μs/event → μ = 100,000 events/s.
    Max stable λ must be within 5% of 100,000.
    """
    synthetic_service_time_s = 10e-6
    result = compute_max_stable_lambda(service_time_s=synthetic_service_time_s)
    expected = 1.0 / synthetic_service_time_s   # 100,000 events/s
    rel_error = abs(result - expected) / expected
    assert rel_error < 0.05, (
        f"Max stable lambda {result:.1f} is more than 5% away from analytical "
        f"prediction {expected:.1f} (relative error {rel_error:.3f}). "
        "This is the symptom of the unit-mismatch bug (ns vs s)."
    )


def test_max_stable_lambda_matches_analytical_prediction_1ms():
    """
    service_time = 1 ms/event → μ = 1,000 events/s.
    Max stable λ must be within 5% of 1,000.
    """
    synthetic_service_time_s = 1e-3
    result = compute_max_stable_lambda(service_time_s=synthetic_service_time_s)
    expected = 1.0 / synthetic_service_time_s   # 1,000 events/s
    rel_error = abs(result - expected) / expected
    assert rel_error < 0.05, (
        f"Max stable lambda {result:.1f} vs expected {expected:.1f} "
        f"(relative error {rel_error:.3f})"
    )


def test_max_stable_lambda_matches_analytical_prediction_5us():
    """
    service_time = 5 μs/event → μ = 200,000 events/s (realistic for a JIT filter
    with 5 μs downstream overhead as used by the actual pipeline).
    """
    synthetic_service_time_s = 5e-6
    result = compute_max_stable_lambda(service_time_s=synthetic_service_time_s)
    expected = 1.0 / synthetic_service_time_s   # 200,000 events/s
    rel_error = abs(result - expected) / expected
    assert rel_error < 0.05, (
        f"Max stable lambda {result:.1f} vs expected {expected:.1f} "
        f"(relative error {rel_error:.3f})"
    )


def test_stability_check_unit_consistency():
    """
    Guard against the unit-mismatch bug: the breaking point must change
    proportionally when we change the service time by 10×.
    If the function confused ns for s, the breaking points would be
    identical regardless of the service time ratio.
    """
    mu_10us = 1.0 / 10e-6    # 100,000 events/s
    mu_100us = 1.0 / 100e-6  #  10,000 events/s

    max_lam_fast = compute_max_stable_lambda(service_time_s=10e-6)
    max_lam_slow = compute_max_stable_lambda(service_time_s=100e-6)

    # Should differ by approximately 10×
    ratio = max_lam_fast / max_lam_slow
    assert 7.0 < ratio < 13.0, (
        f"Expected max_stable_lambda ratio ≈ 10× for 10× service time difference; "
        f"got {ratio:.2f} (fast={max_lam_fast:.1f}, slow={max_lam_slow:.1f}). "
        "If ratio ≈ 1.0, this is the unit-confusion bug."
    )


def test_is_stable_basic_sanity_with_realistic_mu():
    """
    Direct call to _is_stable() with realistic Experiment-B-scale values.
    With μ = 200,000 and λ = 100,000 (ρ=0.5), must be stable.
    With μ = 200,000 and λ = 300,000 (ρ=1.5), must be unstable.
    """
    mu_eff = 200_000.0

    stable_low, rho_low, _ = _is_stable(100_000.0, mu_eff)
    assert stable_low, f"Expected STABLE at ρ={rho_low:.2f}, got unstable"
    assert abs(rho_low - 0.5) < 1e-6

    stable_high, rho_high, _ = _is_stable(300_000.0, mu_eff)
    assert not stable_high, f"Expected UNSTABLE at ρ={rho_high:.2f}, got stable"
    assert abs(rho_high - 1.5) < 1e-6
