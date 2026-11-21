"""
NOMOS Derivative & Attractor Metrics
Agents F01, F06, F07, F08
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np


def evaluate_derivative_prediction(
    X_dot_pred: np.ndarray,
    X_dot_true: np.ndarray,
) -> Dict[str, float]:
    """
    Compute RMSE, MAE, and R2 coefficient of determination on derivatives.
    """
    pred = np.asarray(X_dot_pred, dtype=np.float64)
    true = np.asarray(X_dot_true, dtype=np.float64)

    diff = pred - true
    rmse = float(np.sqrt(np.mean(diff ** 2)))
    mae = float(np.mean(np.abs(diff)))

    ss_res = np.sum(diff ** 2)
    ss_tot = np.sum((true - np.mean(true, axis=0)) ** 2)
    r2 = float(1.0 - (ss_res / (ss_tot + 1e-12)))

    return {
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
    }


def evaluate_chaotic_attractor_statistics(
    x_sim: np.ndarray,
    x_true: np.ndarray,
) -> Dict[str, float]:
    """
    Evaluate statistical invariant measure on chaotic attractors (Lorenz-63).
    Compares marginal means, variances, and covariance matrices when pointwise trajectory diverges.
    Agent F08.
    """
    sim_mean = np.mean(x_sim, axis=0)
    true_mean = np.mean(x_true, axis=0)
    mean_err = float(np.linalg.norm(sim_mean - true_mean))

    sim_cov = np.cov(x_sim, rowvar=False)
    true_cov = np.cov(x_true, rowvar=False)
    cov_fro_err = float(np.linalg.norm(sim_cov - true_cov, ord="fro"))

    return {
        "mean_error": mean_err,
        "covariance_frobenius_error": cov_fro_err,
    }
