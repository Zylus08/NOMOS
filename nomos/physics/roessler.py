"""
NOMOS Rössler Chaotic Attractor Simulator
Milestone M2 — Phase 7 Benchmark Expansion
Agent B06
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.core.system import SystemMetadata
from nomos.physics.base import BasePhysicalSystem


class RoesslerSystem(BasePhysicalSystem):
    """
    Rössler Chaotic System:
    dx/dt = -y - z
    dy/dt = x + a * y
    dz/dt = b + z * (x - c) = b + x * z - c * z
    Simpler single-funnel chaotic attractor with spiral dynamics.
    """

    def __init__(self, a: float = 0.2, b: float = 0.2, c: float = 5.7):
        metadata = SystemMetadata(
            name="roessler",
            dimension=3,
            variable_names=("x", "y", "z"),
            parameter_names=("a", "b", "c"),
            is_conservative=False,
            is_chaotic=True,
            description="Rössler 3D spiral chaotic attractor",
        )
        super().__init__(metadata, {"a": float(a), "b": float(b), "c": float(c)})
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        x, y, z = state[0], state[1], state[2]
        dx = -y - z
        dy = x + self.a * y
        dz = self.b + z * (x - self.c)
        return np.array([dx, dy, dz], dtype=np.float64)

    def ground_truth_symbolic(self) -> Dict[str, str]:
        return {
            "x": "-y - z",
            "y": f"x + {self.a:.4g}*y",
            "z": f"{self.b:.4g} + x*z - {self.c:.4g}*z",
        }
