"""
NOMOS Core Evaluator Interfaces
Agent F01 & F04
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import numpy as np


@dataclass
class EvaluationReport:
    """Standardized report for discovered dynamical system quality."""
    derivative_rmse: float
    derivative_r2: float
    short_horizon_rollout_rmse: float
    long_horizon_rollout_rmse: float
    support_precision: float
    support_recall: float
    support_f1: float
    exact_support_recovered: bool
    coefficient_relative_error: float
    frobenius_error: float
    is_stable: bool
    rollout_failed: bool
    metrics_by_variable: Dict[str, Dict[str, float]]
    metadata: Dict[str, Any]
