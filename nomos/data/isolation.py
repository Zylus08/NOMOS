"""
NOMOS Metadata Access Isolation & Blind Discovery Sandbox
Agents C09 & C11
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from nomos.data.schema import Trajectory, TrajectoryDataset


class IsolatedLearnerDataset:
    """
    Strict sandbox wrapper exposed to the Discovery Engine during fitting.
    Guarantees:
    - Learner CANNOT access ground truth equations.
    - Learner CANNOT access ground truth ODE parameters.
    - Learner CANNOT access uncorrupted clean signals or true derivatives during training.
    - Only provides observed timestamps t and states x.
    """

    def __init__(self, dataset: TrajectoryDataset):
        self._system_name = dataset.system_name
        self._variable_names = tuple(dataset.variable_names)
        self._trajectories = []

        for traj in dataset.trajectories:
            # Strip all evaluator-only fields
            safe_traj = Trajectory(
                id=traj.id,
                t=np.copy(traj.t),
                x=np.copy(traj.x),
                x_clean=None,       # STRIPPED
                x_dot_true=None,    # STRIPPED
                metadata={"id": traj.id},  # STRIPPED of secret parameters
            )
            self._trajectories.append(safe_traj)

    @property
    def system_name(self) -> str:
        return self._system_name

    @property
    def variable_names(self) -> Tuple[str, ...]:
        return self._variable_names

    @property
    def num_trajectories(self) -> int:
        return len(self._trajectories)

    @property
    def trajectories(self) -> List[Trajectory]:
        # Return read-only copy
        return list(self._trajectories)

    def get_stacked_data(self) -> Tuple[np.ndarray, np.ndarray]:
        all_t = np.concatenate([tr.t for tr in self._trajectories], axis=0)
        all_x = np.concatenate([tr.x for tr in self._trajectories], axis=0)
        return all_t, all_x
