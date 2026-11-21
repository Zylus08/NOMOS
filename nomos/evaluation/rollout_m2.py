"""
NOMOS M2 Closed-Loop Rollout Evaluation for Expression Trees
Milestone M2 — Phase 9 & Phase 10 Verification
Agents F02, F03, G06
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy.integrate import solve_ivp
from nomos.symbolic.trees import ExpressionTree


def simulate_expression_trees(
    trees: List[ExpressionTree],
    x0: np.ndarray,
    t_eval: np.ndarray,
    divergence_bound: float = 1e4,
    rtol: float = 1e-6,
    atol: float = 1e-6,
) -> Tuple[np.ndarray, bool, str]:
    """
    Numerically simulate an arbitrary symbolic dynamical system defined by ExpressionTrees:
        dx_i/dt = f_i(x_1, ..., x_n)
    """
    x0 = np.asarray(x0, dtype=np.float64)
    t_span = (float(t_eval[0]), float(t_eval[-1]))
    n_vars = len(x0)

    def rhs(t, state):
        if not np.all(np.isfinite(state)) or np.max(np.abs(state)) > divergence_bound:
            return np.zeros_like(state)
        state_2d = state[np.newaxis, :]
        dx = np.zeros(n_vars, dtype=np.float64)
        for i in range(n_vars):
            try:
                val = float(trees[i].evaluate(state_2d)[0])
                dx[i] = val if np.isfinite(val) else 0.0
            except Exception:
                dx[i] = 0.0
        return dx

    try:
        sol = solve_ivp(
            rhs,
            t_span=t_span,
            y0=x0,
            t_eval=t_eval,
            method="RK45",
            rtol=rtol,
            atol=atol,
            max_step=0.05,
        )
    except Exception as e:
        M = len(t_eval)
        return np.full((M, n_vars), np.nan), False, str(e)

    if not sol.success or len(sol.t) != len(t_eval):
        M = len(t_eval)
        res = np.full((M, n_vars), np.nan)
        if hasattr(sol, "y"):
            valid_m = min(sol.y.shape[1], M)
            res[:valid_m] = sol.y[:, :valid_m].T
        return res, False, sol.message

    traj = sol.y.T
    is_stable = bool(np.all(np.isfinite(traj)) and np.max(np.abs(traj)) < divergence_bound)
    return traj, is_stable, sol.message


def evaluate_tree_rollout(
    trees: List[ExpressionTree],
    true_test_trajectory: np.ndarray,
    t_eval: np.ndarray,
    divergence_bound: float = 1e4,
) -> Tuple[float, float, bool]:
    """
    Simulates discovered symbolic trees from test x0 and computes:
    1. Absolute RMSE
    2. Relative RMSE
    3. Stability flag
    """
    x0 = true_test_trajectory[0]
    sim_traj, is_stable, msg = simulate_expression_trees(
        trees=trees,
        x0=x0,
        t_eval=t_eval,
        divergence_bound=divergence_bound,
    )

    if not is_stable or np.isnan(sim_traj).any():
        return 999.0, 999.0, False

    diff = sim_traj - true_test_trajectory
    rmse = float(np.sqrt(np.mean(diff ** 2)))
    true_norm = float(np.sqrt(np.mean(true_test_trajectory ** 2))) + 1e-12
    rel_rmse = float(rmse / true_norm)
    return rmse, rel_rmse, True
