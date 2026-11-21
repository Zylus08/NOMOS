"""
NOMOS Feature Scaling & Mathematically Exact Coefficient Unscaling
Agent D04
"""

from typing import Tuple
import numpy as np


class FeatureScaler:
    """
    Scales candidate library columns by their L2 norm or std to condition the regression matrix.
    Mathematically exact relation:
        Theta_scaled = Theta * D^{-1}  where D = diag(d_1, ..., d_P)
        X_dot = Theta_scaled * Xi_scaled = Theta * (D^{-1} * Xi_scaled)
        => Xi_true = D^{-1} * Xi_scaled
    """

    def __init__(self, mode: str = "l2"):
        self.mode = mode
        self.scale_factors_: Optional[np.ndarray] = None

    def fit(self, Theta: np.ndarray) -> "FeatureScaler":
        Theta = np.asarray(Theta, dtype=np.float64)
        if self.mode == "l2":
            scales = np.linalg.norm(Theta, axis=0)
        elif self.mode == "std":
            scales = np.std(Theta, axis=0)
        else:
            raise ValueError(f"Unknown scaling mode: {self.mode}")

        # Protect zero or constant columns
        scales[scales < 1e-12] = 1.0
        self.scale_factors_ = scales
        return self

    def transform(self, Theta: np.ndarray) -> np.ndarray:
        if self.scale_factors_ is None:
            raise RuntimeError("Scaler must be fitted before transform")
        return Theta / self.scale_factors_

    def fit_transform(self, Theta: np.ndarray) -> np.ndarray:
        return self.fit(Theta).transform(Theta)

    def unscale_coefficients(self, Xi_scaled: np.ndarray) -> np.ndarray:
        """
        Unscale learned coefficient matrix Xi_scaled back to physical units:
        Xi[j, :] = Xi_scaled[j, :] / scale_factors_[j]
        """
        if self.scale_factors_ is None:
            raise RuntimeError("Scaler not fitted")
        Xi_scaled = np.asarray(Xi_scaled, dtype=np.float64)
        return Xi_scaled / self.scale_factors_[:, np.newaxis]
