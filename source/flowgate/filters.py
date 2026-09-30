"""Stateful filters with explicit initialization and clock semantics.

EMA, adaptive alpha, and KAMA advance in EVENT/UPDATE units. They do not
claim a physical Hz cutoff for irregular timestamps. Butterworth requires
an explicitly uniform grid. State persists across caller batch boundaries.
"""
import math
from collections import deque
from .validation import alpha_value, finite, integer, load_value, positive


class EMA:
    def __init__(self, alpha, *, initialization):
        self.alpha = alpha_value(alpha)
        if initialization not in {"zero", "first"}:
            raise ValueError("initialization must be 'zero' or 'first'")
        self.initialization = initialization
        self.value = 0.0 if initialization == "zero" else None
        self.updates = 0

    def step(self, x, *, alpha=None):
        x = finite(x, "x")
        a = self.alpha if alpha is None else alpha_value(alpha)
        if self.value is None:
            self.value = x
        else:
            result = (1.0 - a) * self.value + a * x
            if not math.isfinite(result):
                raise ArithmeticError("non-finite EMA state/output")
            self.value = result
        self.updates += 1
        return self.value

    def process(self, values):
        return [self.step(x) for x in values]


def ema(values, alpha, *, initialization):
    """Batch convenience; use EMA directly to retain state between batches."""
    return EMA(alpha, initialization=initialization).process(values)


class AdaptiveAlpha:
    def __init__(self, alpha_min, alpha_max, *, max_delta):
        self.alpha_min = alpha_value(alpha_min, "alpha_min")
        self.alpha_max = alpha_value(alpha_max, "alpha_max")
        if self.alpha_min > self.alpha_max:
            raise ValueError("alpha_min must be <= alpha_max")
        self.max_delta = positive(max_delta, "max_delta per observed event")
        self.value = None

    def step(self, load):
        load = load_value(load)
        # Equivalent convex form preserves tiny positive minima at full load.
        target = self.alpha_max * (1.0 - load) + self.alpha_min * load
        target = max(self.alpha_min, min(self.alpha_max, target))
        if self.value is None:
            self.value = target
        else:
            delta = max(-self.max_delta, min(self.max_delta, target - self.value))
            self.value = max(self.alpha_min, min(self.alpha_max, self.value + delta))
        return self.value


class KAMA:
    """Efficiency-ratio EMA; warmup uses slowSC squared, and reports actual alpha.

    period counts OBSERVED updates. Skipping observations changes that clock
    and must be declared by an experiment; it is not automatically corrected.
    """
    def __init__(self, *, period, fast_period, slow_period, initialization):
        self.period = integer(period, "period", 1)
        fast_period = integer(fast_period, "fast_period", 1)
        slow_period = integer(slow_period, "slow_period", 1)
        if fast_period > slow_period:
            raise ValueError("fast_period must be <= slow_period")
        self.fast = 2.0 / (fast_period + 1)
        self.slow = 2.0 / (slow_period + 1)
        self.history = deque(maxlen=self.period + 1)
        self.filter = EMA(self.slow ** 2, initialization=initialization)
        self.alpha = None

    def step(self, x):
        x = finite(x, "x")
        self.history.append(x)
        er = 0.0
        if len(self.history) == self.period + 1:
            values = list(self.history)
            variation = math.fsum(abs(b - a) for a, b in zip(values, values[1:]))
            if variation > 0:
                er = abs(values[-1] - values[0]) / variation
        self.alpha = (er * (self.fast - self.slow) + self.slow) ** 2
        return self.filter.step(x, alpha=self.alpha)

    def process(self, values):
        return [self.step(x) for x in values]


class ButterworthSOS:
    """Digital -3dB cutoff with SciPy prewarping and second-order sections.

    The caller must supply uniformly spaced samples, including when selecting
    a subsample. A bare array cannot prove uniform spacing; grid validation is
    mandatory in the future data adapter. No zero-phase/future-data filtering.
    """
    def __init__(self, *, order, cutoff_hz, fs_hz, initialization):
        import numpy as np
        from scipy.signal import butter
        order = integer(order, "order", 1)
        self.fs_hz = positive(fs_hz, "fs_hz")
        self.cutoff_hz = positive(cutoff_hz, "cutoff_hz")
        if self.cutoff_hz >= self.fs_hz / 2:
            raise ValueError("cutoff_hz must be below Nyquist")
        if initialization not in {"zero", "first"}:
            raise ValueError("initialization must be 'zero' or 'first'")
        self.sos = butter(order, self.cutoff_hz, fs=self.fs_hz, output="sos")
        self.initialization = initialization
        self.state = np.zeros((len(self.sos), 2)) if initialization == "zero" else None

    def process(self, values):
        import numpy as np
        from scipy.signal import sosfilt, sosfilt_zi
        x = np.asarray([finite(v, "x") for v in values], dtype=np.float64)
        if len(x) == 0:
            return x
        if self.state is None:
            self.state = sosfilt_zi(self.sos) * x[0]
        y, state = sosfilt(self.sos, x, zi=self.state)
        if not np.isfinite(y).all() or not np.isfinite(state).all():
            raise ArithmeticError("non-finite filter state/output")
        self.state = state
        return y


def frozen_ema_dc_delay(alpha):
    """LTI DC delay in samples; not a delay formula for the full adaptive system."""
    a = alpha_value(alpha)
    delay = (1 - a) / a
    if not math.isfinite(delay):
        raise ArithmeticError("DC delay exceeds finite floating-point range")
    return delay


def frozen_ema_cutoff_radians(alpha):
    """Exact LTI -3dB cutoff, or None when no crossing exists below Nyquist."""
    a = alpha_value(alpha)
    if a == 1:
        return None
    # sin(w/2)=a/(2*sqrt(1-a)); avoid catastrophic cancellation in acos(1-eps).
    sine = a / (2.0 * math.sqrt(1.0 - a))
    return 2.0 * math.asin(sine) if sine <= 1 else None
