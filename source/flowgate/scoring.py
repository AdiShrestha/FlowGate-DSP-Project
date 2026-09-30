"""Prior-window residual standardization with explicit warmup and scale floor."""
import math
from collections import deque
from statistics import mean, median, stdev
from .validation import finite, integer, positive


class CausalResidualScore:
    def __init__(self, *, window, min_history, scale_floor, estimator):
        self.window = integer(window, "window", 2)
        self.min_history = integer(min_history, "min_history", 2)
        if self.min_history > self.window:
            raise ValueError("min_history must be <= window")
        self.scale_floor = positive(scale_floor, "scale_floor in residual units")
        if estimator not in {"std", "mad"}:
            raise ValueError("estimator must be 'std' or 'mad'")
        self.estimator = estimator
        self.history = deque(maxlen=self.window)

    def step(self, residual):
        residual = finite(residual, "residual")
        score = None
        if len(self.history) >= self.min_history:
            values = list(self.history)
            if self.estimator == "std":
                center = mean(values)
                scale = stdev(values)
            else:
                center = median(values)
                # Gaussian consistency constant, a definition rather than a measured outcome.
                scale = 1.482602218505602 * median(abs(x - center) for x in values)
            if not math.isfinite(center) or not math.isfinite(scale):
                raise ArithmeticError("non-finite prior residual center/scale")
            score = abs(residual - center) / max(scale, self.scale_floor)
            if not math.isfinite(score):
                raise ArithmeticError("non-finite standardized residual")
        self.history.append(residual)
        return score
