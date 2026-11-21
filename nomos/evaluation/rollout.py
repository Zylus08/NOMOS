"""
NOMOS Closed-Loop ODE Rollout Evaluation
Agents F02 & F03
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Any
import numpy as np
from scipy.integrate import solve_ivp
from nomos.core.library import BaseFeatureLibrary


@dataclass
class RolloutResult:
    t: np.ndarray
    x_sim: np.ndarray
    rmse: float
    relative_rmse: float
    is_stable: bool
    failed: bool
    message: str


def simulate_discovered_model(
    Xi: np.ndarray,
    library: BaseFeatureLibrary,
    x0: np.ndarray,
    t_eval: np.ndarray,
    t_span: Optional[Tuple[float, float]] = None,
    rtol: float = 1e-7,
    atol: float = 1e-7,
    max_step: float = 0.05,
    divergence_bound: float = 1e4,
) -> Tuple[np.ndarray, bool, str]:
    """
    Numerically integrate discovered governing equations:
        dx/dt = Theta(x) * Xi
    Includes protection against stiffness, NaN blowup, or numerical explosion.
    """
    Xi = np.asarray(Xi, dtype=np.float64)
    x0 = np.asarray(x0, dtype=np.float64)
    if t_span is None:
        t_span = (t_eval[0], t_eval[-1])

    def rhs(t, state):
        if not np.all(np.isfinite(state)) or np.max(np.abs(state)) > divergence_bound:
            return np.zeros_like(state)
        # Transform state vector of shape (1, n)
        state_2d = state[np.newaxis, :]
        theta_row = library.transform(state_2d)
        dx = theta_row @ Xi
        return dx.ravel()

    sol = solve_ivp(
        rhs,
        t_span=t_span,
        y0=x0,
        t_eval=t_eval,
        method="RK45",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )

    if not sol.success or len(sol.t) != len(t_eval):
        # Fallback padding with NaNs if diverged early
        M = len(t_eval)
        n = len(x0)
        res = np.full((M, n), np.nan)
        if hasattr(sol, "y"):
            valid_m = min(sol.y.shape[1], M)
            res[:valid_m] = sol.y[:, :valid_m].T
        return res, False, sol.message

    traj = sol.y.T
    is_finite = bool(np.all(np.isfinite(traj)) and np.max(np.abs(traj)) < divergence_bound)
    return traj, is_finite, sol.message


def evaluate_rollout(
    Xi: np.ndarray,
    library: BaseFeatureLibrary,
    true_trajectory: np.ndarray,
    t_eval: np.ndarray,
    divergence_bound: float = 1e4,
) -> RolloutResult:
    """
    Evaluate closed-loop rollout RMSE against ground truth trajectory.
    """
    x0 = true_trajectory[0]
    sim_x, is_stable, msg = simulate_discovered_model(
        Xi, library, x0, t_eval, divergence_bound=divergence_bound
    )

    if not is_stable or np.isnan(sim_x).any():
        return RolloutResult(
            t=t_eval,
            x_sim=sim_x,
            rmse=float("inf"),
            relative_rmse=float("inf"),
            is_stable=False,
            failed=True,
            message=f"Rollout diverged or exploded: {msg}",
        )

    diff = sim_x - true_trajectory
    rmse = float(np.sqrt(np.mean(diff ** 2)))
    true_rms = float(np.sqrt(np.mean(true_trajectory ** 2)))
    rel_rmse = float(rmse / (true_rms + 1e-12))

    return RolloutResult(
        t=t_eval,
        x_sim=sim_x,
        rmse=rmse,
        relative_rmse=rel_rmse,
        is_stable=True,
        failed=False,
        message="Success",
    )
