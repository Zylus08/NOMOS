"""
NOMOS Harmonic Oscillator Simulator
Agent B01
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class HarmonicOscillator(BasePhysicalSystem):
    """
    Linear Harmonic Oscillator:
    dx/dt = v
    dv/dt = -omega0^2 * x
    """

    def __init__(self, omega0: float = 1.0):
        metadata = SystemMetadata(
            name="harmonic_oscillator",
            dimension=2,
            variable_names=("x", "v"),
            parameter_names=("omega0",),
            is_conservative=True,
            is_chaotic=False,
            description="Linear undamped harmonic oscillator",
        )
        super().__init__(metadata, {"omega0": float(omega0)})
        self.omega0 = float(omega0)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        x, v = state[0], state[1]
        dx = v
        dv = -(self.omega0 ** 2) * x
        return np.array([dx, dv], dtype=np.float64)

    def analytical_solution(self, t: np.ndarray, x0: np.ndarray) -> np.ndarray:
        x_init, v_init = x0[0], x0[1]
        w = self.omega0
        x_t = x_init * np.cos(w * t) + (v_init / w) * np.sin(w * t)
        v_t = -x_init * w * np.sin(w * t) + v_init * np.cos(w * t)
        return np.column_stack([x_t, v_t])

    def conserved_quantity(self, state: np.ndarray) -> float:
        # Total mechanical energy E = 0.5 * v^2 + 0.5 * omega0^2 * x^2
        x, v = state[0], state[1]
        return 0.5 * (v ** 2) + 0.5 * (self.omega0 ** 2) * (x ** 2)

    def ground_truth_symbolic(self) -> Dict[str, str]:
        return {
            "x": "v",
            "v": f"-{self.omega0**2:.4g}*x",
        }

    def ground_truth_matrix(self, feature_names: List[str]) -> np.ndarray:
        P = len(feature_names)
        Xi = np.zeros((P, 2), dtype=np.float64)
        for i, name in enumerate(feature_names):
            if name == "v":
                Xi[i, 0] = 1.0
            elif name == "x":
                Xi[i, 1] = -(self.omega0 ** 2)
        return Xi
