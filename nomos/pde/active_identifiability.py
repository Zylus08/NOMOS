"""
NOMOS Active Identifiability & Disagreement-Driven Experiment Selection
Phase 8: Autonomous Experimental Design for Coupled PDE Systems
Tests the primary hypothesis:
"Disagreement-driven experiment selection improves exact structural recovery of coupled PDEs
under limited observations, compared with random and fixed experimental designs."
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from nomos.pde.schema import Grid1D, Grid2D, TimeGrid, SpatiotemporalField
from nomos.pde.strong_form import PDEDiscoveryResult


class ActiveIdentifiabilityEngine:
    """
    Autonomous Active Identifiability for dynamical physical laws.
    1. Evaluates ensemble of competing candidate models.
    2. Identifies parameter/structural degeneracies where models agree on training data.
    3. Synthesizes candidate experimental initial conditions (pool-based or parametric).
    4. Computes spatiotemporal disagreement metric D(u0; M1, M2).
    5. Selects the maximally discriminative experiment to falsify impostor models.
    """

    def __init__(self, random_seed: int = 42):
        self.random_seed = int(random_seed)

    def compute_model_disagreement(
        self,
        model1_predict_fn: Callable[[np.ndarray], np.ndarray],
        model2_predict_fn: Callable[[np.ndarray], np.ndarray],
        candidate_u0: np.ndarray,
    ) -> float:
        """
        Compute integrated vector field disagreement between two candidate models:
        D(u0) = || f_M1(u0) - f_M2(u0) ||_2^2
        """
        f1 = model1_predict_fn(candidate_u0)
        f2 = model2_predict_fn(candidate_u0)
        disagreement = float(np.mean((f1 - f2) ** 2))
        return disagreement

    def select_optimal_experiment(
        self,
        model1_fn: Callable[[np.ndarray], np.ndarray],
        model2_fn: Callable[[np.ndarray], np.ndarray],
        candidate_pool: List[Tuple[str, np.ndarray]],
    ) -> Tuple[str, np.ndarray, float, Dict[str, float]]:
        """
        Evaluate candidate initial conditions and select the one maximizing model disagreement.
        Returns: (selected_label, selected_u0, max_disagreement, all_scores).
        """
        best_label = ""
        best_u0 = None
        best_score = -1.0
        scores: Dict[str, float] = {}

        for label, u0 in candidate_pool:
            score = self.compute_model_disagreement(model1_fn, model2_fn, u0)
            scores[label] = score
            if score > best_score:
                best_score = score
                best_label = label
                best_u0 = u0

        return best_label, best_u0, best_score, scores

    def run_identifiability_trial(
        self,
        true_simulator: Any,
        grid: Any,
        time_grid: TimeGrid,
        impostor_model_fn: Callable[[np.ndarray], np.ndarray],
        true_model_fn: Callable[[np.ndarray], np.ndarray],
        strategy: str = "active",  # "active", "random", "fixed"
        candidate_pool: Optional[List[Tuple[str, np.ndarray]]] = None,
    ) -> Dict[str, Any]:
        """
        Run a controlled single-trial experiment comparing Active, Random, and Fixed experiment selection.
        Measures the empirical falsification margin:
        Margin = Residual(Impostor, Oracle_Data) / (Residual(True, Oracle_Data) + 1e-12)
        A margin >> 1 indicates decisive falsification of the degenerate impostor model.
        """
        if candidate_pool is None:
            raise ValueError("candidate_pool must be provided.")

        rng = np.random.RandomState(self.random_seed)

        if strategy == "active":
            label, chosen_u0, score, _ = self.select_optimal_experiment(
                impostor_model_fn, true_model_fn, candidate_pool
            )
        elif strategy == "random":
            idx = rng.randint(0, len(candidate_pool))
            label, chosen_u0 = candidate_pool[idx]
            score = self.compute_model_disagreement(impostor_model_fn, true_model_fn, chosen_u0)
        elif strategy == "fixed":
            # Always pick the default first candidate (passive baseline)
            label, chosen_u0 = candidate_pool[0]
            score = self.compute_model_disagreement(impostor_model_fn, true_model_fn, chosen_u0)
        else:
            raise ValueError(f"Unknown strategy {strategy}")

        # Execute oracle simulation with chosen initial condition
        oracle_field = true_simulator.simulate(chosen_u0, grid, time_grid, noise_level=0.0)

        # Evaluate prediction residuals on oracle data
        u_mid = oracle_field.u[oracle_field.num_time_steps // 2]
        u_t_oracle = oracle_field.u_t_true[oracle_field.num_time_steps // 2] if oracle_field.u_t_true is not None else None

        if u_t_oracle is None:
            # Fallback numerical derivative
            dt = oracle_field.dt
            idx_mid = oracle_field.num_time_steps // 2
            u_t_oracle = (oracle_field.u[idx_mid + 1] - oracle_field.u[idx_mid - 1]) / (2.0 * dt)

        pred_impostor = impostor_model_fn(u_mid)
        pred_true = true_model_fn(u_mid)

        res_impostor = float(np.mean((u_t_oracle - pred_impostor) ** 2))
        res_true = float(np.mean((u_t_oracle - pred_true) ** 2))
        falsification_ratio = float(res_impostor / (res_true + 1e-12))

        # Successfully discriminated if impostor error is at least 10x true error
        is_discriminated = falsification_ratio > 10.0

        return {
            "strategy": strategy,
            "chosen_experiment": label,
            "disagreement_score": score,
            "impostor_residual": res_impostor,
            "true_residual": res_true,
            "falsification_ratio": falsification_ratio,
            "is_discriminated": is_discriminated,
        }
