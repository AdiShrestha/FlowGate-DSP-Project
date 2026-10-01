"""Exact point rankings, explicit event misses, and mathematical Pareto membership.

Scores are finite anomaly RANKING scores, not calibrated probabilities.
No Brier/log loss is manufactured from an arbitrary score mapping.
"""
import math
from numbers import Integral
from statistics import mean
from .validation import finite


def point_metrics(labels, scores, *, threshold):
    labels = list(labels)
    if any(isinstance(y, bool) or not isinstance(y, Integral) or y not in {0, 1} for y in labels):
        raise ValueError("labels must be integer 0/1")
    labels = [int(y) for y in labels]
    scores = [finite(s, "score") for s in scores]
    threshold = finite(threshold, "threshold")
    if not labels or len(labels) != len(scores) or set(labels) != {0, 1}:
        raise ValueError("aligned, nonempty labels/scores with both classes are required")
    n = len(labels)
    pos = sum(labels)
    neg = n - pos
    # Integrate the complete grouped ROC and AP staircase, preserving all ties.
    ordered = sorted(zip(scores, labels), reverse=True)
    tp = fp = 0
    prev_tp = prev_fp = 0
    roc_area = ap = 0.0
    i = 0
    while i < n:
        j = i + 1
        while j < n and ordered[j][0] == ordered[i][0]:
            j += 1
        added_pos = sum(y for _, y in ordered[i:j])
        tp += added_pos
        fp += j - i - added_pos
        roc_area += (fp - prev_fp) * (tp + prev_tp) / (2.0 * pos * neg)
        ap += (tp - prev_tp) / pos * tp / (tp + fp)
        prev_tp, prev_fp = tp, fp
        i = j
    pred = [s >= threshold for s in scores]
    tp = sum(y == 1 and p for y, p in zip(labels, pred))
    fp = sum(y == 0 and p for y, p in zip(labels, pred))
    fn = pos - tp
    tn = neg - fp
    return {"auroc": roc_area, "average_precision": ap, "prevalence": pos / n,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "precision_status": "ok" if tp + fp else "undefined_no_positive_predictions",
            "recall": tp / pos, "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
            "false_positive_rate": fp / neg, "accuracy": (tp + tn) / n}


def event_metrics(events, alert_times_s, *, horizon_s, evaluation_start_s, evaluation_end_s):
    """One alert matches at most one event, in chronological onset order.

    Each event is (onset_s, end_s), within the evaluation interval. Matching
    is forward only in [onset, min(end+horizon, evaluation_end)]. Unmatched
    alerts are false alerts; unmatched events stay misses, with latency None.
    Overlapping windows use a greedy, declared matching policy. This is not
    a claim that this policy is universally appropriate for every dataset.
    All-event recall includes windows cut short at the evaluation boundary;
    a separately named fully-observed recall exposes that denominator choice.
    """
    start = finite(evaluation_start_s, "evaluation_start_s")
    end = finite(evaluation_end_s, "evaluation_end_s")
    horizon = finite(horizon_s, "horizon_s")
    if end <= start or horizon < 0:
        raise ValueError("positive evaluation duration and nonnegative horizon required")
    duration = end - start
    if not math.isfinite(duration):
        raise ArithmeticError("evaluation duration exceeds finite floating-point range")
    intervals = [(finite(a, "onset"), finite(b, "end")) for a, b in events]
    if any(a < start or b > end or b < a for a, b in intervals):
        raise ValueError("event bounds must lie within evaluation interval")
    if intervals != sorted(intervals):
        raise ValueError("events must be ordered by onset/end")
    alerts = [finite(t, "alert_time") for t in alert_times_s]
    if alerts != sorted(alerts) or any(t < start or t > end for t in alerts):
        raise ValueError("alert times must be ordered within evaluation interval")
    used = set()
    latencies = []
    event_rows = []
    for event_id, (onset, stop) in enumerate(intervals):
        censored = horizon > end - stop
        window_end = end if censored else stop + horizon
        match = next((i for i, t in enumerate(alerts)
                      if i not in used and onset <= t <= window_end), None)
        latency = None if match is None else alerts[match] - onset
        if latency is not None and not math.isfinite(latency):
            raise ArithmeticError("event latency exceeds finite floating-point range")
        if match is not None:
            used.add(match)
            latencies.append(latency)
        event_rows.append({"event_index": event_id, "onset_s": onset, "end_s": stop,
                           "alert_index": match, "latency_s": latency,
                           "matched": match is not None,
                           "window_right_censored": censored})
    hits = len(used)
    false_alerts = len(alerts) - hits
    rate = false_alerts / duration * 3600
    if not math.isfinite(rate):
        raise ArithmeticError("false-alert rate exceeds finite floating-point range")
    observed = [r for r in event_rows if not r['window_right_censored']]
    observed_hits = sum(r['matched'] for r in observed)
    return {"events": event_rows, "event_count": len(intervals), "hits": hits,
            "misses": len(intervals) - hits, "false_alerts": false_alerts,
            "event_recall": hits / len(intervals) if intervals else None,
            "false_alerts_per_hour": rate,
            "mean_latency_detected_s": mean(latencies) if hits else None,
            "matching_policy": "chronological_greedy_one_to_one_forward",
            "fully_observed_event_count": len(observed),
            "fully_observed_hits": observed_hits,
            "fully_observed_misses": len(observed) - observed_hits,
            "event_recall_fully_observed": observed_hits / len(observed) if observed else None,
            "right_censored_event_count": len(event_rows) - len(observed),
            "right_censored_unmatched_count": sum(not r['matched'] for r in event_rows if r['window_right_censored'])}


def pareto_mask(points):
    """Higher is better on EVERY axis. Tied identical points both survive.

    Requires estimates from the same experiment keys; this function itself
    checks only finite numerical coordinates, not provenance or uncertainty.
    """
    points = [[finite(x, "coordinate") for x in p] for p in points]
    if not points:
        return []
    width = len(points[0])
    if width == 0 or any(len(p) != width for p in points):
        raise ValueError("points must have a nonzero common dimension")
    return [not any(all(qk >= pk for qk, pk in zip(q, p)) and
                    any(qk > pk for qk, pk in zip(q, p)) for j, q in enumerate(points) if i != j)
            for i, p in enumerate(points)]
