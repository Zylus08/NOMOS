"""
NOMOS Milestone M5.1 Unit Tests:
Held-out Physical Systems (Brusselator 2D, Cahn–Hilliard 1D/2D)
and Strong Baseline Acquisition Strategies.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid1D, Grid2D, TimeGrid
from nomos.pde.simulators.brusselator import Brusselator2DSimulator
from nomos.pde.simulators.cahn_hilliard import CahnHilliard1DSimulator, CahnHilliard2DSimulator
from nomos.closed_loop.oracle import SimulationOracle, ExperimentRequest
from nomos.closed_loop.acquisition import ExperimentAcquisitionEngine, AcquisitionStrategy
from nomos.closed_loop.portfolio import ScientificHypothesis, HypothesisPortfolio, HypothesisStatus


def test_brusselator_2d_simulation_stability():
    grid = Grid2D.create((0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi), 16, 16)
    sim = Brusselator2DSimulator(D_u=0.1, D_v=0.05, A=1.0, B=3.0)
    time_grid = TimeGrid.create((0.0, 0.1), 10)

    # Initial condition near homogeneous steady state (A, B/A) = (1.0, 3.0)
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    u0 = np.zeros((16, 16, 2))
    u0[..., 0] = 1.0 + 0.1 * np.sin(X) * np.cos(Y)
    u0[..., 1] = 3.0 + 0.1 * np.cos(X) * np.sin(Y)

    field = sim.simulate(u0, grid, time_grid, noise_level=0.01, random_seed=42)
    assert field.u.shape == (10, 16, 16, 2)
    assert not np.isnan(field.u).any()
    assert np.all(np.isfinite(field.u))

    # Test RHS
    rhs = sim.rhs_spatial(u0, grid.x, grid.y)
    assert rhs.shape == (16, 16, 2)
    assert not np.isnan(rhs).any()


def test_cahn_hilliard_1d_mass_conservation():
    grid = Grid1D.create((0.0, 2.0 * np.pi), 64)
    sim = CahnHilliard1DSimulator(gamma=1.0, epsilon=0.05)
    time_grid = TimeGrid.create((0.0, 0.05), 15)

    x = grid.x
    u0 = 0.2 * np.cos(3.0 * x)
    initial_mass = sim.compute_invariant(u0, grid.dx)

    field = sim.simulate(u0, grid, time_grid, noise_level=0.0)
    final_mass = sim.compute_invariant(field.u[-1], grid.dx)

    # Mass must be conserved to high precision
    assert abs(final_mass - initial_mass) < 1e-10

    # Free energy must be non-increasing (or stable within numerical tolerance)
    f0 = sim.compute_free_energy(u0, grid.dx)
    f_final = sim.compute_free_energy(field.u[-1], grid.dx)
    assert f_final <= f0 + 1e-6


def test_cahn_hilliard_2d_simulation():
    grid = Grid2D.create((0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi), 16, 16)
    sim = CahnHilliard2DSimulator(gamma=1.0, epsilon=0.08)
    time_grid = TimeGrid.create((0.0, 0.02), 8)

    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    u0 = 0.1 * np.cos(2.0 * X) * np.sin(2.0 * Y)

    field = sim.simulate(u0, grid, time_grid, noise_level=0.01, random_seed=42)
    assert field.u.shape == (8, 16, 16, 1)
    assert not np.isnan(field.u).any()


def test_acquisition_baselines_execute():
    portfolio = HypothesisPortfolio()
    h1 = ScientificHypothesis(
        id="h1",
        equation_str="u_t = -2.0*u_x",
        features=["u_x"],
        parameters={"u_x": -2.0},
        complexity=2,
        origin="test",
        evidence_score=0.6,
    )
    h2 = ScientificHypothesis(
        id="h2",
        equation_str="u_t = -6.0*u*u_x - 1.0*u_xxx",
        features=["u*u_x", "u_xxx"],
        parameters={"u*u_x": -6.0, "u_xxx": -1.0},
        complexity=4,
        origin="test",
        evidence_score=0.4,
    )
    portfolio.register(h1)
    portfolio.register(h2)

    x = np.linspace(0, 2 * np.pi, 32, endpoint=False)
    pool = [
        ("harmonic", np.sin(x), 1.0),
        ("packet", np.sin(x) * np.exp(-((x - np.pi) ** 2)), 1.0),
        ("pulse", np.exp(-5.0 * ((x - np.pi) ** 2)), 1.0),
    ]

    for strat in [
        AcquisitionStrategy.RANDOM,
        AcquisitionStrategy.FIXED,
        AcquisitionStrategy.GREEDY_DISAGREEMENT,
        AcquisitionStrategy.UNCERTAINTY_AWARE,
        AcquisitionStrategy.MODEL_DISCRIMINATION,
        AcquisitionStrategy.HANDCRAFTED_SCHEDULE,
    ]:
        engine = ExperimentAcquisitionEngine(strategy=strat, random_seed=42)
        lbl, u0, score, scores = engine.select_experiment(portfolio, pool, dx=float(x[1] - x[0]))
        assert lbl in ["harmonic", "packet", "pulse"]
        assert u0 is not None
        assert isinstance(score, float)
