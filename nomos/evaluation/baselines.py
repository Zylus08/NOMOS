"""
NOMOS Independent Baselines (Ordinary Least Squares & PySINDy Adapter)
Agents F09 & F10
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from nomos.core.library import BaseFeatureLibrary
from nomos.sparse.ridge import ridge_solve


class OLSBaseline:
    """
    Standard unregularized dense Ordinary Least Squares baseline (Agent F09).
    Does NOT perform sparse thresholding; fits all candidate terms.
    Serves as an empirical lower bound for dense prediction vs sparse recovery.
    """

    def __init__(self):
        self.coef_: Optional[np.ndarray] = None

    def fit(self, Theta: np.ndarray, X_dot: np.ndarray) -> "OLSBaseline":
        Xi, _ = ridge_solve(Theta, X_dot, alpha=0.0)
        self.coef_ = Xi
        return self


class PySINDyAdapter:
    """
    Independent reference baseline wrapping external PySINDy package (Agent F10).
    Runs under IDENTICAL training data, candidate basis degree, and thresholding parameters.
    """

    def __init__(self, threshold: float = 0.1, alpha: float = 1e-5, degree: int = 2):
        self.threshold = float(threshold)
        self.alpha = float(alpha)
        self.degree = int(degree)
        self.model = None
        self.coef_: Optional[np.ndarray] = None

    def fit(
        self,
        X: np.ndarray,
        t: np.ndarray,
        x_dot: Optional[np.ndarray] = None,
        feature_names: Optional[List[str]] = None,
    ) -> "PySINDyAdapter":
        import pysindy as ps
        from nomos.differentiation import finite_difference

        if x_dot is None:
            x_dot = finite_difference(t, X, order=4)

        opt = ps.STLSQ(threshold=self.threshold, alpha=self.alpha, max_iter=50)
        lib = ps.PolynomialLibrary(degree=self.degree, include_bias=True)

        self.model = ps.SINDy(
            optimizer=opt,
            feature_library=lib,
        )

        dt = float(np.mean(np.diff(t)))
        self.model.fit(X, t=dt, x_dot=x_dot, feature_names=feature_names)

        # PySINDy coefficients are (n, P), transpose to NOMOS format (P, n)
        self.coef_ = self.model.coefficients().T
        return self
