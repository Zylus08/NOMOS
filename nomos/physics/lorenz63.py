"""
NOMOS Lorenz-63 Chaotic Attractor Simulator
Agent B06 & A05
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class Lorenz63(BasePhysicalSystem):
    """
    Lorenz-63 Chaotic System:
    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y
    dz/dt = x * y - beta * z
    """

    def __init__(self, sigma: float = 10.0, rho: float = 28.0, beta: float = 8.0 / 3.0):
        metadata = SystemMetadata(
            name="lorenz63",
            dimension=3,
            variable_names=("x", "y", "z"),
            parameter_names=("sigma", "rho", "beta"),
            is_conservative=False,
            is_chaotic=True,
            description="Lorenz-63 3D chaotic attractor",
        )
        super().__init__(
            metadata,
            {"sigma": float(sigma), "rho": float(rho), "beta": float(beta)},
        )
        self.sigma = float(sigma)
        self.rho = float(rho)
        self.beta = float(beta)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        x, y, z = state[0], state[1], state[2]
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        return np.array([dx, dy, dz], dtype=np.float64)

    def phase_space_divergence_rate(self) -> float:
        # Phase volume contraction divergence div(f) = -(sigma + 1 + beta)
        return -(self.sigma + 1.0 + self.beta)

    def ground_truth_symbolic(self) -> Dict[str, str]:
        return {
            "x": f"-{self.sigma:.4g}*x + {self.sigma:.4g}*y",
            "y": f"{self.rho:.4g}*x - y - x*z",
            "z": f"x*y - {self.beta:.4g}*z",
        }

    def ground_truth_matrix(self, feature_names: List[str]) -> np.ndarray:
        P = len(feature_names)
        Xi = np.zeros((P, 3), dtype=np.float64)
        for i, name in enumerate(feature_names):
            if name == "x":
                Xi[i, 0] = -self.sigma
                Xi[i, 1] = self.rho
            elif name == "y":
                Xi[i, 0] = self.sigma
                Xi[i, 1] = -1.0
            elif name == "z":
                Xi[i, 2] = -self.beta
            elif name in ("x*z", "z*x", "x z", "z x"):
                Xi[i, 1] = -1.0
            elif name in ("x*y", "y*x", "x y", "y x"):
                Xi[i, 2] = 1.0
        return Xi
