"""
NOMOS Trigonometric Feature Library
Agent D09
"""

from typing import List, Optional, Tuple
import numpy as np
from nomos.core.library import BaseFeatureLibrary


class TrigonometricLibrary(BaseFeatureLibrary):
    """
    Trigonometric feature library Theta(X) computing sin(k * x_i) and cos(k * x_i).
    """

    def __init__(self, harmonics: List[int] = [1]):
        self.harmonics = list(harmonics)
        self.feature_names_: List[str] = []
        self.specs_: List[Tuple[int, int, str]] = []  # (dim_idx, k, func_type)
        self.n_features_in_: int = 0

    def fit(self, X: np.ndarray, variable_names: Optional[List[str]] = None) -> "TrigonometricLibrary":
        X = np.asarray(X)
        M, n = X.shape
        self.n_features_in_ = n
        var_names = variable_names or [f"x{i}" for i in range(n)]

        specs = []
        feature_names = []

        for d in range(n):
            vname = var_names[d]
            for k in self.harmonics:
                # sin(k*vname)
                k_str = f"{k}*" if k != 1 else ""
                specs.append((d, k, "sin"))
                feature_names.append(f"sin({k_str}{vname})")
                # cos(k*vname)
                specs.append((d, k, "cos"))
                feature_names.append(f"cos({k_str}{vname})")

        self.specs_ = specs
        self.feature_names_ = feature_names
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        M, n = X.shape
        P = len(self.specs_)
        Theta = np.empty((M, P), dtype=np.float64)

        for j, (d, k, fn) in enumerate(self.specs_):
            arg = k * X[:, d]
            Theta[:, j] = np.sin(arg) if fn == "sin" else np.cos(arg)

        return Theta

    def get_feature_names(self) -> List[str]:
        return list(self.feature_names_)

    @property
    def num_features(self) -> int:
        return len(self.feature_names_)
