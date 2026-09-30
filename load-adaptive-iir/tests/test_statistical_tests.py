"""
test_statistical_tests.py — Unit tests for the paired t-test functions.

All tests use small synthetic numpy arrays (n <= 50) — no data loading,
no Numba, no large allocations.
"""

import sys
import numpy as np
import pytest
import pandas as pd
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.statistical_tests import run_paired_ttest, batch_paired_ttests


# ---------------------------------------------------------------------------
# Tests for run_paired_ttest
# ---------------------------------------------------------------------------

def test_paired_ttest_identical_arrays_not_significant():
    """
    Identical arrays → all differences = 0 → scipy returns NaN for t and p
    (0/0 with std=0). The practical requirement: delta_auc must be zero and
    significant_05 must be False (NaN is not < 0.05).
    """
    rng = np.random.default_rng(0)
    aucs = rng.uniform(0.6, 0.9, 30)
    result = run_paired_ttest(aucs, aucs.copy(), "A", "B")
    assert abs(result['delta_auc']) < 1e-12
    assert not result['significant_05']   # NaN < 0.05 is False in Python
    assert not result['significant_01']


def test_paired_ttest_clearly_different_arrays_significant():
    """Arrays with a clear 0.10 mean difference must yield p < 0.001 at n=50."""
    rng = np.random.default_rng(1)
    aucs_A = rng.uniform(0.80, 0.90, 50)   # mean ~0.85
    aucs_B = rng.uniform(0.70, 0.80, 50)   # mean ~0.75
    result = run_paired_ttest(aucs_A, aucs_B, "A", "B")
    assert result['delta_auc'] > 0.05, f"Expected delta > 0.05, got {result['delta_auc']:.4f}"
    assert result['p_value'] < 0.001, f"Expected p < 0.001, got {result['p_value']:.4f}"
    assert result['significant_05']
    assert result['significant_01']


def test_paired_ttest_delta_direction_positive():
    """delta_auc = mean(A) - mean(B), positive when A > B."""
    aucs_A = np.full(20, 0.80)
    aucs_B = np.full(20, 0.75)
    result = run_paired_ttest(aucs_A, aucs_B, "A", "B")
    assert result['delta_auc'] > 0


def test_paired_ttest_delta_direction_negative():
    """delta_auc is negative when A < B."""
    aucs_A = np.full(20, 0.70)
    aucs_B = np.full(20, 0.80)
    result = run_paired_ttest(aucs_A, aucs_B, "A", "B")
    assert result['delta_auc'] < 0


def test_paired_ttest_length_mismatch_raises():
    """Mismatched array lengths must raise AssertionError."""
    with pytest.raises(AssertionError):
        run_paired_ttest(np.ones(10), np.ones(20), "A", "B")


def test_paired_ttest_output_keys_complete():
    """Result dict must contain all expected keys."""
    result = run_paired_ttest(np.ones(5) * 0.8, np.ones(5) * 0.7, "A", "B")
    required = {'name_A', 'name_B', 'mean_auc_A', 'mean_auc_B',
                'delta_auc', 'ci_95', 't_stat', 'p_value',
                'significant_05', 'significant_01', 'n_seeds'}
    assert required.issubset(result.keys())


def test_paired_ttest_n_seeds_correct():
    """n_seeds in output must equal the input array length."""
    n = 42
    result = run_paired_ttest(np.ones(n) * 0.8, np.ones(n) * 0.7, "A", "B")
    assert result['n_seeds'] == n


def test_paired_ttest_ci_95_non_negative():
    """95% CI half-width must always be >= 0."""
    rng = np.random.default_rng(7)
    aucs_A = rng.uniform(0.7, 0.9, 30)
    aucs_B = rng.uniform(0.7, 0.9, 30)
    result = run_paired_ttest(aucs_A, aucs_B, "A", "B")
    assert result['ci_95'] >= 0


def test_paired_ttest_mean_auc_values_correct():
    """mean_auc_A and mean_auc_B must match np.mean of the inputs."""
    aucs_A = np.array([0.80, 0.82, 0.78, 0.81])
    aucs_B = np.array([0.70, 0.72, 0.68, 0.71])
    result = run_paired_ttest(aucs_A, aucs_B, "A", "B")
    assert abs(result['mean_auc_A'] - np.mean(aucs_A)) < 1e-10
    assert abs(result['mean_auc_B'] - np.mean(aucs_B)) < 1e-10


# ---------------------------------------------------------------------------
# Tests for batch_paired_ttests (uses a tiny in-memory CSV via tmp_path)
# ---------------------------------------------------------------------------

def _write_temp_multi_seed_csv(path: str):
    """Write a minimal multi_seed_roc_auc.csv with 2 configs × 10 seeds."""
    rng = np.random.default_rng(42)
    rows = []
    for seed in range(10):
        rows.append({'config': 'Fixed EMA',         'anomaly_type': 'all',
                     'seed': seed, 'roc_auc': 0.83 + rng.normal(0, 0.01)})
        rows.append({'config': 'Load Adaptive EMA', 'anomaly_type': 'all',
                     'seed': seed, 'roc_auc': 0.70 + rng.normal(0, 0.01)})
    pd.DataFrame(rows).to_csv(path, index=False)


def test_batch_paired_ttests_returns_dataframe(tmp_path):
    """batch_paired_ttests must return a non-empty DataFrame."""
    csv_in = str(tmp_path / "multi_seed_roc_auc.csv")
    _write_temp_multi_seed_csv(csv_in)

    # Override output path so we don't touch the real results dir
    import unittest.mock as mock
    with mock.patch("src.statistical_tests.Path") as MockPath:
        # Make Path("results/tables") / "paired_ttest_results.csv" go to tmp_path
        instance = mock.MagicMock()
        instance.__truediv__ = lambda self, x: Path(tmp_path) / x
        instance.mkdir = mock.MagicMock()
        MockPath.return_value = instance
        df = batch_paired_ttests(csv_path=csv_in, reference="Fixed EMA", anomaly_type="all")

    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 1
    assert 'p_value' in df.columns
    assert 'delta_auc' in df.columns


def test_batch_paired_ttests_large_delta_is_significant(tmp_path):
    """
    Load Adaptive EMA mean ~0.70 vs Fixed EMA ~0.83 (delta ~-0.13).
    At n=10 this must be statistically significant (p < 0.01).
    """
    csv_in = str(tmp_path / "multi_seed_roc_auc.csv")
    _write_temp_multi_seed_csv(csv_in)

    import unittest.mock as mock
    with mock.patch("src.statistical_tests.Path") as MockPath:
        instance = mock.MagicMock()
        instance.__truediv__ = lambda self, x: Path(tmp_path) / x
        instance.mkdir = mock.MagicMock()
        MockPath.return_value = instance
        df = batch_paired_ttests(csv_path=csv_in, reference="Fixed EMA", anomaly_type="all")

    row = df[df['name_A'].str.contains("Load Adaptive")]
    assert len(row) == 1, "Expected one row for Load Adaptive EMA"
    assert row.iloc[0]['p_value'] < 0.01, (
        f"Expected significant; got p={row.iloc[0]['p_value']:.4f}"
    )
    assert row.iloc[0]['delta_auc'] < 0  # Load Adaptive is worse here
