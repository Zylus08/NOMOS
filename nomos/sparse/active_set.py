"""
NOMOS Sparse Active-Set Refitting
Agent D02
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from nomos.sparse.ridge import ridge_solve


def active_set_refit(
    Theta: np.ndarray,
    X_dot: np.ndarray,
    support_mask: np.ndarray,
    alpha: float = 0.0,
) -> np.ndarray:
    """
    Perform unregularized (or lightly stabilized) least-squares regression
    STRICTLY on the active support indices of each equation column.
    Removes L2 / L1 shrinkage bias from learned coefficients.
    """
    Theta = np.asarray(Theta, dtype=np.float64)
    X_dot = np.asarray(X_dot, dtype=np.float64)
    support_mask = np.asarray(support_mask, dtype=bool)

    P, n = support_mask.shape
    Xi_refit = np.zeros((P, n), dtype=np.float64)

    for col in range(n):
        active_idx = np.where(support_mask[:, col])[0]
        if len(active_idx) == 0:
            continue

        Theta_sub = Theta[:, active_idx]
        y_col = X_dot[:, col : col + 1]

        coef_sub, _ = ridge_solve(Theta_sub, y_col, alpha=alpha)
        Xi_refit[active_idx, col] = coef_sub.ravel()

    return Xi_refit
