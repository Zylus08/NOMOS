"""
NOMOS End-to-End Pipeline Verification Tests
Tests discovery across all 5 benchmark systems
"""

import numpy as np
import pytest
from nomos.physics import get_benchmark_system, simulate_system
from nomos.data import Trajectory, TrajectoryDataset, IsolatedLearnerDataset
from nomos.pipeline import DiscoveryEngine, DiscoveryConfig
from nomos.evaluation import evaluate_rollout, evaluate_equation_support, evaluate_coefficient_error


@pytest.mark.parametrize("sys_name,lib_type,thresh", [
    ("harmonic_oscillator", "polynomial", 0.05),
    ("damped_oscillator", "polynomial", 0.05),
    ("nonlinear_pendulum", "composite", 0.05),
    ("lotka_volterra", "polynomial", 0.05),
    ("lorenz63", "polynomial", 0.1),
])
def test_pipeline_noiseless_recovery(sys_name, lib_type, thresh):
    sys = get_benchmark_system(sys_name)
    t = np.linspace(0.0, 10.0, 1001)
    x0 = np.ones(sys.dimension)
    sim = simulate_system(sys, x0, (0.0, 10.0), t_eval=t)

    traj = Trajectory(id="traj_0", t=sim.t, x=sim.x, x_dot_true=sim.x_dot_true)
    ds = TrajectoryDataset(system_name=sys_name, variable_names=list(sys.variable_names), trajectories=[traj])
    isolated = IsolatedLearnerDataset(ds)

    cfg = DiscoveryConfig(
        diff_method="finite_difference",
        diff_order=4,
        library_type=lib_type,
        poly_degree=2,
        threshold=thresh,
    )
    engine = DiscoveryEngine(cfg)
    out = engine.fit(isolated)

    # 1. Closed-loop rollout check
    rollout_res = evaluate_rollout(out.coef, out.library, sim.x, sim.t)
    assert rollout_res.is_stable, f"Rollout unstable on {sys_name}"
    # Relative rollout error should be very small for noiseless linear/periodic systems
    if sys_name != "lorenz63":
        assert rollout_res.relative_rmse < 0.05, f"Rollout error too high on {sys_name}: {rollout_res.relative_rmse}"

    # 2. Support recovery check
    Xi_true = sys.ground_truth_matrix(out.feature_names)
    supp_eval = evaluate_equation_support(out.coef != 0, Xi_true != 0)
    assert supp_eval["exact_match"], f"Exact support recovery failed for {sys_name}: disc={out.coef != 0}, true={Xi_true != 0}"

    # 3. Coefficient relative error
    coef_eval = evaluate_coefficient_error(out.coef, Xi_true)
    assert coef_eval["active_relative_error"] < 0.02, f"Coefficient error too high: {coef_eval}"
