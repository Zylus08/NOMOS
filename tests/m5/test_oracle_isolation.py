"""
NOMOS Milestone M5 Unit Tests: Simulation Oracle & Quarantine Isolation
Verifies strict information barrier, no ground truth parameter leakage, and multi-resource cost accounting.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid1D, TimeGrid, SpatiotemporalField
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.closed_loop.oracle import SimulationOracle, ExperimentRequest, ExperimentCost


def test_oracle_quarantine_isolation():
    grid = Grid1D.create((-10.0, 10.0), 64)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    oracle = SimulationOracle(sim, grid)

    u0 = sim.analytical_1soliton(grid.x, 0.0)
    req = ExperimentRequest(
        experiment_id="test_exp_01",
        u0=u0,
        t_span=(0.0, 0.2),
        num_time_steps=20,
        noise_level=0.01,
        random_seed=42,
    )

    resp = oracle.execute_experiment(req)
    field = resp.field

    # Verify field is a genuine SpatiotemporalField
    assert isinstance(field, SpatiotemporalField)
    assert field.spatial_dim == 1
    assert field.num_spatial_points == 64
    assert field.num_time_steps == 20

    # Verify strict sanitization: ground truth simulator, parameters, and clean fields are quarantined
    assert field.true_parameters is None
    assert field.u_clean is None
    assert field.u_t_true is None
    assert not hasattr(field, "_simulator")
    assert not hasattr(resp, "simulator")

    # Verify multi-resource cost accounting
    cost = resp.cost
    assert isinstance(cost, ExperimentCost)
    assert cost.trajectory_queries == 1
    assert cost.total_time_steps == 20
    assert cost.spatial_points == 64
    assert cost.observation_volume > 0.0
    assert cost.compute_time_seconds > 0.0

    # Cumulative cost check
    assert oracle.query_count == 1
    assert oracle.cumulative_cost.trajectory_queries == 1
    assert oracle.cumulative_cost.total_time_steps == 20
