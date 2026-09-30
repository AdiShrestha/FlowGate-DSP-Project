"""FlowGate numerical primitives. No acquisition, experiment, or result runs on import."""
from .filters import EMA, AdaptiveAlpha, KAMA, ButterworthSOS, ema
from .shedding import StrideShedder, EMAPipeline, FilterObservation
from .scoring import CausalResidualScore
from .metrics import point_metrics, event_metrics, pareto_mask
from .queue import fcfs_schedule, QueueObservation

__all__ = ["EMA", "AdaptiveAlpha", "KAMA", "ButterworthSOS", "ema", "StrideShedder",
           "EMAPipeline", "FilterObservation", "CausalResidualScore", "point_metrics",
           "event_metrics", "pareto_mask", "fcfs_schedule", "QueueObservation"]
