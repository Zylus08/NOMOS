"""
NOMOS M2 Neural-Symbolic Discovery Pipeline Orchestrator
Milestone M2 — Phase 5 & Phase 6 Integration
Agents D15, D16, J01, J02
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from nomos.core.system import DynamicalSystem
from nomos.data.schema import TrajectoryDataset
from nomos.data.isolation import IsolatedLearnerDataset
from nomos.differentiation import finite_difference, savitzky_golay_derivative
from nomos.symbolic.trees import ExpressionTree
from nomos.neural.surrogate import NeuralDynamicsSurrogate
from nomos.neural.trainer import SurrogateTrainer
from nomos.search.hybrid import NeuralGuidedSearch
from nomos.search.pareto import ParetoFrontier, CandidateLaw
from nomos.evaluation.rollout import simulate_discovered_model, evaluate_rollout
from nomos.evaluation.identifiability import audit_identifiability, IdentifiabilityReport


@dataclass
class M2DiscoveryConfig:
    search_strategy: str = "beam"  # 'beam', 'genetic', or 'sindy'
    enable_neural_guidance: bool = True
    surrogate_epochs: int = 60
    surrogate_hidden: int = 64
    max_search_evals: int = 1000
    diff_method: str = "savitzky_golay"
    savgol_window: int = 15
    savgol_poly: int = 3
    seed: int = 42


@dataclass
class M2DiscoveryResult:
    system_name: str
    variable_names: List[str]
    discovered_equations: Dict[str, str]
    discovered_trees: Dict[str, ExpressionTree]
    pareto_frontiers: Dict[str, ParetoFrontier]
    identifiability_reports: Dict[str, IdentifiabilityReport]
    surrogate_metrics: Dict[str, Any]
    total_candidate_evaluations: int
    execution_time_seconds: float
    config: M2DiscoveryConfig


class M2DiscoveryEngine:
    """
    Milestone M2 Neural-Symbolic Discovery Engine.
    Executes open-ended equation discovery beyond fixed candidate libraries.
    """

    def __init__(self, config: Optional[M2DiscoveryConfig] = None):
        self.config = config or M2DiscoveryConfig()

    def fit(self, dataset: Any) -> M2DiscoveryResult:
        start_time = time.time()
        var_names = list(dataset.variable_names)
        state_dim = len(var_names)

        # 1. Differentiate trajectories
        x_stacked_list = []
        x_dot_list = []

        for traj in dataset.trajectories:
            t = traj.t
            x = traj.x
            if self.config.diff_method == "savitzky_golay":
                x_dot = savitzky_golay_derivative(
                    t, x, window_length=self.config.savgol_window, polyorder=self.config.savgol_poly
                )
            else:
                x_dot = finite_difference(t, x, order=4)

            x_stacked_list.append(x)
            x_dot_list.append(x_dot)

        X_all = np.concatenate(x_stacked_list, axis=0)
        X_dot_all = np.concatenate(x_dot_list, axis=0)

        # 2. Train Neural Dynamics Surrogate
        surrogate = None
        surrogate_metrics = {}
        if self.config.enable_neural_guidance:
            trainer = SurrogateTrainer(
                hidden_dim=self.config.surrogate_hidden,
                max_epochs=self.config.surrogate_epochs,
                seed=self.config.seed,
            )
            surrogate, surrogate_metrics = trainer.fit(X_all, X_dot_all)

        # 3. Perform Symbolic Search for each state variable dimension
        discovered_equations = {}
        discovered_trees = {}
        pareto_frontiers = {}
        identifiability_reports = {}
        total_evals = 0

        for dim, vname in enumerate(var_names):
            y_target = X_dot_all[:, dim : dim + 1]

            searcher = NeuralGuidedSearch(
                variable_names=var_names,
                base_search_method=self.config.search_strategy,
                max_evals=self.config.max_search_evals,
                enable_guidance=self.config.enable_neural_guidance,
                seed=self.config.seed + dim,
            )
            if surrogate is not None:
                searcher.set_surrogate(surrogate)

            pareto, meta = searcher.search(X_all, y_target, target_dim=dim)
            total_evals += searcher.total_evals

            best_candidate = pareto.get_best(complexity_weight=0.005)
            discovered_trees[vname] = best_candidate.tree
            discovered_equations[vname] = best_candidate.tree.to_string()
            pareto_frontiers[vname] = pareto

            # Audit identifiability and parameter uncertainty
            ident_rep = audit_identifiability(X_all, y_target, pareto)
            identifiability_reports[vname] = ident_rep

        elapsed = float(time.time() - start_time)

        return M2DiscoveryResult(
            system_name=getattr(dataset, "system_name", "unknown"),
            variable_names=var_names,
            discovered_equations=discovered_equations,
            discovered_trees=discovered_trees,
            pareto_frontiers=pareto_frontiers,
            identifiability_reports=identifiability_reports,
            surrogate_metrics=surrogate_metrics,
            total_candidate_evaluations=total_evals,
            execution_time_seconds=elapsed,
            config=self.config,
        )
