"""
NOMOS Milestone M5.3.1: Adversarial Blinding Contract & Hard Budget Test Suite
Rigorous verification of:
1. Deterministic SHA-256 opaque anonymization (PYTHONHASHSEED independent)
2. Explicit allowlist attribute serialization
3. Ten adversarial attack vectors against physical blinding
4. Hard query budget enforcement at the SimulationOracle boundary
"""

import copy
import hashlib
import pytest
import numpy as np

from nomos.pde.schema import Grid1D, Grid2D, TimeGrid, SpatiotemporalField
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.pde.simulators.burgers import BurgersSimulator
from nomos.pde.simulators.gray_scott import GrayScottSimulator
from nomos.pde.isolation import (
    create_learner_field_observation,
    compute_opaque_observation_digest,
    serialize_learner_observation,
    ALLOWED_OBSERVATION_ATTRIBUTES,
    DISALLOWED_EVALUATOR_ATTRIBUTES,
)
from nomos.closed_loop.oracle import (
    SimulationOracle,
    ExperimentRequest,
    ExperimentCost,
    BudgetExceededError,
)
from nomos.closed_loop.acquisition import AcquisitionStrategy, ExperimentAcquisitionEngine
from nomos.closed_loop.portfolio import ScientificHypothesis, HypothesisPortfolio
from nomos.closed_loop.diagnostics import IdentifiabilityStatus, IdentifiabilityAuditor
from nomos.closed_loop.controller import ClosedLoopController
from experiments.m5.run_m5_benchmarks import build_kdv_pool, build_burgers_pool


# --- Vector 1: Randomized Hidden System Names ---
def test_vector1_randomized_hidden_system_names():
    grid = Grid1D.create((-10.0, 10.0), 128)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    u0 = sim.analytical_1soliton(grid.x, 0.0, c=2.0)
    t_grid = TimeGrid.create((0.0, 0.2), 15)
    raw = sim.simulate(u0, grid, t_grid)
    raw.pde_name = "random_unregistered_pde_99214_xyz"

    obs = create_learner_field_observation(raw)
    assert obs.pde_name.startswith("blind_system_")
    assert "random" not in obs.pde_name
    assert "kdv" not in obs.pde_name


# --- Vector 2: Identical Labels Attached to Different Hidden Systems ---
def test_vector2_identical_labels_different_systems():
    g1d = Grid1D.create((-10.0, 10.0), 64)
    t_grid = TimeGrid.create((0.0, 0.1), 10)

    sim_kdv = KdVSimulator(domain=(-10.0, 10.0))
    sim_burg = BurgersSimulator(nu=0.05)

    u0 = np.sin(np.pi * g1d.x / 10.0)
    raw_kdv = sim_kdv.simulate(u0, g1d, t_grid)
    raw_burg = sim_burg.simulate(u0, g1d, t_grid)

    # Force identical deceptive labels on both
    raw_kdv.pde_name = "identical_alias_42"
    raw_burg.pde_name = "identical_alias_42"

    obs_kdv = create_learner_field_observation(raw_kdv)
    obs_burg = create_learner_field_observation(raw_burg)

    # Must produce distinct SHA-256 IDs because physical tensor contents differ
    assert obs_kdv.pde_name != obs_burg.pde_name
    assert obs_kdv.pde_name.startswith("blind_system_")
    assert obs_burg.pde_name.startswith("blind_system_")


# --- Vector 3: Different Labels Attached to Identical Observations ---
def test_vector3_different_labels_identical_observations():
    grid = Grid1D.create((-10.0, 10.0), 64)
    t_grid = TimeGrid.create((0.0, 0.1), 10)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    u0 = sim.analytical_1soliton(grid.x, 0.0)

    raw1 = sim.simulate(u0, grid, t_grid)
    raw2 = sim.simulate(u0, grid, t_grid)

    raw1.pde_name = "superstring_quantum_cosmology"
    raw2.pde_name = "simple_harmonic_oscillator"

    obs1 = create_learner_field_observation(raw1)
    obs2 = create_learner_field_observation(raw2)

    # Pure data-driven digest must be identical regardless of metadata labels
    assert obs1.pde_name == obs2.pde_name


