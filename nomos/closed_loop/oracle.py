"""
NOMOS Simulation Oracle & Sandboxed Experimentation Boundary
Guarantees strict physical isolation between the discovery agent and ground truth physics.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from nomos.pde.schema import Grid1D, Grid2D, TimeGrid, SpatiotemporalField
from nomos.pde.isolation import create_learner_field_observation


@dataclass
class ExperimentCost:
    """Multi-resource experimental cost tracking."""
    trajectory_queries: int = 1
    total_time_steps: int = 0
    spatial_points: int = 0
    observation_volume: float = 0.0         # int dx dt or int dx dy dt
    compute_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trajectory_queries": self.trajectory_queries,
            "total_time_steps": self.total_time_steps,
            "spatial_points": self.spatial_points,
            "observation_volume": round(self.observation_volume, 6),
            "compute_time_seconds": round(self.compute_time_seconds, 6),
        }


@dataclass
class ExperimentRequest:
    """Client request for an autonomous experiment query."""
    experiment_id: str
    u0: np.ndarray                          # Prescribed initial state or control
    t_span: Tuple[float, float] = (0.0, 0.5)
    num_time_steps: int = 30
    noise_level: float = 0.0
    random_seed: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResponse:
    """Sanitized observation package returned to discovery agent."""
    experiment_id: str
    field: SpatiotemporalField              # Learner-isolated observation
    cost: ExperimentCost
    execution_timestamp: float = field(default_factory=time.time)


class SimulationOracle:
    """
    Quarantined Physical Simulation Oracle.
    Executes the true simulator internally but strictly purges all ground-truth
    equations, true derivatives, and exact parameters before returning data to the agent.
    """

    def __init__(self, simulator: Any, grid: Any):
        self._simulator = simulator
        self._grid = grid
        self._query_count = 0
        self._cumulative_cost = ExperimentCost(trajectory_queries=0)

    @property
    def query_count(self) -> int:
        return self._query_count

    @property
    def cumulative_cost(self) -> ExperimentCost:
        return self._cumulative_cost

    def execute_experiment(self, request: ExperimentRequest) -> ExperimentResponse:
        """Execute simulation experiment and return sanitized observations."""
        t0 = time.time()
        self._query_count += 1

        t_grid = TimeGrid.create(request.t_span, request.num_time_steps)
        
        # Run ground-truth simulation
        raw_field = self._simulator.simulate(
            u0=request.u0,
            grid=self._grid,
            time_grid=t_grid,
            noise_level=request.noise_level,
            random_seed=request.random_seed,
        )
        sim_duration = time.time() - t0

        # Strictly sanitize observations via isolation sandbox
        learner_obs = create_learner_field_observation(raw_field)

        # Compute resource cost
        N_pts = learner_obs.num_spatial_points
        M_steps = learner_obs.num_time_steps
        if learner_obs.spatial_dim == 1:
            vol = float(learner_obs.dx * learner_obs.dt * N_pts * M_steps)
        else:
            vol = float(learner_obs.dx * learner_obs.dy * learner_obs.dt * N_pts * M_steps)

        step_cost = ExperimentCost(
            trajectory_queries=1,
            total_time_steps=M_steps,
            spatial_points=N_pts,
            observation_volume=vol,
            compute_time_seconds=sim_duration,
        )

        # Accumulate total costs
        self._cumulative_cost.trajectory_queries += 1
        self._cumulative_cost.total_time_steps += M_steps
        self._cumulative_cost.spatial_points += N_pts
        self._cumulative_cost.observation_volume += vol
        self._cumulative_cost.compute_time_seconds += sim_duration

        return ExperimentResponse(
            experiment_id=request.experiment_id,
            field=learner_obs,
            cost=step_cost,
        )
