"""
NOMOS Scientific Data & Integrity Tests
Agents G04, C04, C09, C11, C12
"""

import numpy as np
import pytest
from nomos.physics import get_benchmark_system, simulate_system
from nomos.data import (
    Trajectory,
    TrajectoryDataset,
    sample_initial_conditions,
    split_trajectories_disjoint,
    inject_gaussian_noise,
    sample_irregular_time,
    apply_missing_observations,
    IsolatedLearnerDataset,
    check_dataset_leakage,
    audit_dataset_quality,
)


@pytest.fixture
def synthetic_dataset():
    sys = get_benchmark_system("harmonic_oscillator")
    trajs = []
    t = np.linspace(0.0, 5.0, 101)
    for i in range(5):
        x0 = np.array([1.0 + 0.2 * i, 0.5 * i])
        sim = simulate_system(sys, x0, (0.0, 5.0), t_eval=t)
        trajs.append(Trajectory(id=f"traj_{i}", t=sim.t, x=sim.x, x_dot_true=sim.x_dot_true))
    return TrajectoryDataset(system_name="harmonic_oscillator", variable_names=["x", "v"], trajectories=trajs)


def test_trajectory_disjoint_splitting(synthetic_dataset):
    train_ds, val_ds, test_ds = split_trajectories_disjoint(
        synthetic_dataset, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2
    )
    leakage = check_dataset_leakage(train_ds, val_ds, test_ds)
    assert not leakage["has_leakage"]
    assert len(leakage["id_overlaps"]["train_val"]) == 0
    assert len(leakage["id_overlaps"]["train_test"]) == 0
    assert len(leakage["id_overlaps"]["val_test"]) == 0
    assert leakage["min_train_test_state_distance"] > 1e-6


def test_metadata_isolation_sandbox(synthetic_dataset):
    isolated = IsolatedLearnerDataset(synthetic_dataset)
    for traj in isolated.trajectories:
        assert traj.x_clean is None, "x_clean leaked to isolated learner!"
        assert traj.x_dot_true is None, "x_dot_true leaked to isolated learner!"
        # Check no hidden ground truth parameters in metadata
        assert "true_params" not in traj.metadata


def test_gaussian_noise_injection():
    t = np.linspace(0, 1, 100)
    x = np.sin(t)[:, np.newaxis]
    tr = Trajectory(id="test", t=t, x=x)
    noisy_tr = inject_gaussian_noise(tr, noise_ratio=0.05, seed=42)
    assert noisy_tr.x_clean is not None
    assert not np.array_equal(noisy_tr.x, tr.x)
    # Check noise level within statistical tolerance
    diff = noisy_tr.x - tr.x
    measured_noise = np.std(diff) / np.std(tr.x)
    assert abs(measured_noise - 0.05) < 0.02


def test_dataset_quality_audit(synthetic_dataset):
    report = audit_dataset_quality(synthetic_dataset)
    assert report["is_healthy"]
    assert not report["has_nan"]
    assert not report["has_inf"]
    assert report["total_trajectories"] == 5
