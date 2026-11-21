"""
NOMOS Trajectory-Disjoint Splitting
Agent C04
"""

from typing import Dict, List, Tuple
import numpy as np
from nomos.data.schema import TrajectoryDataset, Trajectory


def split_trajectories_disjoint(
    dataset: TrajectoryDataset,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2,
    seed: int = 42,
) -> Tuple[TrajectoryDataset, TrajectoryDataset, TrajectoryDataset]:
    """
    Strictly split dataset by WHOLE TRAJECTORIES.
    Guarantees no state from test trajectories appears in train or validation sets.
    """
    total = train_ratio + val_ratio + test_ratio
    train_ratio /= total
    val_ratio /= total
    test_ratio /= total

    n_traj = dataset.num_trajectories
    if n_traj < 3:
        raise ValueError(f"Need at least 3 trajectories to split train/val/test disjointly, got {n_traj}")

    rng = np.random.default_rng(seed)
    indices = np.arange(n_traj)
    rng.shuffle(indices)

    n_train = max(1, int(round(n_traj * train_ratio)))
    n_val = max(1, int(round(n_traj * val_ratio)))
    if n_train + n_val >= n_traj:
        n_train = max(1, n_traj - 2)
        n_val = 1
    n_test = n_traj - n_train - n_val

    train_idx = indices[:n_train]
    val_idx = indices[n_train : n_train + n_val]
    test_idx = indices[n_train + n_val :]

    train_trajs = [dataset.trajectories[i] for i in train_idx]
    val_trajs = [dataset.trajectories[i] for i in val_idx]
    test_trajs = [dataset.trajectories[i] for i in test_idx]

    train_ds = TrajectoryDataset(
        system_name=dataset.system_name,
        variable_names=list(dataset.variable_names),
        trajectories=train_trajs,
        noise_level=dataset.noise_level,
        dt_nominal=dataset.dt_nominal,
        provenance={"split": "train", "parent_hash": dataset.dataset_hash, "traj_ids": [t.id for t in train_trajs]},
    )
    val_ds = TrajectoryDataset(
        system_name=dataset.system_name,
        variable_names=list(dataset.variable_names),
        trajectories=val_trajs,
        noise_level=dataset.noise_level,
        dt_nominal=dataset.dt_nominal,
        provenance={"split": "val", "parent_hash": dataset.dataset_hash, "traj_ids": [t.id for t in val_trajs]},
    )
    test_ds = TrajectoryDataset(
        system_name=dataset.system_name,
        variable_names=list(dataset.variable_names),
        trajectories=test_trajs,
        noise_level=dataset.noise_level,
        dt_nominal=dataset.dt_nominal,
        provenance={"split": "test", "parent_hash": dataset.dataset_hash, "traj_ids": [t.id for t in test_trajs]},
    )

    return train_ds, val_ds, test_ds
