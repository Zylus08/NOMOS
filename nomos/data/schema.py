"""
NOMOS Trajectory Dataset Schema & Cryptographic Integrity
Agents C01, C08, C10
"""

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


@dataclass
class Trajectory:
    """Individual trajectory instance."""
    id: str
    t: np.ndarray             # Shape: (M,)
    x: np.ndarray             # Observed states, Shape: (M, n)
    x_clean: Optional[np.ndarray] = None  # Uncorrupted states (evaluator only)
    x_dot_true: Optional[np.ndarray] = None  # True continuous derivative (evaluator only)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_sha256(self) -> str:
        """Compute SHA-256 checksum over time and state matrices."""
        hasher = hashlib.sha256()
        hasher.update(self.t.tobytes())
        hasher.update(self.x.tobytes())
        return hasher.hexdigest()


@dataclass
class TrajectoryDataset:
    """
    Collection of physical trajectories.
    Enforces immutability and provenance tracking.
    """
    system_name: str
    variable_names: List[str]
    trajectories: List[Trajectory]
    noise_level: float = 0.0
    dt_nominal: float = 0.01
    provenance: Dict[str, Any] = field(default_factory=dict)
    dataset_hash: str = ""

    def __post_init__(self):
        if not self.dataset_hash:
            self.dataset_hash = self.compute_integrity_hash()

    def compute_integrity_hash(self) -> str:
        hasher = hashlib.sha256()
        hasher.update(self.system_name.encode("utf-8"))
        for traj in self.trajectories:
            hasher.update(traj.compute_sha256().encode("utf-8"))
        return hasher.hexdigest()

    @property
    def num_trajectories(self) -> int:
        return len(self.trajectories)

    @property
    def dimension(self) -> int:
        return len(self.variable_names)

    @property
    def total_samples(self) -> int:
        return sum(len(traj.t) for traj in self.trajectories)

    def get_stacked_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Stack all trajectories into concatenated time and state matrices.
        Returns: (T_stacked (N,), X_stacked (N, n))
        """
        all_t = np.concatenate([tr.t for tr in self.trajectories], axis=0)
        all_x = np.concatenate([tr.x for tr in self.trajectories], axis=0)
        return all_t, all_x
