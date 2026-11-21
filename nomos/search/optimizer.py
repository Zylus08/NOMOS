"""
NOMOS Continuous Coefficient Optimization
Milestone M2 — Phase 6 Joint Structure & Coefficient Optimization
Agents D12 & D13
"""

from typing import Callable, List, Optional, Tuple
import numpy as np
from scipy.optimize import minimize

from nomos.symbolic.trees import ExpressionTree


def optimize_coefficients(
    tree: ExpressionTree,
    X: np.ndarray,
    y_target: np.ndarray,
    method: str = "L-BFGS-B",
    max_iter: int = 40,
    reg_lambda: float = 1e-6,
) -> Tuple[ExpressionTree, float]:
    """
    Optimize continuous constant nodes in the expression tree to minimize:
        Loss(c) = 1/M * ||y_target - tree(X; c)||^2 + reg_lambda * ||c||^2
    """
    constants = tree.get_constants()
    if not constants:
        # No constants to optimize; compute baseline loss
        pred = tree.evaluate(X)
        loss = float(np.mean((y_target.ravel() - pred.ravel()) ** 2))
        return tree.copy(), loss

    init_c = np.array(constants, dtype=np.float64)
    y_flat = y_target.ravel()
    M = len(y_flat)

    # Protect against extreme initial constants
    init_c = np.clip(init_c, -100.0, 100.0)

    work_tree = tree.copy()

    def loss_fun(c_vals):
        work_tree.set_constants(c_vals.tolist())
        pred = work_tree.evaluate(X).ravel()
        if not np.all(np.isfinite(pred)):
            return 1e10
        mse = np.mean((y_flat - pred) ** 2)
        reg = reg_lambda * np.sum(c_vals ** 2)
        return float(mse + reg)

    try:
        res = minimize(
            loss_fun,
            init_c,
            method=method,
            options={"maxiter": max_iter, "disp": False},
        )
        opt_c = res.x
        final_loss = float(res.fun)
    except Exception:
        # Fallback to Nelder-Mead
        try:
            res = minimize(loss_fun, init_c, method="Nelder-Mead", options={"maxiter": max_iter})
            opt_c = res.x
            final_loss = float(res.fun)
        except Exception:
            opt_c = init_c
            final_loss = loss_fun(init_c)

    best_tree = tree.copy()
    best_tree.set_constants(opt_c.tolist())
    return best_tree, final_loss
