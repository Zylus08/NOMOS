"""
NOMOS Ridge-Stabilized Least Squares & Rank-Deficient Matrix Handling
Agents D05 & D06
"""

from typing import Tuple
import numpy as np


def ridge_solve(
    A: np.ndarray,
    B: np.ndarray,
    alpha: float = 1e-5,
    rcond: float = 1e-12,
) -> Tuple[np.ndarray, float]:
    """
    Solve regularized least squares problem:
        min_X ||A X - B||_F^2 + alpha ||X||_F^2
    Handles rank-deficient A via SVD filtering:
        X = (A^T A + alpha I)^{-1} A^T B
    Returns: (X, condition_number)
    """
    A = np.asarray(A, dtype=np.float64)
    B = np.asarray(B, dtype=np.float64)

    M, P = A.shape
    # Compute condition number
    s = np.linalg.svd(A, compute_uv=False)
    cond = float(s[0] / (s[-1] + 1e-15)) if len(s) > 0 else 1.0

    if alpha <= 0.0:
        # Standard least squares with pseudoinverse
        X, residuals, rank, s_vals = np.linalg.lstsq(A, B, rcond=rcond)
        return X, cond

    # Normal equations with Tikhonov damping
    AtA = A.T @ A
    AtB = A.T @ B
    reg = alpha * np.eye(P)
    try:
        X = np.linalg.solve(AtA + reg, AtB)
    except np.linalg.LinAlgError:
        # SVD fallback for severe degeneracy
        X = np.linalg.pinv(AtA + reg, rcond=rcond) @ AtB

    return X, cond