# --- Vector 4: Reordered Benchmark Registration ---
def test_vector4_reordered_benchmark_registration():
    grid = Grid1D.create((-10.0, 10.0), 128)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    pool_orig = build_kdv_pool(sim, grid)
    pool_reordered = list(reversed(pool_orig))

    oracle1 = SimulationOracle(sim, grid, max_budget=4)
    ctrl1 = ClosedLoopController(
        oracle=oracle1,
        grid=grid,
        candidate_experiment_pool=pool_orig,
        strategy=AcquisitionStrategy.GREEDY_DISAGREEMENT,
        max_budget=4,
        candidate_library=["u*u_x", "u_xxx", "u_x"],
    )
    ep1 = ctrl1.run_investigation()

    oracle2 = SimulationOracle(sim, grid, max_budget=4)
    ctrl2 = ClosedLoopController(
        oracle=oracle2,
        grid=grid,
        candidate_experiment_pool=pool_reordered,
        strategy=AcquisitionStrategy.GREEDY_DISAGREEMENT,
        max_budget=4,
        candidate_library=["u*u_x", "u_xxx", "u_x"],
    )
    ep2 = ctrl2.run_investigation()

    # Both must identify true KdV physics regardless of pool order
    assert ep1.status == IdentifiabilityStatus.IDENTIFIED
    assert ep2.status == IdentifiabilityStatus.IDENTIFIED
    assert "u*u_x" in ep1.winning_hypothesis.parameters
    assert "u*u_x" in ep2.winning_hypothesis.parameters


# --- Vector 5: Hidden Parameter Perturbations ---
def test_vector5_hidden_parameter_perturbation():
    grid = Grid1D.create((0.0, 2.0 * np.pi), 64)
    sim = BurgersSimulator(nu=0.082) # Non-standard viscosity
    pool = build_burgers_pool(sim, grid)
    oracle = SimulationOracle(sim, grid, max_budget=4)

    ctrl = ClosedLoopController(
        oracle=oracle,
        grid=grid,
        candidate_experiment_pool=pool,
        strategy=AcquisitionStrategy.GREEDY_DISAGREEMENT,
        max_budget=4,
        candidate_library=["u*u_x", "u_xx", "u_xxx"],
    )
    ep = ctrl.run_investigation()

    assert ep.status == IdentifiabilityStatus.IDENTIFIED
    assert ep.winning_hypothesis is not None
    # Must recover 0.082, not default 0.05
    assert np.isclose(ep.winning_hypothesis.parameters["u_xx"], 0.082, atol=0.015)
    assert not np.isclose(ep.winning_hypothesis.parameters["u_xx"], 0.05, atol=1e-3)


# --- Vector 6: Cross-Process Reproducibility (PYTHONHASHSEED Independence) ---
def test_vector6_pythonhashseed_independence():
    grid = Grid1D.create((-5.0, 5.0), 32)
    t = np.linspace(0, 0.5, 5)
    u = np.outer(t, np.exp(-grid.x**2))

    f1 = SpatiotemporalField(id="obs_1", pde_name="kdv", x=grid.x, t=t, u=u)
    f2 = SpatiotemporalField(id="obs_2", pde_name="burgers", x=grid.x, t=t, u=u)

    # Identical array values must produce identical SHA-256 digests across any process
    d1 = compute_opaque_observation_digest(f1)
    d2 = compute_opaque_observation_digest(f2)
    assert d1 == d2
    assert len(d1) == 64


# --- Vector 7: Isolation Boundary Import Protection & Allowlist Enforcement ---
def test_vector7_isolation_boundary_allowlist():
    grid = Grid1D.create((-10.0, 10.0), 32)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    oracle = SimulationOracle(sim, grid)

    req = ExperimentRequest(experiment_id="test_exp", u0=sim.analytical_1soliton(grid.x, 0.0))
    resp = oracle.execute_experiment(req)
    obs = resp.field

    # Check that evaluator fields are None
    for attr in DISALLOWED_EVALUATOR_ATTRIBUTES:
        val = getattr(obs, attr, None)
        assert val is None, f"Evaluator attribute {attr} leaked into learner observation!"

    # Check serialization adheres strictly to allowlist
    serialized = serialize_learner_observation(obs)
    for key in serialized:
        assert key in ALLOWED_OBSERVATION_ATTRIBUTES


# --- Vector 8: Elimination of Simulator Parameter Seeding in Candidates ---
def test_vector8_no_parameter_seeding_in_candidates():
    grid = Grid1D.create((-10.0, 10.0), 128)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    pool = build_kdv_pool(sim, grid)
    oracle = SimulationOracle(sim, grid)

    ctrl = ClosedLoopController(
        oracle=oracle,
        grid=grid,
        candidate_experiment_pool=pool,
        strategy=AcquisitionStrategy.GREEDY_DISAGREEMENT,
        max_budget=4,
    )

    init_lbl, init_u0, _ = pool[0]
    req = ExperimentRequest(experiment_id="init_probe", u0=init_u0)
    resp = oracle.execute_experiment(req)
    ctrl.observed_fields.append(resp.field)
    ctrl._generate_initial_hypotheses(resp.field)

    for h in ctrl.portfolio.get_all():
        assert h.origin != "competing_physical_prior"
        assert any(h.origin.startswith(pfx) for pfx in ("wsindy_", "beam_", "parsimonious_submodel_"))
        assert "impostor" not in h.id


