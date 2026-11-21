"""
NOMOS Adversarial Validation & Red-Team Audit Tests
Agents G04, G08, G09, G10
"""

import numpy as np
import pytest
from nomos.physics import get_benchmark_system, simulate_system
from nomos.data import Trajectory, TrajectoryDataset, split_trajectories_disjoint, check_dataset_leakage
from nomos.library import PolynomialLibrary, TrigonometricLibrary, CompositeLibrary
from nomos.sparse import STLSQ
from nomos.pipeline import DiscoveryEngine, DiscoveryConfig


def test_adversarial_identifiability_harmonic_degeneracy():
    """
    Adversarial Test G08:
    Construct an intentionally collinear library containing both sin^2(x) + cos^2(x) and 1.
    Tests whether the system handles degeneracy and condition number explosion gracefully.
    """
    M = 100
    x = np.linspace(0, 2 * np.pi, M)[:, np.newaxis]
    sin2 = np.sin(x) ** 2
    cos2 = np.cos(x) ** 2
    ones = np.ones((M, 1))

    # Degenerate library: sin^2 + cos^2 - 1 = 0
    Theta = np.column_stack([ones, sin2, cos2])
    y = 2.0 * ones  # Constant derivative

    # Fit STLSQ
    opt = STLSQ(threshold=0.1, alpha=1e-3)
    res = opt.fit(Theta, y)

    # Must converge without crashing despite severe collinearity
    assert res.converged
    assert np.all(np.isfinite(res.coef))


def test_adversarial_inadequate_candidate_library():
    """
    Adversarial Test G09:
    Attempt to discover nonlinear pendulum using ONLY polynomial basis (no trig).
    Proves that discovery fails when the true governing law lies outside the hypothesis class.
    """
    sys = get_benchmark_system("nonlinear_pendulum")
    t = np.linspace(0.0, 5.0, 501)
    sim = simulate_system(sys, np.array([2.0, 0.0]), (0.0, 5.0), t_eval=t)

    traj = Trajectory(id="pendulum_large_angle", t=sim.t, x=sim.x)
    ds = TrajectoryDataset(system_name="nonlinear_pendulum", variable_names=["theta", "omega"], trajectories=[traj])

    # Inadequate polynomial degree 2 library
    cfg = DiscoveryConfig(library_type="polynomial", poly_degree=2, threshold=0.05)
    engine = DiscoveryEngine(cfg)
    out = engine.fit(ds)

    # Discovered law in polynomial library CANNOT contain sin(theta)
    assert "sin(theta)" not in out.feature_names
    # Discovered system should fail exact support recovery
    assert "sin(theta)" not in [eq.raw_str for eq in out.discovered_system.equations.values()]


def test_adversarial_data_leakage_attack():
    """
    Adversarial Test G04:
    Attempt to construct a leaky dataset where a test trajectory shares state with train.
    Verifies that check_dataset_leakage catches the attack.
    """
    t = np.linspace(0, 1, 10)
    x = np.zeros((10, 2))
    tr1 = Trajectory(id="tr1", t=t, x=x)
    tr2 = Trajectory(id="tr1", t=t, x=x)  # Duplicate ID and states

    ds1 = TrajectoryDataset(system_name="test", variable_names=["x", "v"], trajectories=[tr1])
    ds2 = TrajectoryDataset(system_name="test", variable_names=["x", "v"], trajectories=[tr2])

    leakage = check_dataset_leakage(ds1, ds1, ds2)
    assert leakage["has_leakage"]
