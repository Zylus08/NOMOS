"""
NOMOS Physics Base & Invariant Tracking
Roles B10 & B09
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from nomos.core.system import DynamicalSystem, SystemMetadata


class BasePhysicalSystem(DynamicalSystem):
    """
    Base physical system with phase-space validation and conservation checks.
    """

    def compute_energy_drift(self, trajectory: np.ndarray) -> Optional[float]:
        """
        Compute relative maximum energy variation |E(t) - E(0)| / (|E(0)| + 1e-12).
        Returns None if system is dissipative or non-conservative.
        """
        if not self.metadata.is_conservative:
            return None
        energies = np.array([self.conserved_quantity(pt) for pt in trajectory])
        if any(e is None for e in energies):
            return None
        e0 = energies[0]
        max_diff = np.max(np.abs(energies - e0))
        return float(max_diff / (abs(e0) + 1e-12))

    def validate_trajectory(self, trajectory: np.ndarray) -> bool:
        """Verify no NaNs, Infs, or unrealistic explosion."""
        if not np.all(np.isfinite(trajectory)):
            return False
        if np.max(np.abs(trajectory)) > 1e6:
            return False
        return True
