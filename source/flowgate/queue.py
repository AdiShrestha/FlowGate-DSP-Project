"""Exact FCFS scheduling algebra. Outputs are MODEL predictions, not telemetry.

Inputs are timestamps in seconds and declared per-event service durations in
seconds. This operator does not sample arrivals, infer service from filter
timings, claim infinite-horizon stability, or invent server measurements.
"""
import math
from dataclasses import dataclass
from .validation import finite


@dataclass(frozen=True)
class QueueObservation:
    event_index: int
    arrival_s: float
    admitted: bool
    start_s: float | None
    finish_s: float | None
    wait_s: float | None
    sojourn_s: float | None


def fcfs_schedule(arrivals_s, service_s, *, admitted=None):
    arrivals = [finite(t, "arrival_s") for t in arrivals_s]
    services = [finite(s, "service_s") for s in service_s]
    if len(arrivals) != len(services):
        raise ValueError("arrivals and service durations must align")
    if any(s < 0 for s in services):
        raise ValueError("service durations must be nonnegative")
    if any(b < a for a, b in zip(arrivals, arrivals[1:])):
        raise ValueError("arrivals must be nondecreasing; do not repair ordering silently")
    mask = [True] * len(arrivals) if admitted is None else list(admitted)
    if len(mask) != len(arrivals) or any(type(x) is not bool for x in mask):
        raise ValueError("admitted must be an aligned boolean vector")
    previous_finish = None
    rows = []
    for i, (t, s, keep) in enumerate(zip(arrivals, services, mask)):
        if not keep:
            rows.append(QueueObservation(i, t, False, None, None, None, None))
            continue
        start = t if previous_finish is None else max(t, previous_finish)
        finish = start + s
        if not math.isfinite(finish):
            raise ArithmeticError("non-finite completion time")
        wait, sojourn = start - t, finish - t
        if not math.isfinite(wait) or not math.isfinite(sojourn):
            raise ArithmeticError("non-finite queue wait/sojourn")
        rows.append(QueueObservation(i, t, True, start, finish, wait, sojourn))
        previous_finish = finish
    return rows
