"""
NOMOS Composite & Custom Candidate Feature Library
Agent D10
"""

from typing import List, Optional
import numpy as np
from nomos.core.library import BaseFeatureLibrary


class CompositeLibrary(BaseFeatureLibrary):
    """
    Concatenates multiple candidate libraries (e.g. Polynomial + Trigonometric).
    Automatically de-duplicates constant terms.
    """

    def __init__(self, libraries: List[BaseFeatureLibrary]):
        self.libraries = list(libraries)
        self.feature_names_: List[str] = []
        self.n_features_in_: int = 0

    def fit(self, X: np.ndarray, variable_names: Optional[List[str]] = None) -> "CompositeLibrary":
        X = np.asarray(X)
        self.n_features_in_ = X.shape[1]

        all_names = []
        for lib in self.libraries:
            lib.fit(X, variable_names)
            for name in lib.get_feature_names():
                # Avoid duplicate '1' if present in multiple sub-libraries
                if name == "1" and "1" in all_names:
                    continue
                all_names.append(name)

        self.feature_names_ = all_names
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        parts = []
        seen_names = set()

        for lib in self.libraries:
            t = lib.transform(X)
            names = lib.get_feature_names()
            for col_idx, name in enumerate(names):
                if name == "1" and "1" in seen_names:
                    continue
                seen_names.add(name)
                parts.append(t[:, col_idx : col_idx + 1])

        return np.column_stack(parts)

    def get_feature_names(self) -> List[str]:
        return list(self.feature_names_)

    @property
    def num_features(self) -> int:
        return len(self.feature_names_)
