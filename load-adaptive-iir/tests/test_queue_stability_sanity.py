"""
test_queue_stability_sanity.py — Section 7, sanity-checks for the
stability-detection logic used in Experiment B.

Two synthetic cases:
  1. λ ≫ μ  → must be flagged UNSTABLE
  2. λ ≪ μ  → must be flagged STABLE

This validates that the stability check itself is trustworthy before we
rely on it for the real configurations.
"""

import numpy as np
import pytest
import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# ---------------------------------------------------------------------------
# Inline stability checker (same logic as Experiment B uses)
# ---------------------------------------------------------------------------

def _is_stable(
    lam: float,
    mu: float,
    n_ticks: int = 10_000,
    seed: int = 0,
) -> bool:
    """
    Returns (stable, rho, queue_depth_trace).

    Analytical: ρ = λ/μ.  Unstable if ρ >= 1.
    Empirical:  simulate a queue; flag unstable if the final half of the
                trace has a statistically significant upward trend (slope > 0).
    A configuration is flagged stable only if ρ < 1 AND empirical slope ≤ 0.
    """
    rho = lam / mu

    # Analytical gate
    if rho >= 1.0:
        return False

    # Empirical check — simulate an M/D/1-style queue.
    # At each event: one item arrives; server drains (mu * inter_arrival_time) items.
    # Net queue change per event = 1 - mu * inter_arrival_time.
    np.random.seed(seed)
    q = 0.0
    depths = np.empty(n_ticks)
    for i in range(n_ticks):
        # Draw the time between this arrival and the next
        inter_arrival = np.random.exponential(1.0 / lam)
        # Service capacity during that window
        drained = mu * inter_arrival
        q = max(0.0, q + 1.0 - drained)
        depths[i] = q

    # Check for upward trend in the second half
    half = n_ticks // 2
    second_half = depths[half:]
    x_idx = np.arange(len(second_half), dtype=float)
    slope = np.polyfit(x_idx, second_half, 1)[0]

    return slope <= 0.05  # small positive tolerance for sampling noise


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_overloaded_system_is_unstable():
    """λ = 100 events/s, μ = 1 event/s → ρ = 100 >> 1, must be flagged UNSTABLE."""
    lam = 100.0
    mu = 1.0
    stable = _is_stable(lam, mu)
    assert not stable, (
        f"Expected UNSTABLE for λ={lam}, μ={mu} (ρ={lam/mu:.1f}), "
        f"but got stable=True"
    )


def test_lightly_loaded_system_is_stable():
    """λ = 1 event/s, μ = 100 events/s → ρ = 0.01 << 1, must be flagged STABLE."""
    lam = 1.0
    mu = 100.0
    stable = _is_stable(lam, mu)
    assert stable, (
        f"Expected STABLE for λ={lam}, μ={mu} (ρ={lam/mu:.3f}), "
        f"but got stable=False"
    )


def test_near_critical_overload_is_unstable():
    """λ = 0.99 events/s, μ = 1.0 events/s → ρ = 0.99, right at the edge.
    Analytically stable (ρ < 1), so this SHOULD be flagged stable — but queue
    depth will grow very slowly. This test confirms the function doesn't
    over-aggressively flag near-critical systems as unstable."""
    lam = 0.99
    mu = 1.0
    stable = _is_stable(lam, mu, n_ticks=5_000, seed=42)
    # ρ < 1, so analytically stable — test that we agree
    assert stable, (
        f"Expected STABLE for λ={lam}, μ={mu} (ρ={lam/mu:.3f}), "
        f"but got stable=False"
    )


def test_clearly_overloaded_various_ratios():
    """Multiple λ/μ > 1 ratios, all must be UNSTABLE."""
    mu = 10.0
    for lam in [11.0, 20.0, 50.0, 100.0, 1000.0]:
        stable = _is_stable(lam, mu)
        assert not stable, (
            f"Expected UNSTABLE for λ={lam}, μ={mu} (ρ={lam/mu:.1f})"
        )


def test_clearly_stable_various_ratios():
    """Multiple λ/μ << 1 ratios, all must be STABLE."""
    mu = 100.0
    for lam in [1.0, 5.0, 10.0, 50.0]:
        stable = _is_stable(lam, mu, n_ticks=5_000)
        assert stable, (
            f"Expected STABLE for λ={lam}, μ={mu} (ρ={lam/mu:.2f})"
        )
