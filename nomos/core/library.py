"""
NOMOS Core Library Interfaces
Agent A02 & D10
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np


class BaseFeatureLibrary(ABC):
    """
    Abstract base class for candidate function libraries Theta(X).
    """

    @abstractmethod
    def fit(self, X: np.ndarray, variable_names: Optional[List[str]] = None) -> "BaseFeatureLibrary":
        """Compute feature dimensions and feature names from input state shape."""
        pass

    @abstractmethod
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Evaluate candidate functions on state matrix X (M x n).
        Returns Theta(X) of shape (M x P).
        """
        pass

    def fit_transform(self, X: np.ndarray, variable_names: Optional[List[str]] = None) -> np.ndarray:
        return self.fit(X, variable_names).transform(X)

    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """Return list of human-readable feature names of length P."""
        pass

    @property
    @abstractmethod
    def num_features(self) -> int:
        """Number of candidate functions P."""
        pass
