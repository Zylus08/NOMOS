"""
NOMOS Nonlinear Pendulum Simulator & Small-Angle Comparison
Agents B03 & B04
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class NonlinearPendulum(BasePhysicalSystem):
    """
    Simple Nonlinear Pendulum:
    d theta / dt = omega
    d omega / dt = - (g / L) * sin(theta)
    """

    def __init__(self, g: float = 9.81, L: float = 1.0):
        metadata = SystemMetadata(
            name="nonlinear_pendulum",
            dimension=2,
            variable_names=("theta", "omega"),
            parameter_names=("g", "L"),
            is_conservative=True,
            is_chaotic=False,
            description="Nonlinear gravity pendulum",
        )
        super().__init__(metadata, {"g": float(g), "L": float(L)})
        self.g = float(g)
        self.L = float(L)
        self.omega0_sq = float(g / L)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        theta, omega = state[0], state[1]
        d_theta = omega
        d_omega = -self.omega0_sq * np.sin(theta)
        return np.array([d_theta, d_omega], dtype=np.float64)

    def conserved_quantity(self, state: np.ndarray) -> float:
        # Energy per unit mass: E = 0.5 * L^2 * omega^2 - g * L * cos(theta)
        theta, omega = state[0], state[1]
        return 0.5 * (self.L ** 2) * (omega ** 2) - self.g * self.L * np.cos(theta)

    def small_angle_divergence(
        self, t_eval: np.ndarray, theta0: float, omega0: float = 0.0
    ) -> Dict[str, Any]:
        """
        Compare exact nonlinear pendulum trajectory vs linear small-angle approx (sin theta ~ theta).
        Agent B04 role.
        """
        from nomos.physics.solvers import simulate_system
        nonlin_sol = simulate_system(
            self, np.array([theta0, omega0]), (t_eval[0], t_eval[-1]), t_eval=t_eval
        )

        w = np.sqrt(self.omega0_sq)
        theta_lin = theta0 * np.cos(w * t_eval) + (omega0 / w) * np.sin(w * t_eval)

        divergence = np.max(np.abs(nonlin_sol.x[:, 0] - theta_lin))
        rel_div = divergence / (abs(theta0) + 1e-12)

        return {
            "theta0_deg": float(np.degrees(theta0)),
            "theta0_rad": float(theta0),
            "max_divergence_rad": float(divergence),
            "relative_divergence": float(rel_div),
        }

    def ground_truth_symbolic(self) -> Dict[str, str]:
        return {
            "theta": "omega",
            "omega": f"-{self.omega0_sq:.4g}*sin(theta)",
        }

    def ground_truth_matrix(self, feature_names: List[str]) -> np.ndarray:
        P = len(feature_names)
        Xi = np.zeros((P, 2), dtype=np.float64)
        for i, name in enumerate(feature_names):
            if name == "omega":
                Xi[i, 0] = 1.0
            elif name in ("sin(theta)", "sin(1*theta)"):
                Xi[i, 1] = -self.omega0_sq
        return Xi
