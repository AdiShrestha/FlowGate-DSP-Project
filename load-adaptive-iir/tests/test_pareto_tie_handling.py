"""
test_pareto_tie_handling.py — Regression test for the Pareto dominance
tie-handling bug (Section 1 of the hardening pass).

The previous implementation used strict > on BOTH axes, so two points that
tie on throughput but differ on AUC were both kept on the frontier — even
though the lower-AUC one is dominated by the higher-AUC one.

The correct definition: q dominates p iff q >= p on every axis AND q > p on
at least one.  This test verifies that fix holds.
"""

import sys
import numpy as np
import pytest
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the fixed internal helpers directly from experiment_c_pareto
from src.experiment_c_pareto import _dominates, _pareto_frontier


# ---------------------------------------------------------------------------
# Named-point helper so tests read clearly
# ---------------------------------------------------------------------------

class Point:
    """Lightweight named point for test readability."""
    def __init__(self, name: str, throughput: float, roc_auc: float):
        self.name = name
        self.throughput = throughput
        self.roc_auc = roc_auc

    def to_row(self) -> np.ndarray:
        return np.array([self.throughput, self.roc_auc], dtype=float)


def run_pareto(points: list[Point]) -> set[str]:
    """Run _pareto_frontier on a list of Points, return names of survivors."""
    arr = np.array([p.to_row() for p in points])
    mask = _pareto_frontier(arr)
    return {p.name for p, m in zip(points, mask) if m}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_dominates_strict_improvement_both_axes():
    """q is strictly better on both axes → q dominates p."""
    q = np.array([200.0, 0.90])
    p = np.array([100.0, 0.80])
    assert _dominates(q, p)
    assert not _dominates(p, q)


def test_dominates_tied_throughput_higher_auc():
    """q ties on throughput but has higher AUC → q dominates p (tie-axis fix)."""
    q = np.array([100.0, 0.90])
    p = np.array([100.0, 0.80])
    assert _dominates(q, p), "Higher AUC with tied throughput should dominate"
    assert not _dominates(p, q)


def test_dominates_tied_auc_higher_throughput():
    """q has higher throughput but ties on AUC → q dominates p."""
    q = np.array([200.0, 0.80])
    p = np.array([100.0, 0.80])
    assert _dominates(q, p), "Higher throughput with tied AUC should dominate"
    assert not _dominates(p, q)


def test_dominates_identical_points_neither_dominates():
    """Identical points: neither dominates the other."""
    p = np.array([100.0, 0.80])
    q = np.array([100.0, 0.80])
    assert not _dominates(p, q)
    assert not _dominates(q, p)


def test_dominates_incomparable_points():
    """p better on throughput, q better on AUC → neither dominates."""
    p = np.array([200.0, 0.70])
    q = np.array([100.0, 0.90])
    assert not _dominates(p, q)
    assert not _dominates(q, p)


def test_pareto_correctly_handles_ties():
    """
    Reproduces the exact tie structure of the 6-config dataset:
      - Group A: tied throughput=100, varying AUC → only highest AUC survives
      - Group B: tied throughput=200, varying AUC → only highest AUC survives
    Expected frontier: {A1, B1}
    """
    points = [
        Point("A1", throughput=100, roc_auc=0.80),
        Point("A2", throughput=100, roc_auc=0.75),  # dominated by A1 (same thru, lower AUC)
        Point("A3", throughput=100, roc_auc=0.70),  # dominated by A1
        Point("B1", throughput=200, roc_auc=0.65),
        Point("B2", throughput=200, roc_auc=0.60),  # dominated by B1
    ]
    frontier = run_pareto(points)
    assert frontier == {"A1", "B1"}, (
        f"Expected frontier {{'A1', 'B1'}}, got {frontier}.\n"
        "Tie-handling bug: a point with the same throughput but lower AUC "
        "must be dominated by the higher-AUC point in the same throughput tier."
    )


def test_pareto_all_distinct_incomparable():
    """When no point dominates any other, all should be on the frontier."""
    points = [
        Point("X1", throughput=300, roc_auc=0.60),
        Point("X2", throughput=200, roc_auc=0.75),
        Point("X3", throughput=100, roc_auc=0.90),
    ]
    frontier = run_pareto(points)
    assert frontier == {"X1", "X2", "X3"}, (
        f"All three are incomparable, all should survive; got {frontier}"
    )


def test_pareto_single_dominant_point():
    """One point dominates all others on both axes."""
    points = [
        Point("Best",  throughput=300, roc_auc=0.95),
        Point("Mid",   throughput=200, roc_auc=0.80),
        Point("Worst", throughput=100, roc_auc=0.60),
    ]
    frontier = run_pareto(points)
    assert frontier == {"Best"}, (
        f"Only 'Best' should survive; got {frontier}"
    )


def test_pareto_two_tier_ties_match_6config_structure():
    """
    Replicates the exact 6-config production structure:
      - 2 high-throughput configs (shedding: same tier)
      - 4 normal-throughput configs (non-shedding: same tier)
    Within each tier, only the config with the highest AUC should survive.
    Across tiers, the two survivors (one per tier) are incomparable
    (high-throughput has lower AUC, normal-throughput has higher AUC),
    so both survive.
    """
    points = [
        # High-throughput tier (shedding)
        Point("HS1", throughput=346000, roc_auc=0.66),
        Point("HS2", throughput=346000, roc_auc=0.65),  # dominated by HS1
        # Normal-throughput tier (no shedding)
        Point("NS1", throughput=179000, roc_auc=0.76),
        Point("NS2", throughput=179000, roc_auc=0.75),  # dominated by NS1
        Point("NS3", throughput=179000, roc_auc=0.70),  # dominated by NS1
        Point("NS4", throughput=179000, roc_auc=0.65),  # dominated by NS1
    ]
    frontier = run_pareto(points)
    assert frontier == {"HS1", "NS1"}, (
        f"Expected exactly {{'HS1', 'NS1'}}; got {frontier}.\n"
        "This is the production-structure equivalent: within each throughput tier "
        "only the highest-AUC config should survive."
    )
