"""
NOMOS Derivative Error Diagnostics
Agent D14
"""

from typing import Dict, List, Optional, Any
import numpy as np


def evaluate_derivative_error(
    x_dot_estimated: np.ndarray,
    x_dot_true: np.ndarray,
    variable_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Compute RMSE, MAE, Max Error, and Relative Error of estimated derivatives
    against true continuous derivatives.
    """
    x_dot_estimated = np.asarray(x_dot_estimated, dtype=np.float64)
    x_dot_true = np.asarray(x_dot_true, dtype=np.float64)

    if x_dot_estimated.shape != x_dot_true.shape:
        raise ValueError(f"Shape mismatch: {x_dot_estimated.shape} vs {x_dot_true.shape}")

    diff = x_dot_estimated - x_dot_true
    rmse = float(np.sqrt(np.mean(diff ** 2)))
    mae = float(np.mean(np.abs(diff)))
    max_err = float(np.max(np.abs(diff)))

    true_norm = np.linalg.norm(x_dot_true)
    rel_error = float(np.linalg.norm(diff) / (true_norm + 1e-12))

    per_var = {}
    n_vars = x_dot_true.shape[1] if x_dot_true.ndim > 1 else 1
    names = variable_names or [f"x{i}" for i in range(n_vars)]

    for i, name in enumerate(names):
        d_est = x_dot_estimated[:, i] if x_dot_estimated.ndim > 1 else x_dot_estimated
        d_true = x_dot_true[:, i] if x_dot_true.ndim > 1 else x_dot_true
        d_diff = d_est - d_true
        v_rmse = float(np.sqrt(np.mean(d_diff ** 2)))
        v_rel = float(np.linalg.norm(d_diff) / (np.linalg.norm(d_true) + 1e-12))
        per_var[name] = {"rmse": v_rmse, "relative_error": v_rel}

    return {
        "rmse": rmse,
        "mae": mae,
        "max_error": max_err,
        "relative_error": rel_error,
        "per_variable": per_var,
    }
