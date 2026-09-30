"""
test_anomaly_injection.py — Tests for anomaly_injection.py.

Covers:
  1. Determinism (same seed → same output)
  2. Non-overlap guarantee
  3. All three anomaly types are present
  4. Series-too-short raises ValueError
  5. n_each=0 produces empty anomaly_info
  6. Mask matches anomaly_info locations
"""

import sys
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.anomaly_injection import inject_anomalies


def _make_series(n=5000, seed=0):
    rng = np.random.default_rng(seed)
    prices = 40_000.0 + np.cumsum(rng.standard_normal(n) * 5.0)
    return pd.Series(prices)


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_same_seed_same_output():
    """Same seed must produce bit-identical output."""
    x = _make_series()
    x1, mask1, info1 = inject_anomalies(x, seed=42)
    x2, mask2, info2 = inject_anomalies(x, seed=42)
    np.testing.assert_array_equal(x1, x2)
    np.testing.assert_array_equal(mask1, mask2)
    assert [(a['type'], a['start'], a['end']) for a in info1] == \
           [(a['type'], a['start'], a['end']) for a in info2]


def test_different_seeds_different_output():
    """Different seeds must produce different injection locations."""
    x = _make_series()
    _, mask1, _ = inject_anomalies(x, seed=1)
    _, mask2, _ = inject_anomalies(x, seed=2)
    assert not np.array_equal(mask1, mask2), "Different seeds produced identical masks"


# ---------------------------------------------------------------------------
# Output structure
# ---------------------------------------------------------------------------

def test_output_length_matches_input():
    x = _make_series(n=3000)
    x_inj, mask, info = inject_anomalies(x)
    assert len(x_inj) == len(x)
    assert len(mask) == len(x)


def test_mask_dtype_is_bool():
    x = _make_series()
    _, mask, _ = inject_anomalies(x)
    assert mask.dtype == bool


def test_all_three_anomaly_types_injected():
    """inject_anomalies must inject all three types: point, level_shift, volatility_burst."""
    x = _make_series(n=5000)
    _, _, info = inject_anomalies(x, n_each=3)
    types_found = {a['type'] for a in info}
    assert 'point' in types_found
    assert 'level_shift' in types_found
    assert 'volatility_burst' in types_found


def test_anomaly_info_matches_mask():
    """Every location in anomaly_info must be True in the mask."""
    x = _make_series(n=5000)
    _, mask, info = inject_anomalies(x, n_each=3)
    for a in info:
        # At least the first sample of each anomaly must be in the mask
        assert mask[a['start']], (
            f"Anomaly start={a['start']} not set in mask for type {a['type']}"
        )


# ---------------------------------------------------------------------------
# Non-overlap guarantee
# ---------------------------------------------------------------------------

def test_anomaly_windows_do_not_overlap():
    """
    The inject_anomalies function removes used indices from available_indices
    with a 300-sample exclusion zone. Injected anomaly windows must not overlap.
    """
    x = _make_series(n=10_000)
    _, _, info = inject_anomalies(x, n_each=5, seed=99)

    intervals = sorted([(a['start'], a['end']) for a in info])
    for i in range(len(intervals) - 1):
        end_i = intervals[i][1]
        start_next = intervals[i + 1][0]
        assert start_next > end_i, (
            f"Overlapping anomaly windows: [{intervals[i]}] and [{intervals[i+1]}]"
        )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_series_too_short_raises():
    """Series shorter than 2×buffer=1000 samples must raise ValueError."""
    x = pd.Series(np.ones(999))
    with pytest.raises(ValueError, match="too short"):
        inject_anomalies(x)


def test_n_each_zero_produces_empty_info():
    """n_each=0 must inject nothing and return an empty anomaly_info list."""
    x = _make_series(n=3000)
    x_inj, mask, info = inject_anomalies(x, n_each=0)
    assert len(info) == 0
    assert not np.any(mask), "Mask must be all-False when n_each=0"
    np.testing.assert_array_equal(x_inj, x.values)
