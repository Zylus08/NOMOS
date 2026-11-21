"""
NOMOS Spline-Based Numerical Differentiation
Agent D13
"""

from typing import Optional
import numpy as np
from scipy.interpolate import UnivariateSpline


def spline_derivative(
    t: np.ndarray,
    x: np.ndarray,
    s: Optional[float] = None,
    k: int = 4,
) -> np.ndarray:
    """
    Differentiate state trajectories using smoothing B-splines.
    s: smoothing factor. If None, uses default cross-validation / variance estimate.
    k: spline degree (k=4 gives cubic spline with continuous 2nd derivative).
    """
    x = np.asarray(x, dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)
    is_1d = (x.ndim == 1)
    if is_1d:
        x = x[:, np.newaxis]

    M, n = x.shape
    x_dot = np.zeros_like(x)

    for dim in range(n):
        series = x[:, dim]
        # Automatic smoothing factor based on residual noise estimate if s is None
        smooth_param = s
        if smooth_param is None:
            # Estimate noise variance from second differences
            diff2 = np.diff(series, n=2)
            var_est = np.var(diff2) / 6.0
            smooth_param = var_est * M if var_est > 1e-12 else 0.0

        spline = UnivariateSpline(t, series, k=min(k, M - 1), s=smooth_param)
        x_dot[:, dim] = spline.derivative(n=1)(t)

    if is_1d:
        return x_dot[:, 0]
    return x_dot
