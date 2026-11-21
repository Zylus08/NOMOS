"""
NOMOS Evaluation Package Module
"""

from nomos.evaluation.metrics import evaluate_derivative_prediction, evaluate_chaotic_attractor_statistics
from nomos.evaluation.rollout import simulate_discovered_model, evaluate_rollout, RolloutResult
from nomos.evaluation.support import evaluate_equation_support
from nomos.evaluation.coefficients import evaluate_coefficient_error
from nomos.evaluation.baselines import OLSBaseline, PySINDyAdapter
from nomos.evaluation.aggregation import aggregate_experiment_runs

__all__ = [
    "evaluate_derivative_prediction",
    "evaluate_chaotic_attractor_statistics",
    "simulate_discovered_model",
    "evaluate_rollout",
    "RolloutResult",
    "evaluate_equation_support",
    "evaluate_coefficient_error",
    "OLSBaseline",
    "PySINDyAdapter",
    "aggregate_experiment_runs",
]
