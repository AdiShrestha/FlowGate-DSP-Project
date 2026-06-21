"""
test_shedding_changes_evaluation.py — Regression test for the 'borrowed metric'
shedding bug (Section 4.2 of the hardening pass).

The original bug: shedding-enabled configurations silently reused the
non-shedding configuration's ROC-AUC score instead of being re-evaluated
on their actual (shed-applied) output.  This caused the shedding row to
report the same detection quality as its baseline, masking the real tradeoff.

This test guards against that regression: given a backpressure trace with
non-trivial shedding (shed_fraction > 10%), the ROC-AUC of Fixed EMA + Shedding
must DIFFER from Fixed EMA (no shedding).  Identical results is the bug's
exact symptom.

Shed fraction is verified first so we know shedding actually fired.
"""

import sys
import numpy as np
import pytest
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.anomaly_injection import inject_anomalies
from src.detection import detect_anomalies
from src.evaluate import compute_auc
from src.load_shedding import run_config, compute_processing_mask
from src.queue_simulator import simulate_backpressure


# ---------------------------------------------------------------------------
# Helper: build a test environment with non-trivial shedding
# ---------------------------------------------------------------------------

def _build_test_environment():
    """
    Build a deterministic synthetic price series + backpressure trace that
    reliably produces shed_fraction > 0.10 so shedding actually fires.
    Returns (x_injected, L, mask_ground_truth, anomaly_info).
    """
    n = 20_000
    rng = np.random.default_rng(0)
    t = np.arange(n) * (1.0 / 8.66)
    p = 40_000.0 + np.cumsum(rng.standard_normal(n) * 5.0)
    import pandas as pd
    df = pd.DataFrame({'timestamp': t, 'price': p})

    # High burst multiplier to get non-trivial shedding
    bursts = [(3_000, 8_000), (12_000, 17_000)]
    L = simulate_backpressure(df['timestamp'], burst_multiplier=3.0, burst_intervals=bursts)
    L_arr = L.values.astype(np.float64)

    x_clean = p
    x_injected, mask, anomaly_info = inject_anomalies(pd.Series(x_clean), seed=7)

    return x_injected.values if hasattr(x_injected, 'values') else np.asarray(x_injected), L_arr, mask, anomaly_info


def _evaluate_filter(config_name: str, x: np.ndarray, L: np.ndarray,
                     mask: np.ndarray, anomaly_info: list) -> float:
    """Run a named config and return ROC-AUC."""
    y, _, _ = run_config(config_name, x, L)
    _, z_score, _ = detect_anomalies(x, y)
    roc_auc, _, _, _, _, _ = compute_auc(z_score, anomaly_info, mask)
    return roc_auc


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_shedding_actually_skips_ticks():
    """
    Pre-condition: the shedding mechanism must actually skip ticks (shed_fraction > 0.10).
    If this fails, the other tests are vacuous (shedding never fired).
    """
    _, L, _, _ = _build_test_environment()
    mask = compute_processing_mask(L, shed_max_skip=4)
    shed_fraction = 1.0 - float(np.mean(mask))
    assert shed_fraction > 0.10, (
        f"Shedding shed_fraction={shed_fraction:.4f} <= 0.10; "
        "the test environment doesn't produce enough load for non-trivial shedding. "
        "Adjust burst_multiplier or burst_intervals."
    )


def test_shedding_produces_different_roc_auc_than_baseline():
    """
    Fixed EMA + Shedding must produce a DIFFERENT ROC-AUC than Fixed EMA (no shedding).
    Identical results is the exact symptom of the 'borrowed metric' bug.
    """
    x, L, mask, anomaly_info = _build_test_environment()

    roc_auc_baseline = _evaluate_filter("Fixed EMA", x, L, mask, anomaly_info)
    roc_auc_shed = _evaluate_filter("Fixed EMA + Shedding", x, L, mask, anomaly_info)

    assert roc_auc_baseline != roc_auc_shed, (
        f"Shedding-enabled evaluation returned an IDENTICAL ROC-AUC "
        f"({roc_auc_shed:.6f}) to the non-shedding baseline ({roc_auc_baseline:.6f}). "
        "This is the exact symptom of the 'borrowed metric' bug found earlier: "
        "shedding configurations must be re-evaluated on their actual (shed-applied) "
        "output, not inherit the baseline's score."
    )


def test_shedding_produces_different_roc_auc_load_adaptive():
    """
    Load-Adaptive EMA + Shedding must differ from Load-Adaptive EMA (no shedding).
    """
    x, L, mask, anomaly_info = _build_test_environment()

    roc_auc_baseline = _evaluate_filter("Load-Adaptive EMA", x, L, mask, anomaly_info)
    roc_auc_shed = _evaluate_filter("Load-Adaptive EMA + Shedding", x, L, mask, anomaly_info)

    assert roc_auc_baseline != roc_auc_shed, (
        f"Load-Adaptive EMA + Shedding ROC-AUC ({roc_auc_shed:.6f}) == "
        f"Load-Adaptive EMA ({roc_auc_baseline:.6f}). 'Borrowed metric' bug regression."
    )


def test_shedding_z_scores_differ_from_baseline():
    """
    The z-score arrays themselves (not just the final AUC) must differ between
    the shedding and non-shedding paths.  This rules out the bug hiding at the
    z-score level even if AUC happens to match.
    """
    x, L, mask, anomaly_info = _build_test_environment()

    y_base, _, _ = run_config("Fixed EMA", x, L)
    y_shed, _, _ = run_config("Fixed EMA + Shedding", x, L)

    _, z_base, _ = detect_anomalies(x, y_base)
    _, z_shed, _ = detect_anomalies(x, y_shed)

    assert not np.allclose(z_base, z_shed, atol=1e-10), (
        "z-score arrays are identical for Fixed EMA with and without shedding. "
        "Shedding must change the filter output (forward-filled gaps), which "
        "propagates into the residuals and z-scores."
    )


def test_shedding_output_has_forward_filled_gaps():
    """
    The shedding filter output must contain constant runs (forward-fill) at
    the positions where ticks were skipped.  This verifies the shedding
    mechanism is actually active and writing to the output array.
    """
    x, L, mask, anomaly_info = _build_test_environment()

    y_shed, _, process_mask = run_config("Fixed EMA + Shedding", x, L)
    assert process_mask is not None, "process_mask should not be None for a shedding config"

    # Find a skipped region and verify y is constant there
    skipped = np.where(~process_mask)[0]
    assert len(skipped) > 0, "No skipped ticks found — shedding didn't fire"

    # Find a run of 2+ consecutive skipped ticks
    found_run = False
    for i in range(len(skipped) - 1):
        if skipped[i + 1] == skipped[i] + 1:
            # Both i and i+1 are skipped — y must be constant (forward-fill)
            assert y_shed[skipped[i]] == y_shed[skipped[i + 1]], (
                f"Forward-fill broken at ticks {skipped[i]}, {skipped[i+1]}: "
                f"y={y_shed[skipped[i]]:.6f} vs {y_shed[skipped[i+1]]:.6f}"
            )
            found_run = True
            break
    assert found_run, "No consecutive skipped-tick pair found to verify forward-fill"
