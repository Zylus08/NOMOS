"""
NOMOS Base PDE Simulator Architecture
Phase 2: Numerical PDE Simulators
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from nomos.pde.schema import (
    BoundaryConditionType,
    Grid1D,
    TimeGrid,
    SpatiotemporalField,
)


class BasePDESimulator(ABC):
    """
    Abstract base class for high-precision 1D spatiotemporal PDE simulators.
    Enforces clean separation between ground-truth physics and learner interfaces.
    """

    def __init__(
        self,
        name: str,
        parameters: Dict[str, float],
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
        domain: Tuple[float, float] = (0.0, 2.0 * np.pi),
    ):
        self.name = name
        self.parameters = dict(parameters)
        self.boundary_condition = boundary_condition
        self.domain = domain

    @abstractmethod
    def rhs_spatial(self, u: np.ndarray, x: np.ndarray) -> np.ndarray:
        """
        Compute true spatial right-hand side f(u, u_x, u_xx, ...) such that u_t = f.
        Input u shape: (N,) or (N, C). Output shape: identical.
        """
        pass

    @abstractmethod
    def simulate(
        self,
        u0: np.ndarray,
        grid: Grid1D,
        time_grid: TimeGrid,
        noise_level: float = 0.0,
        random_seed: Optional[int] = None,
    ) -> SpatiotemporalField:
        """
        Execute high-precision numerical time integration.
        Returns SpatiotemporalField complete with evaluator metadata and true derivatives.
        """
        pass

    @abstractmethod
    def analytical_solution(
        self, x: np.ndarray, t: float, u0_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> Optional[np.ndarray]:
        """Return analytical reference solution if available for verification."""
        pass

    def compute_invariant(self, u: np.ndarray, dx: float) -> Optional[float]:
        """Compute conserved quantity (mass, energy, momentum) for stability verification."""
        return None
