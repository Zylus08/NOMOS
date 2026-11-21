"""
NOMOS Van der Pol Oscillator Simulator
Milestone M2 — Phase 7 Benchmark Expansion
Agent B02
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class VanDerPolOscillator(BasePhysicalSystem):
    """
    Van der Pol Oscillator:
    dx/dt = v
    dv/dt = mu * (1 - x^2) * v - x = mu * v - mu * x^2 * v - x
    Self-excited non-conservative oscillator possessing a stable limit cycle.
    """

    def __init__(self, mu: float = 1.0):
        metadata = SystemMetadata(
            name="vanderpol_oscillator",
            dimension=2,
            variable_names=("x", "v"),
            parameter_names=("mu",),
            is_conservative=False,
            is_chaotic=False,
            description="Van der Pol relaxation oscillator with limit cycle",
        )
        super().__init__(metadata, {"mu": float(mu)})
        self.mu = float(mu)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        x, v = state[0], state[1]
        dx = v
        dv = self.mu * (1.0 - x ** 2) * v - x
        return np.array([dx, dv], dtype=np.float64)

    def ground_truth_symbolic(self) -> Dict[str, str]:
        return {
            "x": "v",
            "v": f"{self.mu:.4g}*v - {self.mu:.4g}*x**2*v - x",
        }
