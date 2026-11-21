"""
NOMOS Polynomial Feature Library
Agent D08
"""

import itertools
from typing import List, Optional, Tuple
import numpy as np
from nomos.core.library import BaseFeatureLibrary


class PolynomialLibrary(BaseFeatureLibrary):
    """
    Polynomial candidate function library Theta(X) up to degree d.
    Includes constant term (if include_bias=True), linear terms, and cross-products.
    """

    def __init__(self, degree: int = 2, include_bias: bool = True):
        self.degree = int(degree)
        self.include_bias = bool(include_bias)
        self.feature_names_: List[str] = []
        self.combinations_: List[Tuple[int, ...]] = []
        self.n_features_in_: int = 0

    def fit(self, X: np.ndarray, variable_names: Optional[List[str]] = None) -> "PolynomialLibrary":
        X = np.asarray(X)
        M, n = X.shape
        self.n_features_in_ = n
        var_names = variable_names or [f"x{i}" for i in range(n)]

        combinations = []
        feature_names = []

        # Degree 0
        if self.include_bias:
            combinations.append(())
            feature_names.append("1")

        # Degree 1 to degree
        for d in range(1, self.degree + 1):
            for combo in itertools.combinations_with_replacement(range(n), d):
                combinations.append(combo)
                # Format name e.g. "x", "x^2", "x*y"
                counts = {}
                for idx in combo:
                    counts[var_names[idx]] = counts.get(var_names[idx], 0) + 1
                parts = []
                for vname, cnt in counts.items():
                    if cnt == 1:
                        parts.append(vname)
                    else:
                        parts.append(f"{vname}^{cnt}")
                feature_names.append("*".join(parts))

        self.combinations_ = combinations
        self.feature_names_ = feature_names
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        M, n = X.shape
        if n != self.n_features_in_:
            raise ValueError(f"X has {n} features, library fitted with {self.n_features_in_}")

        P = len(self.combinations_)
        Theta = np.empty((M, P), dtype=np.float64)

        for j, combo in enumerate(self.combinations_):
            if len(combo) == 0:
                Theta[:, j] = 1.0
            else:
                prod = np.ones(M, dtype=np.float64)
                for idx in combo:
                    prod *= X[:, idx]
                Theta[:, j] = prod

        return Theta

    def get_feature_names(self) -> List[str]:
        return list(self.feature_names_)

    @property
    def num_features(self) -> int:
        return len(self.feature_names_)
