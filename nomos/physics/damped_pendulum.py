"""
NOMOS Damped Nonlinear Pendulum Simulator
Milestone M2 — Phase 7 Benchmark Expansion
Agent B03
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class DampedPendulum(BasePhysicalSystem):
    """
    Damped Simple Pendulum:
    d theta / dt = omega
    d omega / dt = -b * omega - (g / L) * sin(theta)
    """

    def __init__(self, b: float = 0.25, g: float = 9.81, L: float = 1.0):
        metadata = SystemMetadata(
            name="damped_pendulum",
            dimension=2,
            variable_names=("theta", "omega"),
            parameter_names=("b", "g", "L"),
            is_conservative=False,
            is_chaotic=False,
            description="Viscously damped gravity pendulum",
        )
        super().__init__(metadata, {"b": float(b), "g": float(g), "L": float(L)})
        self.b = float(b)
        self.g = float(g)
        self.L = float(L)
        self.omega0_sq = float(g / L)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        theta, omega = state[0], state[1]
        d_theta = omega
        d_omega = -self.b * omega - self.omega0_sq * np.sin(theta)
        return np.array([d_theta, d_omega], dtype=np.float64)

    def ground_truth_symbolic(self) -> Dict[str, str]:
        return {
            "theta": "omega",
            "omega": f"-{self.b:.4g}*omega - {self.omega0_sq:.4g}*sin(theta)",
        }
