"""
NOMOS Strong-Form PDE Discovery Engine (PDE-FIND / SINDy-PDE)
Phase 4: Strong-Form Spatiotemporal Identification
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from nomos.pde.schema import SpatiotemporalField
from nomos.pde.operators import compute_pde_derivatives_matrix
from nomos.sparse.stlsq import STLSQ
from nomos.library.scaling import FeatureScaler


@dataclass
class PDEDiscoveryResult:
    """Standardized output of PDE law discovery."""
    pde_name: str
    discovered_equation: str
    feature_names: List[str]
    coefficients: Dict[str, float]
    residual_norm: float
    support_mask: List[bool]
    num_evaluations: int
    execution_time_seconds: float
    discovery_mode: str  # 'strong_form', 'weak_form', 'symbolic_grammar', 'neural_guided'
    metadata: Dict[str, Any] = field(default_factory=dict)


class StrongFormPDEDiscovery:
    """
    Classical strong-form sparse PDE discovery (PDE-FIND / SINDy-PDE).
    Constructs differential candidate library Theta(U) directly from numerical derivatives:
        u_t = Theta(U) * Xi
    Solves via Sequentially Thresholded Least Squares (STLSQ) with physical column scaling.
    """

    def __init__(
        self,
        threshold: float = 0.05,
        alpha: float = 1e-4,
        max_iter: int = 50,
        diff_method: str = "fd",
        filter_window: Optional[int] = None,
        include_cubic: bool = True,
        include_fourth_deriv: bool = True,
    ):
        self.threshold = float(threshold)
        self.alpha = float(alpha)
        self.max_iter = int(max_iter)
        self.diff_method = diff_method
        self.filter_window = filter_window
        self.include_cubic = bool(include_cubic)
        self.include_fourth_deriv = bool(include_fourth_deriv)

    def build_candidate_library(
        self, field: SpatiotemporalField
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Build feature matrix Theta and target vector u_t from observed field.
        Flattens space-time points into rows of design matrix.
        """
        U = field.u
        dx = field.dx
        dt = field.dt
        periodic = field.boundary_condition.value == "periodic"

        derivs = compute_pde_derivatives_matrix(
            U, dx=dx, dt=dt, periodic=periodic, method=self.diff_method, filter_window=self.filter_window
        )

        target = derivs["u_t"].flatten()  # Shape: (M*N,)

        # Feature terms
        feature_dict: Dict[str, np.ndarray] = {
            "u": derivs["u"].flatten(),
            "u_x": derivs["u_x"].flatten(),
            "u_xx": derivs["u_xx"].flatten(),
            "u_xxx": derivs["u_xxx"].flatten(),
            "u*u_x": derivs["u*u_x"].flatten(),
            "u^2": derivs["u^2"].flatten(),
            "u^2*u_x": derivs["u^2*u_x"].flatten(),
        }

        if self.include_cubic:
            feature_dict["u^3"] = derivs["u^3"].flatten()

        if self.include_fourth_deriv:
            feature_dict["u_xxxx"] = derivs["u_xxxx"].flatten()

        # Handle boundaries: if non-periodic, discard outer 2 spatial rows and initial/final time rows
        M, N = U.shape
        if not periodic:
            valid_mask = np.zeros((M, N), dtype=bool)
            valid_mask[2:-2, 2:-2] = True
            valid_flat = valid_mask.flatten()
            target = target[valid_flat]
            for k in feature_dict:
                feature_dict[k] = feature_dict[k][valid_flat]

        feature_names = list(feature_dict.keys())
        Theta = np.column_stack([feature_dict[k] for k in feature_names])

        return Theta, target, feature_names

    def fit(self, field: SpatiotemporalField) -> PDEDiscoveryResult:
        import time

        t0 = time.time()
        Theta, target, feature_names = self.build_candidate_library(field)

        # STLSQ sparse regression
        opt = STLSQ(
            threshold=self.threshold,
            alpha=self.alpha,
            max_iter=self.max_iter,
            normalize_columns=True,
            refit_active_set=True,
        )

        res = opt.fit(Theta, target.reshape(-1, 1))
        coefs = res.coef.flatten()
        duration = time.time() - t0

        # Construct equation string
        active_terms = []
        coef_dict = {}
        for name, val in zip(feature_names, coefs):
            if abs(val) > 1e-4:
                coef_dict[name] = float(val)
                active_terms.append(f"{val:+.4f}*{name}")

        eq_str = "u_t = " + (" ".join(active_terms) if active_terms else "0.0")

        return PDEDiscoveryResult(
            pde_name=field.pde_name,
            discovered_equation=eq_str,
            feature_names=feature_names,
            coefficients=coef_dict,
            residual_norm=float(res.residual_norm),
            support_mask=[abs(c) > 1e-4 for c in coefs],
            num_evaluations=len(feature_names),
            execution_time_seconds=duration,
            discovery_mode="strong_form",
            metadata={
                "threshold": self.threshold,
                "diff_method": self.diff_method,
                "converged": res.converged,
                "iterations": res.iterations,
            },
        )
