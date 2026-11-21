"""
NOMOS Lotka-Volterra Predator-Prey Simulator
Agent B05
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class LotkaVolterra(BasePhysicalSystem):
    """
    Lotka-Volterra Predator-Prey Model:
    dx/dt = alpha * x - beta * x * y
    dy/dt = delta * x * y - gamma * y
    """

    def __init__(
        self, alpha: float = 1.5, beta: float = 1.0, gamma: float = 3.0, delta: float = 1.0
    ):
        metadata = SystemMetadata(
            name="lotka_volterra",
            dimension=2,
            variable_names=("x", "y"),
            parameter_names=("alpha", "beta", "gamma", "delta"),
            is_conservative=True,
            is_chaotic=False,
            description="Lotka-Volterra predator-prey dynamics",
        )
        super().__init__(
            metadata,
            {
                "alpha": float(alpha),
                "beta": float(beta),
                "gamma": float(gamma),
                "delta": float(delta),
            },
        )
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.gamma = float(gamma)
        self.delta = float(delta)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        x, y = state[0], state[1]
        dx = self.alpha * x - self.beta * x * y
        dy = self.delta * x * y - self.gamma * y
        return np.array([dx, dy], dtype=np.float64)

    def conserved_quantity(self, state: np.ndarray) -> float:
        # First integral V(x, y) = delta * x - gamma * ln(x) + beta * y - alpha * ln(y)
        x, y = state[0], state[1]
        if x <= 0 or y <= 0:
            return float("nan")
        return (
            self.delta * x
            - self.gamma * np.log(x)
            + self.beta * y
            - self.alpha * np.log(y)
        )

    def ground_truth_symbolic(self) -> Dict[str, str]:
        return {
            "x": f"{self.alpha:.4g}*x - {self.beta:.4g}*x*y",
            "y": f"{self.delta:.4g}*x*y - {self.gamma:.4g}*y",
        }

    def ground_truth_matrix(self, feature_names: List[str]) -> np.ndarray:
        P = len(feature_names)
        Xi = np.zeros((P, 2), dtype=np.float64)
        for i, name in enumerate(feature_names):
            if name == "x":
                Xi[i, 0] = self.alpha
            elif name in ("x*y", "y*x", "x y", "y x"):
                Xi[i, 0] = -self.beta
                Xi[i, 1] = self.delta
            elif name == "y":
                Xi[i, 1] = -self.gamma
        return Xi
