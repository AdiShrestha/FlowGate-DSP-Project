"""Reject invalid observations rather than substituting or clipping them."""
import math
from numbers import Real


def finite(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a real number, excluding booleans")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def positive(value, name):
    value = finite(value, name)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def integer(value, name, minimum):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def alpha_value(value, name="alpha"):
    value = positive(value, name)
    if value > 1:
        raise ValueError(f"{name} must be <= 1")
    return value


def load_value(value):
    value = finite(value, "load")
    if not 0 <= value <= 1:
        raise ValueError("load must lie in [0, 1]; its provenance belongs to the caller")
    return value
