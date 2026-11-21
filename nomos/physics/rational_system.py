"""
NOMOS Rational Kinetics Dynamical System Simulator
Milestone M2 — Phase 7 Benchmark Expansion
Agent B05
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class RationalKineticsSystem(BasePhysicalSystem):
    """
    Michaelis-Menten / Hill Rational Kinetics System:
    dx/dt = Vm * x / (Km + x) - d * x
    dy/dt = alpha * x - gamma * y
    Contains non-polynomial rational expression requiring division in hypothesis class.
    """

    def __init__(self, Vm: float = 2.0, Km: float = 1.0, d: float = 0.5, alpha: float = 1.0, gamma: float = 0.8):
        metadata = SystemMetadata(
            name="rational_kinetics",
            dimension=2,
            variable_names=("x", "y"),
            parameter_names=("Vm", "Km", "d", "alpha", "gamma"),
            is_conservative=False,
            is_chaotic=False,
            description="Nonlinear rational enzyme reaction system",
        )
        super().__init__(
            metadata,
            {"Vm": float(Vm), "Km": float(Km), "d": float(d), "alpha": float(alpha), "gamma": float(gamma)},
        )
        self.Vm = float(Vm)
        self.Km = float(Km)
        self.d = float(d)
        self.alpha = float(alpha)
        self.gamma = float(gamma)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        x, y = state[0], state[1]
        # Protect denominator
        denom = max(1e-6, self.Km + x)
        dx = (self.Vm * x) / denom - self.d * x
        dy = self.alpha * x - self.gamma * y
        return np.array([dx, dy], dtype=np.float64)

    def ground_truth_symbolic(self) -> Dict[str, str]:
        return {
            "x": f"({self.Vm:.4g}*x) / ({self.Km:.4g} + x) - {self.d:.4g}*x",
            "y": f"{self.alpha:.4g}*x - {self.gamma:.4g}*y",
        }
