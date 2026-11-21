"""
NOMOS Initial Condition & Parameter Regime Sampling
Agents C02 & C03
"""

from typing import List, Optional, Tuple
import numpy as np


def sample_initial_conditions(
    bounds: List[Tuple[float, float]],
    n_samples: int,
    method: str = "latin_hypercube",
    seed: int = 42,
) -> List[np.ndarray]:
    """
    Sample diverse initial conditions across phase space bounds.
    Methods:
    - 'latin_hypercube': Stratified hypercube sampling
    - 'uniform': Uniform pseudo-random sampling
    - 'grid': Cartesian corner and center grid
    """
    rng = np.random.default_rng(seed)
    dim = len(bounds)
    bounds_arr = np.array(bounds, dtype=np.float64)
    lows = bounds_arr[:, 0]
    highs = bounds_arr[:, 1]
    spans = highs - lows

    if method == "latin_hypercube":
        # Stratified Latin Hypercube
        result = np.zeros((n_samples, dim), dtype=np.float64)
        for d in range(dim):
            intervals = np.linspace(0, 1, n_samples + 1)
            pts = rng.uniform(intervals[:-1], intervals[1:])
            rng.shuffle(pts)
            result[:, d] = lows[d] + pts * spans[d]
        return [result[i] for i in range(n_samples)]

    elif method == "uniform":
        raw = rng.uniform(0.0, 1.0, size=(n_samples, dim))
        scaled = lows + raw * spans
        return [scaled[i] for i in range(n_samples)]

    elif method == "grid":
        # Multi-dimensional grid
        pts_per_dim = max(2, int(np.ceil(n_samples ** (1.0 / dim))))
        grid_axes = [np.linspace(lows[d], highs[d], pts_per_dim) for d in range(dim)]
        mesh = np.meshgrid(*grid_axes)
        stacked = np.column_stack([m.ravel() for m in mesh])
        indices = np.linspace(0, len(stacked) - 1, min(n_samples, len(stacked)), dtype=int)
        return [stacked[i] for i in indices]

    else:
        raise ValueError(f"Unknown sampling method: {method}")