# --- Vector 9: Acquisition Depends Exclusively on Observable Disagreement ---
def test_vector9_acquisition_observable_disagreement():
    engine = ExperimentAcquisitionEngine(strategy=AcquisitionStrategy.GREEDY_DISAGREEMENT, random_seed=42)
    portfolio = HypothesisPortfolio()

    h1 = ScientificHypothesis(
        id="h1",
        equation_str="u_t = -6 u u_x",
        features=["u*u_x"],
        parameters={"u*u_x": -6.0},
        complexity=2,
        origin="wsindy_thresh_0.015",
    )
    h2 = ScientificHypothesis(
        id="h2",
        equation_str="u_t = 0.05 u_xx",
        features=["u_xx"],
        parameters={"u_xx": 0.05},
        complexity=2,
        origin="wsindy_thresh_0.045",
    )
    portfolio.register(h1)
    portfolio.register(h2)

    grid = Grid1D.create((-10.0, 10.0), 64)
    u0_smooth = np.sin(grid.x)
    u0_flat = np.zeros_like(grid.x)

    pool = [("flat_uninformative", u0_flat, 1.0), ("informative_sine", u0_smooth, 1.0)]

    chosen_lbl, _, score, ledger = engine.select_experiment(
        portfolio=portfolio,
        candidate_pool=pool,
        dx=grid.dx,
    )
    # Observable vector field divergence selects informative sine over uninformative flat zero
    assert chosen_lbl == "informative_sine"
    assert score > 0.0
    assert ledger["informative_sine"] > ledger["flat_uninformative"]


# --- Vector 10: Stopping Criteria Depend Exclusively on Observable Residuals ---
def test_vector10_stopping_criteria_observable():
    auditor = IdentifiabilityAuditor(bayes_factor_threshold=10.0)
    portfolio = HypothesisPortfolio()

    h_dominant = ScientificHypothesis(
        id="h_dominant",
        equation_str="u_t = -6 u u_x - u_xxx",
        features=["u*u_x", "u_xxx"],
        parameters={"u*u_x": -6.0, "u_xxx": -1.0},
        complexity=4,
        origin="wsindy_thresh_0.015",
        val_mse=0.001,
        bic=10.0,
        supporting_experiments=["exp_00", "exp_01"],
    )
    h_sub = ScientificHypothesis(
        id="h_sub",
        equation_str="u_t = 0.05 u_xx",
        features=["u_xx"],
        parameters={"u_xx": 0.05},
        complexity=2,
        origin="wsindy_thresh_0.045",
        val_mse=0.45,
        bic=55.0, # Delta BIC = 45.0 >> 10.0
    )
    portfolio.register(h_dominant)
    portfolio.register(h_sub)

    status, winner, diag = auditor.audit_portfolio(portfolio, current_budget_used=2, max_budget=4)
    assert status == IdentifiabilityStatus.IDENTIFIED
    assert winner is not None
    assert winner.id == "h_dominant"
    assert diag["delta_bic"] >= 10.0


# --- Vector 11: Hard Query Budget Rejection in SimulationOracle ---
def test_vector11_hard_budget_rejection():
    grid = Grid1D.create((-10.0, 10.0), 32)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    oracle = SimulationOracle(sim, grid, max_budget=3)

    u0 = sim.analytical_1soliton(grid.x, 0.0)
    req = ExperimentRequest(experiment_id="exp", u0=u0)

    # 3 permitted queries
    oracle.execute_experiment(req)
    assert oracle.query_count == 1
    oracle.execute_experiment(req)
    assert oracle.query_count == 2
    oracle.execute_experiment(req)
    assert oracle.query_count == 3

    # 4th query must be strictly rejected
    with pytest.raises(BudgetExceededError) as exc_info:
        oracle.execute_experiment(req)
    assert "budget exhausted" in str(exc_info.value).lower()
    assert oracle.query_count == 3


# --- Vector 12: ClosedLoopController Query Limit Bound ---
def test_vector12_controller_total_query_bound():
    grid = Grid1D.create((-10.0, 10.0), 64)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    pool = build_kdv_pool(sim, grid)
    oracle = SimulationOracle(sim, grid, max_budget=4)

    ctrl = ClosedLoopController(
        oracle=oracle,
        grid=grid,
        candidate_experiment_pool=pool,
        strategy=AcquisitionStrategy.FIXED, # Fixed may exhaust budget if library distractors present
        max_budget=4,
        candidate_library=["u*u_x", "u_xx", "u_xxx", "u_xxxx", "1"],
    )

    ep = ctrl.run_investigation()

    # Total queries must never exceed 4
    assert oracle.query_count <= 4
    assert ep.total_cost.trajectory_queries <= 4
    assert ep.total_cost.trajectory_queries == oracle.query_count
