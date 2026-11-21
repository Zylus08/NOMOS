"""
NOMOS High-Order Finite Difference Numerical Differentiation
Agent D11
"""

from typing import Optional
import numpy as np


def finite_difference(
    t: np.ndarray,
    x: np.ndarray,
    order: int = 2,
) -> np.ndarray:
    """
    Compute time derivative dx/dt via finite differences with accuracy order 2, 4, or 6.
    Works for 1D or 2D state arrays (M, n).
    Handles uniform or non-uniform time grids.
    """
    x = np.asarray(x, dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)
    is_1d = (x.ndim == 1)
    if is_1d:
        x = x[:, np.newaxis]

    M, n = x.shape
    if M < 3:
        raise ValueError(f"Need at least 3 points for finite difference, got {M}")

    # Check uniform spacing
    dt_arr = np.diff(t)
    dt_mean = np.mean(dt_arr)
    is_uniform = np.allclose(dt_arr, dt_mean, rtol=1e-3, atol=1e-6)

    x_dot = np.zeros_like(x)

    if not is_uniform or order == 2:
        # Standard 2nd-order interior central difference with forward/backward at boundaries
        for i in range(1, M - 1):
            h1 = t[i] - t[i - 1]
            h2 = t[i + 1] - t[i]
            # General non-uniform 2nd-order formula
            x_dot[i] = (
                - (h2 / (h1 * (h1 + h2))) * x[i - 1]
                + ((h2 - h1) / (h1 * h2)) * x[i]
                + (h1 / (h2 * (h1 + h2))) * x[i + 1]
            )
        # Boundaries: 2nd-order one-sided
        h0 = t[1] - t[0]
        h1 = t[2] - t[1]
        x_dot[0] = (
            -(2 * h0 + h1) / (h0 * (h0 + h1)) * x[0]
            + (h0 + h1) / (h0 * h1) * x[1]
            - h0 / (h1 * (h0 + h1)) * x[2]
        )
        h_end1 = t[-1] - t[-2]
        h_end2 = t[-2] - t[-3]
        x_dot[-1] = (
            h_end1 / (h_end2 * (h_end1 + h_end2)) * x[-3]
            - (h_end1 + h_end2) / (h_end1 * h_end2) * x[-2]
            + (2 * h_end1 + h_end2) / (h_end1 * (h_end1 + h_end2)) * x[-1]
        )

    elif order >= 4:
        # Uniform 4th-order central difference
        dt = dt_mean
        if M < 5:
            # Fallback to order 2
            return finite_difference(t, x, order=2)

        # 4th-order central interior: (-x[i+2] + 8*x[i+1] - 8*x[i-1] + x[i-2]) / (12*dt)
        for i in range(2, M - 2):
            x_dot[i] = (-x[i + 2] + 8.0 * x[i + 1] - 8.0 * x[i - 1] + x[i - 2]) / (12.0 * dt)

        # 2nd-order fallback for boundary layer
        x_dot[1] = (x[2] - x[0]) / (2.0 * dt)
        x_dot[-2] = (x[-1] - x[-3]) / (2.0 * dt)
        x_dot[0] = (-3.0 * x[0] + 4.0 * x[1] - x[2]) / (2.0 * dt)
        x_dot[-1] = (3.0 * x[-1] - 4.0 * x[-2] + x[-3]) / (2.0 * dt)

    if is_1d:
        return x_dot[:, 0]
    return x_dot
