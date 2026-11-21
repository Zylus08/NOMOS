"""
NOMOS Neural Guidance & Feature Importance Engine
Milestone M2 — Phase 5 Neural-Guided Symbolic Search
Agents D09 & D10
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from nomos.symbolic.primitives import NodeType
from nomos.neural.surrogate import NeuralDynamicsSurrogate


@dataclass
class GuidanceProfile:
    """
    Guidance extracted from Neural Surrogate to prioritize symbolic candidates.
    """
    state_importance: Dict[str, float]  # Importance score per variable
    operator_weights: Dict[NodeType, float]  # Prioritized probabilities per operator
    is_strongly_nonlinear: bool
    recommended_primitives: List[str]


class NeuralGuidanceEngine:
    """
    Extracts structural priors from trained Neural Surrogate:
    1. Jacobian Sensitivity Analysis: Identifies active state variables.
    2. Curvature & Nonlinearity Spectrum: Detects trigonometric, rational, or polynomial shapes.
    """

    def __init__(self, surrogate: NeuralDynamicsSurrogate, variable_names: List[str]):
        self.surrogate = surrogate
        self.variable_names = list(variable_names)

    def extract_guidance(self, X_sample: np.ndarray, target_dim: int = 0) -> GuidanceProfile:
        M = min(150, len(X_sample))
        X_sub = X_sample[:M]

        # 1. Compute Jacobian sensitivity
        jacobians = self.surrogate.compute_jacobian(X_sub)  # (M, state_dim, state_dim)
        # Average absolute gradient of target variable with respect to all states
        grad_target = np.abs(jacobians[:, target_dim, :])  # (M, state_dim)
        mean_sens = np.mean(grad_target, axis=0)  # (state_dim,)
        total_sens = np.sum(mean_sens) + 1e-12
        norm_sens = mean_sens / total_sens

        var_importance = {
            self.variable_names[i]: float(norm_sens[i])
            for i in range(len(self.variable_names))
        }

        # 2. Curvature / Nonlinearity test
        # Compare surrogate predictions with best linear model fit
        y_pred = self.surrogate.predict_numpy(X_sub)[:, target_dim]
        # Linear fit residual
        A = np.column_stack([np.ones(M), X_sub])
        w, _, _, _ = np.linalg.lstsq(A, y_pred, rcond=1e-10)
        lin_pred = A @ w
        lin_residual = np.mean((y_pred - lin_pred) ** 2)
        total_var = np.var(y_pred) + 1e-12
        nonlin_ratio = float(lin_residual / total_var)

        is_strongly_nonlinear = (nonlin_ratio > 0.08)

        # 3. Formulate operator prior weights
        op_weights = {
            NodeType.ADD: 1.0,
            NodeType.SUB: 1.0,
            NodeType.MUL: 1.2,
            NodeType.NEG: 0.8,
            NodeType.SIN: 0.3,
            NodeType.COS: 0.3,
            NodeType.DIV: 0.2,
            NodeType.EXP: 0.1,
            NodeType.LOG: 0.1,
        }

        recommended = ["add", "sub", "mul"]

        if is_strongly_nonlinear:
            # Check periodicity / boundedness
            min_y, max_y = np.min(y_pred), np.max(y_pred)
            op_weights[NodeType.SIN] = 1.5
            op_weights[NodeType.COS] = 1.5
            recommended.extend(["sin", "cos"])

            # Check for rational/asymptote signature
            grad_std = np.std(grad_target, axis=0)
            if np.max(grad_std) > 2.0 * np.mean(grad_std):
                op_weights[NodeType.DIV] = 1.2
                recommended.append("div")

        return GuidanceProfile(
            state_importance=var_importance,
            operator_weights=op_weights,
            is_strongly_nonlinear=is_strongly_nonlinear,
            recommended_primitives=recommended,
        )
