"""
NOMOS Core Optimizer Interfaces
Agent A02 & D01
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import numpy as np


@dataclass
class OptimizerResult:
    """Standardized output of sparse regression optimizer."""
    coef: np.ndarray  # Shape: (P, n)
    support: np.ndarray  # Boolean mask of shape (P, n)
    iterations: int
    converged: bool
    residual_norm: float
    loss_history: List[float]
    metadata: Dict[str, Any]


class BaseSparseOptimizer(ABC):
    """
    Abstract base class for sparse regression solvers identifying Xi in:
        X_dot = Theta(X) * Xi
    """

    @abstractmethod
    def fit(self, Theta: np.ndarray, X_dot: np.ndarray) -> OptimizerResult:
        """Fit sparse coefficients Xi minimizing residual and sparsity penalty."""
        pass
