"""
NOMOS Core System Interfaces & Mathematical Contracts
Agent A01 & J02
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Any
import numpy as np


@dataclass(frozen=True)
class SystemMetadata:
    """Immutable metadata describing a physical dynamical system."""
    name: str
    dimension: int
    variable_names: Tuple[str, ...]
    parameter_names: Tuple[str, ...]
    is_conservative: bool = False
    is_chaotic: bool = False
    description: str = ""


class DynamicalSystem(ABC):
    """
    Abstract base class for all physical dynamical systems.
    Contracts:
    - Must define RHS: dx/dt = f(t, x, *args)
    - Must provide clean analytical solution if available
    - Must compute conserved quantities (Hamiltonian / First integrals) if applicable
    """

    def __init__(self, metadata: SystemMetadata, parameters: Dict[str, float]):
        self.metadata = metadata
        self.parameters = dict(parameters)

    @property
    def dimension(self) -> int:
        return self.metadata.dimension

    @property
    def variable_names(self) -> Tuple[str, ...]:
        return self.metadata.variable_names

    @abstractmethod
    def rhs(self, t: float, x: np.ndarray) -> np.ndarray:
        """Evaluate the continuous vector field f(t, x) -> dx/dt."""
        pass

    def analytical_solution(self, t: np.ndarray, x0: np.ndarray) -> Optional[np.ndarray]:
        """Return analytical trajectory if closed-form exists, else None."""
        return None

    def conserved_quantity(self, x: np.ndarray) -> Optional[float]:
        """Compute energy or first integral for state x, or None if dissipative."""
        return None

    def ground_truth_symbolic(self) -> Dict[str, str]:
        """
        Ground-truth string equations.
        CRITICAL: Never exposed to discovery engine during fitting.
        Only used by evaluation / verification agents.
        """
        return {}

    def ground_truth_matrix(self, feature_names: List[str]) -> np.ndarray:
        """
        True coefficient matrix Xi (P x n) corresponding to given feature names.
        Used strictly by evaluator roles for support and error metrics.
        """
        raise NotImplementedError
