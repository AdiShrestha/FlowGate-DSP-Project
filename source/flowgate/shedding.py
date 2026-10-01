"""Deterministic stride admission, with held output explicitly marked.

No downstream detector is run here. A held display value is not a new
measurement or alert. Runtime must account for every ingress/controller step.
"""
from dataclasses import dataclass
from .filters import EMA, AdaptiveAlpha
from .validation import alpha_value, finite, integer, load_value


class StrideShedder:
    def __init__(self, *, max_skip):
        self.max_skip = integer(max_skip, "max_skip", 0)
        self.since = self.max_skip

    def step(self, load):
        load = load_value(load)
        # Python round: ties to even. This is part of the declared event policy.
        target = round(self.max_skip * load)
        if self.since >= target:
            self.since = 0
            return True
        self.since += 1
        return False


@dataclass(frozen=True)
class FilterObservation:
    event_index: int
    processed: bool
    output: float
    alpha: float
    initialized_from_first: bool
    effective_beta: float


class EMAPipeline:
    """Alpha/controller advance on each ingress event; EMA only on admitted events.

    Holding/skipping changes the event-domain filter operator. We intentionally
    do not claim equivalence to a full-rate EMA or invent omitted observations.
    """
    def __init__(self, *, alpha, initialization, max_skip):
        if isinstance(alpha, AdaptiveAlpha):
            self.controller = alpha
            start_alpha = alpha.alpha_max
        else:
            self.controller = None
            start_alpha = alpha_value(alpha)
        self.filter = EMA(start_alpha, initialization=initialization)
        self.shedder = StrideShedder(max_skip=max_skip)
        self.events = 0

    def step(self, x, load):
        x = finite(x, "x")
        load = load_value(load)
        previous = (self.controller.value if self.controller else None,
                    self.shedder.since, self.filter.value, self.filter.updates)
        try:
            a = self.controller.step(load) if self.controller is not None else self.filter.alpha
            processed = self.shedder.step(load)
            first = processed and self.filter.value is None
            if processed:
                self.filter.step(x, alpha=a)
        except Exception:
            if self.controller:
                self.controller.value = previous[0]
            self.shedder.since, self.filter.value, self.filter.updates = previous[1:]
            raise
        # alpha is the controller's command. First-value initialization is a
        # state assignment (weight one); a skipped event is a hold (weight zero).
        beta = 1.0 if first else a if processed else 0.0
        observation = FilterObservation(self.events, processed, self.filter.value, a, first, beta)
        self.events += 1
        return observation

    def process(self, values, loads):
        values = [finite(x, "x") for x in values]
        loads = [load_value(x) for x in loads]
        if len(values) != len(loads):
            raise ValueError("values and loads must have identical length")
        before=(self.controller.value if self.controller else None,self.shedder.since,
                self.filter.value,self.filter.updates,self.events)
        try:return [self.step(x, load) for x, load in zip(values, loads)]
        except Exception:
            if self.controller:self.controller.value=before[0]
            self.shedder.since,self.filter.value,self.filter.updates,self.events=before[1:]
            raise
