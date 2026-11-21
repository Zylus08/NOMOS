"""
NOMOS Duffing Oscillator Simulator
Milestone M2 — Phase 7 Benchmark Expansion
Agent B01
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class DuffingOscillator(BasePhysicalSystem):
    """
    Duffing Oscillator:
    dx/dt = v
    dv/dt = -delta * v - alpha * x - beta * x^3
    Features cubic non-linearity and double-well potential when alpha < 0, beta > 0.
    """

    def __init__(self, delta: float = 0.2, alpha: float = -1.0, beta: float = 1.0):
        metadata = SystemMetadata(
            name="duffing_oscillator",
            dimension=2,
            variable_names=("x", "v"),
            parameter_names=("delta", "alpha", "beta"),
            is_conservative=False,
            is_chaotic=False,
            description="Duffing oscillator with cubic stiffness and damping",
        )
        super().__init__(
            metadata,
            {"delta": float(delta), "alpha": float(alpha), "beta": float(beta)},
        )
        self.delta = float(delta)
        self.alpha = float(alpha)
        self.beta = float(beta)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        x, v = state[0], state[1]
        dx = v
        dv = -self.delta * v - self.alpha * x - self.beta * (x ** 3)
        return np.array([dx, dv], dtype=np.float64)

    def ground_truth_symbolic(self) -> Dict[str, str]:
        c_v = -self.delta
        c_x = -self.alpha
        c_x3 = -self.beta
        return {
            "x": "v",
            "v": f"{c_v:.4g}*v + {c_x:.4g}*x + {c_x3:.4g}*x**3",
        }
