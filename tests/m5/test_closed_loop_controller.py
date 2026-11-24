"""
NOMOS Milestone M5 Unit Tests: Closed-Loop Autonomous Controller
Verifies 8-stage investigation cycle, early stopping, and decision trace generation.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid1D
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.closed_loop.oracle import SimulationOracle
from nomos.closed_loop.acquisition import AcquisitionStrategy
from nomos.closed_loop.controller import ClosedLoopController
from nomos.closed_loop.diagnostics import IdentifiabilityStatus
from experiments.m5.run_m5_benchmarks import build_kdv_pool


def test_closed_loop_controller_cycle():
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
        noise_level=0.0,
        random_seed=42,
        dimension=1,
        target_channel="u",
        candidate_library=["u*u_x", "u_xxx", "u_x"],
    )

    episode = controller.run_investigation()

    # 1. Verification of early stopping upon unique identifiability
    assert episode.status == IdentifiabilityStatus.IDENTIFIED
    assert episode.winning_hypothesis is not None

    # 2. Winning hypothesis recovers true KdV physics
    recovered_keys = set(episode.winning_hypothesis.parameters.keys())
    assert "u*u_x" in recovered_keys
    assert "u_xxx" in recovered_keys
    assert np.isclose(episode.winning_hypothesis.parameters["u*u_x"], -6.0, atol=0.25)
    assert np.isclose(episode.winning_hypothesis.parameters["u_xxx"], -1.0, atol=0.1)

    # 3. Trajectory queries within budget
    assert episode.total_cost.trajectory_queries <= 4
    assert len(episode.trace) >= 1

    # 4. Verification of trace record structure
    first_step = episode.trace[0]
    assert first_step.iteration == 1
    assert first_step.stage == "CLOSED_LOOP_STEP"
    assert first_step.acquisition_score > 0.0
    assert first_step.selected_experiment in [p[0] for p in pool]
