"""Pair by explicit independent-unit identity. No truncation or seed-only joining."""
import math
from statistics import fmean, stdev
from .validation import finite


def paired_t_summary(a_by_unit, b_by_unit, *, confidence):
    """Student-t interval for a preregistered independent-unit mean difference.

    Caller must justify unit independence and approximate normality of the
    mean. Repeated seeds within one day are not independent population days.
    Returns an explicit degenerate status rather than NaN, zero p, or a verdict.
    """
    from scipy.stats import t as student_t
    confidence = finite(confidence, "confidence")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0,1)")
    if set(a_by_unit) != set(b_by_unit) or len(a_by_unit) < 2:
        raise ValueError("identical unit IDs and at least two units are required")
    ids = sorted(a_by_unit)
    differences = [finite(a_by_unit[i], "A") - finite(b_by_unit[i], "B") for i in ids]
    if not all(math.isfinite(d) for d in differences):
        raise ArithmeticError("paired differences exceed finite floating-point range")
    estimate = fmean(differences)
    sd = stdev(differences)
    if sd == 0:
        return {"unit_ids": ids, "n_units": len(ids), "effect": estimate,
                "ci": None, "p_two_sided": None, "status": "degenerate_variance"}
    se = sd / math.sqrt(len(ids))
    df = len(ids) - 1
    critical = float(student_t.ppf((1 + confidence) / 2, df))
    p = float(2 * student_t.sf(abs(estimate / se), df))
    interval = [estimate - critical * se, estimate + critical * se]
    if not all(math.isfinite(v) for v in [estimate, sd, se, critical, *interval, p]) or se <= 0:
        raise ArithmeticError("paired inference exceeds finite floating-point range")
    return {"unit_ids": ids, "n_units": len(ids), "effect": estimate,
            "ci": interval,
            "confidence": confidence, "p_two_sided": p if p > 0 else None,
            "status": "p_underflow" if p == 0 else "ok"}


def holm_adjust(pvalues):
    pvalues = [finite(p, "p") for p in pvalues]
    if any(not 0 <= p <= 1 for p in pvalues):
        raise ValueError("p values must lie in [0,1]")
    adjusted = [0.0] * len(pvalues)
    previous = 0.0
    for rank, i in enumerate(sorted(range(len(pvalues)), key=pvalues.__getitem__)):
        previous = max(previous, min(1.0, pvalues[i] * (len(pvalues) - rank)))
        adjusted[i] = previous
    return adjusted
