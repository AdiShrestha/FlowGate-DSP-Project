"""
test_load_shedding.py — Section 7, test for compute_processing_mask.

Tests:
1. all-True at L=0 everywhere (no shedding at zero load)
2. expected stride pattern at L=1 everywhere
3. never produces a gap longer than shed_max_skip+1 ticks
4. L containing NaN raises ValueError (not silent misbehaviour)
5. edge-case: single-element and empty-ish inputs
"""

import numpy as np
import pytest
import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.load_shedding import compute_processing_mask


# ---------------------------------------------------------------------------
# Test 1 — No shedding at zero load
# ---------------------------------------------------------------------------

def test_zero_load_all_processed():
    """At L=0 everywhere, every tick must be processed (all True)."""
    for n in [1, 10, 100, 1000]:
        L = np.zeros(n)
        mask = compute_processing_mask(L, shed_max_skip=4)
        assert np.all(mask), f"Expected all-True at L=0, n={n}"


# ---------------------------------------------------------------------------
# Test 2 — Expected stride at L=1
# ---------------------------------------------------------------------------

def test_full_load_stride_pattern():
    """
    At L=1 with shed_max_skip=4, target_skip = round(4*1) = 4.
    The rule processes tick i when ticks_since_processed >= target_skip.
    Starting from i=0: process tick 0, skip 1-4, process 5, skip 6-9, ...
    i.e. every 5th tick is processed (indices 0, 5, 10, ...).
    """
    shed = 4
    n = 50
    L = np.ones(n)
    mask = compute_processing_mask(L, shed_max_skip=shed)

    # Verify the first processed index is 0
    assert mask[0], "First tick should always be processed"

    # Every gap between consecutive processed ticks must equal shed_max_skip+1
    processed = np.where(mask)[0]
    if len(processed) > 1:
        gaps = np.diff(processed)
        assert np.all(gaps == shed + 1), (
            f"Expected all gaps = {shed + 1} at L=1, got {gaps}"
        )


def test_full_load_stride_various_shed_max():
    """Test stride pattern for shed_max_skip values 1, 2, 3, 8."""
    for shed in [1, 2, 3, 8]:
        n = 100
        L = np.ones(n)
        mask = compute_processing_mask(L, shed_max_skip=shed)
        processed = np.where(mask)[0]
        if len(processed) > 1:
            gaps = np.diff(processed)
            assert np.all(gaps == shed + 1), (
                f"shed_max_skip={shed}: expected gap {shed+1}, got {gaps}"
            )


# ---------------------------------------------------------------------------
# Test 3 — Max gap never exceeds shed_max_skip+1
# ---------------------------------------------------------------------------

def test_max_gap_bounded_random_load():
    """For random L in [0,1], the longest run of skipped ticks must be <= shed_max_skip."""
    np.random.seed(99)
    shed = 4
    for _ in range(10):
        L = np.random.uniform(0, 1, 500)
        mask = compute_processing_mask(L, shed_max_skip=shed)

        # Compute longest consecutive False run
        max_gap = 0
        current_gap = 0
        for v in mask:
            if not v:
                current_gap += 1
                max_gap = max(max_gap, current_gap)
            else:
                current_gap = 0

        assert max_gap <= shed, (
            f"Max gap {max_gap} exceeds shed_max_skip={shed}"
        )


def test_first_tick_always_processed():
    """The very first tick must always be processed (ticks_since_processed starts at 0)."""
    np.random.seed(3)
    for _ in range(20):
        L = np.random.uniform(0, 1, 50)
        mask = compute_processing_mask(L, shed_max_skip=4)
        assert mask[0], "First tick must always be processed"


# ---------------------------------------------------------------------------
# Test 4 — NaN in L raises ValueError
# ---------------------------------------------------------------------------

def test_nan_raises():
    """L containing NaN must raise ValueError, not silently misbehave."""
    L = np.array([0.0, 0.5, np.nan, 1.0, 0.2])
    with pytest.raises(ValueError, match="NaN"):
        compute_processing_mask(L, shed_max_skip=4)


def test_nan_raises_all_nan():
    L = np.full(20, np.nan)
    with pytest.raises(ValueError, match="NaN"):
        compute_processing_mask(L, shed_max_skip=2)


# ---------------------------------------------------------------------------
# Test 5 — Edge cases
# ---------------------------------------------------------------------------

def test_single_element():
    """Single-element L should work without error."""
    L = np.array([0.5])
    mask = compute_processing_mask(L, shed_max_skip=4)
    assert len(mask) == 1
    assert mask[0]  # First tick always processed


def test_shed_max_skip_zero():
    """shed_max_skip=0 means target_skip=0 for all L, so every tick is processed."""
    np.random.seed(5)
    L = np.random.uniform(0, 1, 100)
    mask = compute_processing_mask(L, shed_max_skip=0)
    assert np.all(mask), "shed_max_skip=0 should process every tick"


def test_output_length_matches_input():
    """Output mask must be the same length as input L."""
    for n in [1, 10, 100, 999]:
        L = np.random.uniform(0, 1, n)
        mask = compute_processing_mask(L)
        assert len(mask) == n, f"Length mismatch: got {len(mask)}, expected {n}"


def test_dtype_is_bool():
    """Output must be a boolean array."""
    L = np.linspace(0, 1, 50)
    mask = compute_processing_mask(L, shed_max_skip=4)
    assert mask.dtype == np.bool_, f"Expected bool, got {mask.dtype}"
