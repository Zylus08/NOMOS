"""
NOMOS Discovery Engine Configuration
Agent D15
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Any


@dataclass
class DiscoveryConfig:
    """Hyperparameter configuration for discovery engine."""
    diff_method: str = "finite_difference"  # 'finite_difference', 'savitzky_golay', 'spline'
    diff_order: int = 4
    savgol_window: int = 11
    savgol_poly: int = 3
    spline_s: Optional[float] = None

    library_type: str = "polynomial"  # 'polynomial', 'trigonometric', 'composite'
    poly_degree: int = 2
    include_bias: bool = True
    trig_harmonics: List[int] = field(default_factory=lambda: [1])

    threshold: float = 0.1
    alpha: float = 1e-5
    max_iter: int = 50
    normalize_columns: bool = True
    refit_active_set: bool = True
