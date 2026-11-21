"""
NOMOS Savitzky-Golay Numerical Differentiation
Agent D12
"""

from typing import Optional
import numpy as np
from scipy.signal import savgol_filter


def savitzky_golay_derivative(
    t: np.ndarray,
    x: np.ndarray,
    window_length: int = 11,
    polyorder: int = 3,
) -> np.ndarray:
    """
    Differentiate noisy time-series x(t) using Savitzky-Golay polynomial filter.
    Optimal for suppressing moderate high-frequency observation noise.
    """
    x = np.asarray(x, dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)
    is_1d = (x.ndim == 1)
    if is_1d:
        x = x[:, np.newaxis]

    M, n = x.shape
    dt = float(np.mean(np.diff(t)))

    # Ensure window_length is odd and <= M
    if window_length >= M:
        window_length = M - 1 if (M % 2 == 0) else M
    if window_length % 2 == 0:
        window_length += 1
    if window_length <= polyorder:
        polyorder = max(1, window_length - 1)

    x_dot = np.zeros_like(x)
    for dim in range(n):
        x_dot[:, dim] = savgol_filter(
            x[:, dim],
            window_length=window_length,
            polyorder=polyorder,
            deriv=1,
            delta=dt,
            mode="interp",
        )

    if is_1d:
        return x_dot[:, 0]
    return x_dot
