"""
NOMOS Original Sequentially Thresholded Least Squares (STLSQ)
Agents D01 & D07
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from nomos.core.optimizer import BaseSparseOptimizer, OptimizerResult
from nomos.sparse.ridge import ridge_solve
from nomos.sparse.active_set import active_set_refit
from nomos.library.scaling import FeatureScaler


class STLSQ(BaseSparseOptimizer):
    """
    Original Sequentially Thresholded Least Squares (STLSQ) optimizer.
    Solves: min_Xi ||X_dot - Theta * Xi||_F^2 + alpha ||Xi||_F^2
    subject to hard thresholding: |Xi_phys_jk| < threshold => Xi_phys_jk = 0.
    Features:
    - Built-in column scaling & exact unscaling
    - Thresholding in physical coefficient space (scale-invariant)
    - Active-set unregularized refitting on final support
    - Support convergence and cycle detection
    - Condition number diagnostics
    """

    def __init__(
        self,
        threshold: float = 0.1,
        alpha: float = 1e-5,
        max_iter: int = 50,
        normalize_columns: bool = True,
        refit_active_set: bool = True,
    ):
        self.threshold = float(threshold)
        self.alpha = float(alpha)
        self.max_iter = int(max_iter)
        self.normalize_columns = bool(normalize_columns)
        self.refit_active_set = bool(refit_active_set)

    def fit(self, Theta: np.ndarray, X_dot: np.ndarray) -> OptimizerResult:
        Theta = np.asarray(Theta, dtype=np.float64)
        X_dot = np.asarray(X_dot, dtype=np.float64)
        M, P = Theta.shape
        _, n = X_dot.shape

        scaler = None
        Theta_train = Theta
        if self.normalize_columns:
            scaler = FeatureScaler(mode="l2")
            Theta_train = scaler.fit_transform(Theta)

        # Initial regularized least squares
        Xi_scaled, cond = ridge_solve(Theta_train, X_dot, alpha=self.alpha)

        # Convert to physical coefficients to test threshold
        if scaler is not None:
            Xi_phys = scaler.unscale_coefficients(Xi_scaled)
        else:
            Xi_phys = Xi_scaled

        support = np.abs(Xi_phys) >= self.threshold

        loss_history = []
        converged = False
        iteration = 0
        seen_supports = []

        for it in range(self.max_iter):
            iteration = it + 1
            # Current residual
            res_norm = float(np.linalg.norm(X_dot - Theta_train @ Xi_scaled))
            loss_history.append(res_norm)

            # Refit on active support
            for col in range(n):
                act_idx = np.where(support[:, col])[0]
                if len(act_idx) == 0:
                    Xi_scaled[:, col] = 0.0
                else:
                    Xi_sub, _ = ridge_solve(
                        Theta_train[:, act_idx],
                        X_dot[:, col : col + 1],
                        alpha=self.alpha,
                    )
                    Xi_scaled[:, col] = 0.0
                    Xi_scaled[act_idx, col] = Xi_sub.ravel()

            # Physical coefficients
            if scaler is not None:
                Xi_phys = scaler.unscale_coefficients(Xi_scaled)
            else:
                Xi_phys = Xi_scaled

            # Hard thresholding in physical space
            new_support = np.abs(Xi_phys) >= self.threshold

            # Convergence check: support unchanged
            if np.array_equal(new_support, support):
                converged = True
                break

            # Cycle detection
            support_hash = new_support.tobytes()
            if support_hash in seen_supports:
                converged = True
                break
            seen_supports.append(support_hash)

            support = new_support

        # Final physical coefficients
        if scaler is not None:
            Xi = scaler.unscale_coefficients(Xi_scaled)
        else:
            Xi = Xi_scaled

        # Zero out terms below threshold
        Xi[~support] = 0.0

        # Final active-set refit without shrinkage on unscaled Theta
        final_support = np.abs(Xi) > 1e-12
        if self.refit_active_set:
            Xi = active_set_refit(Theta, X_dot, final_support, alpha=0.0)
            final_support = np.abs(Xi) > 1e-12

        final_residual = float(np.linalg.norm(X_dot - Theta @ Xi))

        return OptimizerResult(
            coef=Xi,
            support=final_support,
            iterations=iteration,
            converged=converged,
            residual_norm=final_residual,
            loss_history=loss_history,
            metadata={
                "threshold": self.threshold,
                "alpha": self.alpha,
                "condition_number": cond,
                "active_count": int(np.count_nonzero(final_support)),
            },
        )
