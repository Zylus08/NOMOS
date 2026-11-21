"""
NOMOS Damped Oscillator Simulator
Agent B02
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class DampedOscillator(BasePhysicalSystem):
    """
    Damped Harmonic Oscillator:
    dx/dt = v
    dv/dt = -omega0^2 * x - 2 * zeta * omega0 * v
    """

    def __init__(self, omega0: float = 1.0, zeta: float = 0.1):
        metadata = SystemMetadata(
            name="damped_oscillator",
            dimension=2,
            variable_names=("x", "v"),
            parameter_names=("omega0", "zeta"),
            is_conservative=False,
            is_chaotic=False,
            description="Viscously damped linear oscillator",
        )
        super().__init__(metadata, {"omega0": float(omega0), "zeta": float(zeta)})
        self.omega0 = float(omega0)
        self.zeta = float(zeta)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        x, v = state[0], state[1]
        dx = v
        dv = -(self.omega0 ** 2) * x - 2.0 * self.zeta * self.omega0 * v
        return np.array([dx, dv], dtype=np.float64)

    def analytical_solution(self, t: np.ndarray, x0: np.ndarray) -> np.ndarray:
        x_init, v_init = x0[0], x0[1]
        w0 = self.omega0
        z = self.zeta
        if z < 1.0:
            # Underdamped
            wd = w0 * np.sqrt(1.0 - z ** 2)
            alpha = z * w0
            A = x_init
            B = (v_init + alpha * x_init) / wd
            exp_term = np.exp(-alpha * t)
            x_t = exp_term * (A * np.cos(wd * t) + B * np.sin(wd * t))
            v_t = exp_term * (
                (-alpha * A + wd * B) * np.cos(wd * t)
                + (-alpha * B - wd * A) * np.sin(wd * t)
            )
            return np.column_stack([x_t, v_t])
        elif np.isclose(z, 1.0):
            # Critically damped
            alpha = w0
            A = x_init
            B = v_init + alpha * x_init
            exp_term = np.exp(-alpha * t)
            x_t = exp_term * (A + B * t)
            v_t = exp_term * (B - alpha * (A + B * t))
            return np.column_stack([x_t, v_t])
        else:
            # Overdamped
            gamma = w0 * np.sqrt(z ** 2 - 1.0)
            alpha = z * w0
            r1 = -alpha + gamma
            r2 = -alpha - gamma
            c1 = (v_init - r2 * x_init) / (r1 - r2)
            c2 = (r1 * x_init - v_init) / (r1 - r2)
            x_t = c1 * np.exp(r1 * t) + c2 * np.exp(r2 * t)
            v_t = c1 * r1 * np.exp(r1 * t) + c2 * r2 * np.exp(r2 * t)
            return np.column_stack([x_t, v_t])

    def ground_truth_symbolic(self) -> Dict[str, str]:
        c_x = -(self.omega0 ** 2)
        c_v = -2.0 * self.zeta * self.omega0
        return {
            "x": "v",
            "v": f"{c_x:.4g}*x + {c_v:.4g}*v",
        }

    def ground_truth_matrix(self, feature_names: List[str]) -> np.ndarray:
        P = len(feature_names)
        Xi = np.zeros((P, 2), dtype=np.float64)
        c_x = -(self.omega0 ** 2)
        c_v = -2.0 * self.zeta * self.omega0
        for i, name in enumerate(feature_names):
            if name == "v":
                Xi[i, 0] = 1.0
                Xi[i, 1] = c_v
            elif name == "x":
                Xi[i, 1] = c_x
        return Xi
