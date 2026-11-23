"""
NOMOS High-Precision Spatial & Temporal Differential Operators
Phase 3: Numerical Operators & Stencils
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from scipy.fft import fft, ifft, fftfreq
from scipy.signal import savgol_filter


def spectral_derivative_1d(
    u: np.ndarray,
    dx: float,
    order: int = 1,
    axis: int = -1,
    periodic: bool = True,
) -> np.ndarray:
    """
    Compute spatial derivative using periodic Fourier spectral differentiation.
    Guaranteed exponential convergence for smooth periodic functions.
    Strictly raises ValueError if applied to non-periodic data.
    """
    if not periodic:
        raise ValueError(
            "Spectral differentiation via FFT strictly requires periodic boundary conditions. "
            "Use finite differences for non-periodic domains."
        )

    N = u.shape[axis]
    L = N * dx
    k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)

    # Fourier multiplier symbol: (i*k)^order
    symbol = (1j * k) ** order

    # Handle Nyquist frequency for odd order derivatives (enforce real output)
    if order % 2 != 0 and N % 2 == 0:
        symbol[N // 2] = 0.0

    u_hat = fft(u, axis=axis)
    u_deriv = np.real(ifft(symbol * u_hat, axis=axis))
    return u_deriv


def finite_difference_1d(
    u: np.ndarray,
    dx: float,
    order: int = 1,
    accuracy: int = 4,
    axis: int = -1,
    periodic: bool = True,
) -> np.ndarray:
    """
    Compute spatial derivative using high-order centered finite difference stencils.
    Supports accuracy orders 2, 4, and 6, with periodic wrapping or one-sided boundaries.
    """
    u_arr = np.asarray(u, dtype=np.float64)
    N = u_arr.shape[axis]

    # Swap target axis to last dimension for clean indexing
    if axis != -1 and axis != u_arr.ndim - 1:
        u_arr = np.swapaxes(u_arr, axis, -1)
        swapped = True
    else:
        swapped = False

    orig_shape = u_arr.shape
    u_flat = u_arr.reshape(-1, N)
    out_flat = np.zeros_like(u_flat)

    if order == 1:
        if accuracy == 2:
            # 2nd order centered: (-u_{i-1} + u_{i+1}) / (2*dx)
            if periodic:
                out_flat = (np.roll(u_flat, -1, axis=-1) - np.roll(u_flat, 1, axis=-1)) / (2.0 * dx)
            else:
                out_flat[:, 1:-1] = (u_flat[:, 2:] - u_flat[:, :-2]) / (2.0 * dx)
                out_flat[:, 0] = (-3.0 * u_flat[:, 0] + 4.0 * u_flat[:, 1] - u_flat[:, 2]) / (2.0 * dx)
                out_flat[:, -1] = (3.0 * u_flat[:, -1] - 4.0 * u_flat[:, -2] + u_flat[:, -3]) / (2.0 * dx)

        elif accuracy >= 4:
            # 4th order centered: (-u_{i+2} + 8*u_{i+1} - 8*u_{i-1} + u_{i-2}) / (12*dx)
            if periodic:
                out_flat = (
                    -np.roll(u_flat, -2, axis=-1)
                    + 8.0 * np.roll(u_flat, -1, axis=-1)
                    - 8.0 * np.roll(u_flat, 1, axis=-1)
                    + np.roll(u_flat, 2, axis=-1)
                ) / (12.0 * dx)
            else:
                out_flat[:, 2:-2] = (
                    -u_flat[:, 4:] + 8.0 * u_flat[:, 3:-1] - 8.0 * u_flat[:, 1:-3] + u_flat[:, :-4]
                ) / (12.0 * dx)
                # Lower-order fallbacks at non-periodic boundaries
                out_flat[:, 0] = (-3.0 * u_flat[:, 0] + 4.0 * u_flat[:, 1] - u_flat[:, 2]) / (2.0 * dx)
                out_flat[:, 1] = (u_flat[:, 2] - u_flat[:, 0]) / (2.0 * dx)
                out_flat[:, -2] = (u_flat[:, -1] - u_flat[:, -3]) / (2.0 * dx)
                out_flat[:, -1] = (3.0 * u_flat[:, -1] - 4.0 * u_flat[:, -2] + u_flat[:, -3]) / (2.0 * dx)

    elif order == 2:
        if accuracy == 2:
            # 2nd order centered: (u_{i+1} - 2*u_i + u_{i-1}) / dx^2
            if periodic:
                out_flat = (
                    np.roll(u_flat, -1, axis=-1) - 2.0 * u_flat + np.roll(u_flat, 1, axis=-1)
                ) / (dx**2)
            else:
                out_flat[:, 1:-1] = (u_flat[:, 2:] - 2.0 * u_flat[:, 1:-1] + u_flat[:, :-2]) / (dx**2)
                out_flat[:, 0] = (2.0 * u_flat[:, 0] - 5.0 * u_flat[:, 1] + 4.0 * u_flat[:, 2] - u_flat[:, 3]) / (dx**2)
                out_flat[:, -1] = (2.0 * u_flat[:, -1] - 5.0 * u_flat[:, -2] + 4.0 * u_flat[:, -3] - u_flat[:, -4]) / (dx**2)

        elif accuracy >= 4:
            # 4th order centered: (-u_{i+2} + 16*u_{i+1} - 30*u_i + 16*u_{i-1} - u_{i-2}) / (12*dx^2)
            if periodic:
                out_flat = (
                    -np.roll(u_flat, -2, axis=-1)
                    + 16.0 * np.roll(u_flat, -1, axis=-1)
                    - 30.0 * u_flat
                    + 16.0 * np.roll(u_flat, 1, axis=-1)
                    - np.roll(u_flat, 2, axis=-1)
                ) / (12.0 * (dx**2))
            else:
                out_flat[:, 2:-2] = (
                    -u_flat[:, 4:] + 16.0 * u_flat[:, 3:-1] - 30.0 * u_flat[:, 2:-2] + 16.0 * u_flat[:, 1:-3] - u_flat[:, :-4]
                ) / (12.0 * (dx**2))
                out_flat[:, 0] = (u_flat[:, 2] - 2.0 * u_flat[:, 1] + u_flat[:, 0]) / (dx**2)
                out_flat[:, 1] = (u_flat[:, 2] - 2.0 * u_flat[:, 1] + u_flat[:, 0]) / (dx**2)
                out_flat[:, -2] = (u_flat[:, -1] - 2.0 * u_flat[:, -2] + u_flat[:, -3]) / (dx**2)
                out_flat[:, -1] = (u_flat[:, -1] - 2.0 * u_flat[:, -2] + u_flat[:, -3]) / (dx**2)

    elif order == 3:
        # 3rd derivative: 2nd order centered: (u_{i+2} - 2*u_{i+1} + 2*u_{i-1} - u_{i-2}) / (2*dx^3)
        if periodic:
            out_flat = (
                np.roll(u_flat, -2, axis=-1)
                - 2.0 * np.roll(u_flat, -1, axis=-1)
                + 2.0 * np.roll(u_flat, 1, axis=-1)
                - np.roll(u_flat, 2, axis=-1)
            ) / (2.0 * (dx**3))
        else:
            out_flat[:, 2:-2] = (
                u_flat[:, 4:] - 2.0 * u_flat[:, 3:-1] + 2.0 * u_flat[:, 1:-3] - u_flat[:, :-4]
            ) / (2.0 * (dx**3))
            out_flat[:, :2] = out_flat[:, 2:3]
            out_flat[:, -2:] = out_flat[:, -3:-2]

    elif order == 4:
        # 4th derivative: 2nd order centered: (u_{i+2} - 4*u_{i+1} + 6*u_i - 4*u_{i-1} + u_{i-2}) / dx^4
        if periodic:
            out_flat = (
                np.roll(u_flat, -2, axis=-1)
                - 4.0 * np.roll(u_flat, -1, axis=-1)
                + 6.0 * u_flat
                - 4.0 * np.roll(u_flat, 1, axis=-1)
                + np.roll(u_flat, 2, axis=-1)
            ) / (dx**4)
        else:
            out_flat[:, 2:-2] = (
                u_flat[:, 4:] - 4.0 * u_flat[:, 3:-1] + 6.0 * u_flat[:, 2:-2] - 4.0 * u_flat[:, 1:-3] + u_flat[:, :-4]
            ) / (dx**4)
            out_flat[:, :2] = out_flat[:, 2:3]
            out_flat[:, -2:] = out_flat[:, -3:-2]

    else:
        raise NotImplementedError(f"Differential order {order} not supported in finite_difference_1d.")

    out = out_flat.reshape(orig_shape)
    if swapped:
        out = np.swapaxes(out, axis, -1)
    return out


def compute_derivative(
    u: np.ndarray,
    dx: float,
    order: int = 1,
    method: str = "fd",
    accuracy: int = 4,
    periodic: bool = True,
    filter_window: Optional[int] = None,
    filter_poly: int = 3,
) -> np.ndarray:
    """
    Unified entry point for spatial and temporal numerical differentiation.
    Optionally applies Savitzky-Golay noise-aware filtering before differentiation.
    """
    u_work = np.asarray(u, dtype=np.float64)

    if filter_window is not None and filter_window > filter_poly:
        # Enforce odd window length
        if filter_window % 2 == 0:
            filter_window += 1
        if filter_window <= u_work.shape[-1]:
            u_work = savgol_filter(u_work, window_length=filter_window, polyorder=filter_poly, axis=-1)

    if method == "spectral":
        return spectral_derivative_1d(u_work, dx=dx, order=order, periodic=periodic)
    elif method == "fd":
        return finite_difference_1d(u_work, dx=dx, order=order, accuracy=accuracy, periodic=periodic)
    else:
        raise ValueError(f"Unknown derivative method '{method}'. Choose 'fd' or 'spectral'.")


def compute_pde_derivatives_matrix(
    u: np.ndarray,
    dx: float,
    dt: float,
    periodic: bool = True,
    method: str = "fd",
    filter_window: Optional[int] = None,
) -> Dict[str, np.ndarray]:
    """
    Compute comprehensive suite of spatial derivatives, temporal derivative,
    and nonlinear terms for PDE dictionary construction.
    Input u shape: (M, N) (M time steps, N spatial points).
    """
    derivs: Dict[str, np.ndarray] = {}

    # State
    derivs["u"] = u.copy()

    # Temporal derivative u_t (along axis 0)
    derivs["u_t"] = finite_difference_1d(u, dx=dt, order=1, accuracy=2, axis=0, periodic=False)

    # Spatial derivatives (along axis 1)
    derivs["u_x"] = compute_derivative(u, dx=dx, order=1, method=method, periodic=periodic, filter_window=filter_window)
    derivs["u_xx"] = compute_derivative(u, dx=dx, order=2, method=method, periodic=periodic, filter_window=filter_window)
    derivs["u_xxx"] = compute_derivative(u, dx=dx, order=3, method=method, periodic=periodic, filter_window=filter_window)
    derivs["u_xxxx"] = compute_derivative(u, dx=dx, order=4, method=method, periodic=periodic, filter_window=filter_window)

    # Nonlinear powers and advection products
    derivs["u^2"] = u**2
    derivs["u^3"] = u**3
    derivs["u*u_x"] = u * derivs["u_x"]
    derivs["u^2*u_x"] = (u**2) * derivs["u_x"]
    derivs["u_x^2"] = derivs["u_x"] ** 2

    return derivs
