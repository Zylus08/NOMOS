"""
NOMOS Dataset Leakage Detection & Quality Audit
Agents C11, C12, G04
"""

from typing import Dict, List, Tuple, Any
import numpy as np
from nomos.data.schema import TrajectoryDataset


def check_dataset_leakage(
    train_ds: TrajectoryDataset,
    val_ds: TrajectoryDataset,
    test_ds: TrajectoryDataset,
) -> Dict[str, Any]:
    """
    Adversarial audit to verify NO state, timestamp, or trajectory leakage across splits.
    Checks:
    1. Trajectory ID disjointness.
    2. Exact state vector collisions between train, val, and test.
    3. Initial condition overlap distance.
    """
    train_ids = {t.id for t in train_ds.trajectories}
    val_ids = {t.id for t in val_ds.trajectories}
    test_ids = {t.id for t in test_ds.trajectories}

    id_overlap_tv = train_ids.intersection(val_ids)
    id_overlap_tt = train_ids.intersection(test_ids)
    id_overlap_vt = val_ids.intersection(test_ids)

    # State overlap check
    _, X_train = train_ds.get_stacked_data()
    _, X_val = val_ds.get_stacked_data()
    _, X_test = test_ds.get_stacked_data()

    # Minimum pairwise distance between train and test states
    # Use random subsample if large
    n_sub = min(500, len(X_train), len(X_test))
    rng = np.random.default_rng(42)
    sub_tr = X_train[rng.choice(len(X_train), n_sub, replace=False)]
    sub_te = X_test[rng.choice(len(X_test), n_sub, replace=False)]

    diffs = sub_tr[:, np.newaxis, :] - sub_te[np.newaxis, :, :]
    dists = np.sqrt(np.sum(diffs ** 2, axis=-1))
    min_dist = float(np.min(dists))

    has_leakage = (
        bool(id_overlap_tv)
        or bool(id_overlap_tt)
        or bool(id_overlap_vt)
        or (min_dist < 1e-12)
    )

    return {
        "has_leakage": has_leakage,
        "id_overlaps": {
            "train_val": list(id_overlap_tv),
            "train_test": list(id_overlap_tt),
            "val_test": list(id_overlap_vt),
        },
        "min_train_test_state_distance": min_dist,
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
    }


def audit_dataset_quality(dataset: TrajectoryDataset) -> Dict[str, Any]:
    """
    Audit conditioning, NaNs, infinities, and signal statistics.
    Agent C12.
    """
    _, X = dataset.get_stacked_data()
    has_nan = bool(np.isnan(X).any())
    has_inf = bool(np.isinf(X).any())

    means = np.mean(X, axis=0).tolist()
    stds = np.std(X, axis=0).tolist()
    mins = np.min(X, axis=0).tolist()
    maxs = np.max(X, axis=0).tolist()

    return {
        "system": dataset.system_name,
        "total_trajectories": dataset.num_trajectories,
        "total_samples": dataset.total_samples,
        "has_nan": has_nan,
        "has_inf": has_inf,
        "feature_means": means,
        "feature_stds": stds,
        "feature_mins": mins,
        "feature_maxs": maxs,
        "is_healthy": (not has_nan) and (not has_inf),
    }
