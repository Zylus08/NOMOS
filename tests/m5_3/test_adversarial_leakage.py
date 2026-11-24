"""
NOMOS Milestone M5.3: Adversarial Information Leakage Test Suite
Strictly verifies that no ground-truth system identity, hidden simulator parameters,
or clean analytical fields leak into candidate hypothesis generation or closed-loop control.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid1D, Grid2D, TimeGrid, SpatiotemporalField
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.pde.simulators.burgers import BurgersSimulator
from nomos.pde.simulators.gray_scott import GrayScottSimulator
from nomos.pde.isolation import create_learner_field_observation, create_learner_dataset
from nomos.closed_loop.oracle import SimulationOracle, ExperimentRequest
from nomos.closed_loop.acquisition import AcquisitionStrategy
from nomos.closed_loop.controller import ClosedLoopController
from nomos.closed_loop.diagnostics import IdentifiabilityStatus
from experiments.m5.run_m5_benchmarks import build_kdv_pool, build_burgers_pool, build_gray_scott_pool


def test_randomized_pde_name():
    """
    Test 1: Arbitrary / Randomized String Resistance.
    Learner observation scrubber must replace arbitrary or random strings with blind_system_*.
    The controller must discover the correct physics without relying on known name patterns.
    """
    grid = Grid1D.create((-10.0, 10.0), 128)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    u0 = sim.analytical_1soliton(grid.x, 0.0, c=2.0)
    t_grid = TimeGrid.create((0.0, 0.2), 15)
    raw_field = sim.simulate(u0, grid, t_grid)

    # Inject completely random / adversarial name into raw field
    raw_field.pde_name = "galaxy_cluster_hydrodynamics_random_99482"
    sanitized = create_learner_field_observation(raw_field)

    assert sanitized.pde_name.startswith("blind_system_")
    assert "galaxy" not in sanitized.pde_name
    assert "kdv" not in sanitized.pde_name


def test_adversarial_label_inversion():
    """
    Test 2: Adversarial Inversion / Label Scrambling.
    When KdV data is falsely labeled 'viscous_burgers', the controller must NOT
    inject Burgers diffusion or use the misleading string.
    """
    grid = Grid1D.create((-10.0, 10.0), 128)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    pool = build_kdv_pool(sim, grid)
    oracle = SimulationOracle(sim, grid)

    # Wrap oracle simulator to inject misleading pde_name
    sim.name = "viscous_burgers"

    controller = ClosedLoopController(
        oracle=oracle,
        grid=grid,
        candidate_experiment_pool=pool,
        strategy=AcquisitionStrategy.GREEDY_DISAGREEMENT,
        max_budget=4,
        noise_level=0.0,
        random_seed=42,
        dimension=1,
        target_channel="u",
        candidate_library=["u*u_x", "u_xxx", "u_x"],
    )

    episode = controller.run_investigation()

    # Verify that no hypothesis contains 'burgers' or origin 'competing_physical_prior'
    for h in controller.portfolio.get_all():
        assert "burgers" not in h.id.lower()
        assert "linear_diffusion_impostor" not in h.id
        assert h.origin != "competing_physical_prior"

    # Verify correct KdV recovery despite deceptive simulator name
    assert episode.status == IdentifiabilityStatus.IDENTIFIED
    assert episode.winning_hypothesis is not None
    assert "u*u_x" in episode.winning_hypothesis.parameters
    assert "u_xxx" in episode.winning_hypothesis.parameters
    assert np.isclose(episode.winning_hypothesis.parameters["u*u_x"], -6.0, atol=0.25)
    assert np.isclose(episode.winning_hypothesis.parameters["u_xxx"], -1.0, atol=0.1)


def test_parameter_perturbation_isolation():
    """
    Test 3: Simulator Parameter Perturbation.
    When physical parameters are modified (e.g. nu=0.075 instead of standard 0.05),
    the controller must discover the true parameter (0.075) and NEVER contain
    the old hardcoded parameter (0.05).
    """
    grid = Grid1D.create((0.0, 2.0 * np.pi), 64)
    # Modified viscosity 0.075 (previously hardcoded was 0.05)
    sim = BurgersSimulator(nu=0.075)
    pool = build_burgers_pool(sim, grid)
    oracle = SimulationOracle(sim, grid)

    controller = ClosedLoopController(
        oracle=oracle,
        grid=grid,
        candidate_experiment_pool=pool,
        strategy=AcquisitionStrategy.GREEDY_DISAGREEMENT,
        max_budget=4,
        noise_level=0.0,
        random_seed=42,
        dimension=1,
        target_channel="u",
        candidate_library=["u*u_x", "u_xx", "u_xxx", "u_x"],
    )

    episode = controller.run_investigation()

    # Verify zero presence of hardcoded 0.05
    for h in controller.portfolio.get_all():
        if "u_xx" in h.parameters and len(h.parameters) == 1:
            # Sub-model parameter must be fitted from data, not hardcoded 0.05
            assert not np.isclose(h.parameters["u_xx"], 0.05, atol=1e-3)

    assert episode.status == IdentifiabilityStatus.IDENTIFIED
    assert episode.winning_hypothesis is not None
    assert np.isclose(episode.winning_hypothesis.parameters["u_xx"], 0.075, atol=0.01)
    assert np.isclose(episode.winning_hypothesis.parameters["u*u_x"], -1.0, atol=0.05)


def test_step0_hypothesis_origin_and_features():
    """
    Test 4: Step 0 Hypothesis Portfolio Inspection.
    Verify that at Step 0, all hypotheses have data-derived origins and
    zero hypotheses carry 'competing_physical_prior' or hardcoded parameters.
    """
    grid = Grid1D.create((-10.0, 10.0), 128)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    pool = build_kdv_pool(sim, grid)
    oracle = SimulationOracle(sim, grid)

    controller = ClosedLoopController(
        oracle=oracle,
        grid=grid,
        candidate_experiment_pool=pool,
        strategy=AcquisitionStrategy.GREEDY_DISAGREEMENT,
        max_budget=4,
        random_seed=42,
    )

    # Initialize Stage 0 observation only
    init_lbl, init_u0, _ = pool[0]
    req = ExperimentRequest(experiment_id="exp_init", u0=init_u0)
    resp = oracle.execute_experiment(req)
    controller.observed_fields.append(resp.field)
    controller._generate_initial_hypotheses(resp.field)

    all_hyps = controller.portfolio.get_all()
    assert len(all_hyps) > 0

    for h in all_hyps:
        # Strict origin audit
        assert h.origin != "competing_physical_prior"
        assert any(h.origin.startswith(prefix) for prefix in ("wsindy_", "beam_", "parsimonious_submodel_"))
        # Strict id audit: no hardcoded system labels
        assert "impostor" not in h.id
        assert "kdv" not in h.id
        assert "burgers" not in h.id
        assert "gray_scott" not in h.id


def test_oracle_quarantine_integrity():
    """
    Test 5: Oracle Quarantine Integrity.
    Verifies that SimulationOracle strictly purges all ground-truth attributes
    and anonymizes the observation pde_name before returning to caller.
    """
    grid = Grid1D.create((-10.0, 10.0), 64)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    oracle = SimulationOracle(sim, grid)

    u0 = sim.analytical_1soliton(grid.x, 0.0)
    req = ExperimentRequest(experiment_id="exp_isolation_check", u0=u0)
    resp = oracle.execute_experiment(req)
    obs = resp.field

    assert obs.u_clean is None
    assert obs.u_t_true is None
    assert obs.true_parameters is None
    assert not hasattr(obs, "_simulator")
    assert not hasattr(resp, "simulator")
    assert obs.pde_name.startswith("blind_system_")
    assert "kdv" not in obs.pde_name
