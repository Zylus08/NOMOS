"""
NOMOS 1D Linear Advection Simulator
PDE: u_t = -c * u_x
"""

from typing import Dict, Optional, Tuple, Callable
import numpy as np
from scipy.fft import fft, ifft, fftfreq

from nomos.pde.schema import (
    BoundaryConditionType,
    Grid1D,
    TimeGrid,
    SpatiotemporalField,
)
from nomos.pde.simulators.base import BasePDESimulator


class LinearAdvectionSimulator(BasePDESimulator):
    """
    Simulates the 1D Hyperbolic Linear Advection Equation:
        u_t + c * u_x = 0  ==>  u_t = -c * u_x
    Default: periodic domain [0, 2*pi] with wave speed c = 1.0.
    """

    def __init__(
        self,
        c: float = 1.0,
        domain: Tuple[float, float] = (0.0, 2.0 * np.pi),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="linear_advection",
            parameters={"c": float(c)},
            boundary_condition=boundary_condition,
            domain=domain,
        )
        self.c = float(c)

    def rhs_spatial(self, u: np.ndarray, x: np.ndarray) -> np.ndarray:
        """Compute -c * u_x using periodic Fourier differentiation."""
        N = len(u)
        L = self.domain[1] - self.domain[0]
        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)
        u_hat = fft(u)
        u_x = np.real(ifft(1j * k * u_hat))
        return -self.c * u_x

    def analytical_solution(
        self, x: np.ndarray, t: float, u0_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> Optional[np.ndarray]:
        """
        Analytical solution u(x, t) = u0(x - c*t).
        Default harmonic: u(x, t) = sin(x - c*t).
        """
        L = self.domain[1] - self.domain[0]
        x_shifted = np.mod(x - self.c * t - self.domain[0], L) + self.domain[0]
        if u0_func is not None:
            return u0_func(x_shifted)
        return np.sin(x_shifted)

    def compute_invariant(self, u: np.ndarray, dx: float) -> float:
        """Energy / L2-norm invariant: E = int u^2 dx (strictly conserved)."""
        return float(np.sum(u**2) * dx)

    def simulate(
        self,
        u0: np.ndarray,
        grid: Grid1D,
        time_grid: TimeGrid,
        noise_level: float = 0.0,
        random_seed: Optional[int] = None,
    ) -> SpatiotemporalField:
        N = grid.num_points
        M = time_grid.num_steps
        L = self.domain[1] - self.domain[0]
        dt = time_grid.dt

        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)
        shift_factor = np.exp(-1j * self.c * k * dt)

        U = np.zeros((M, N), dtype=np.float64)
        U_t_true = np.zeros((M, N), dtype=np.float64)
        u_hat = fft(np.asarray(u0, dtype=np.float64))

        for m in range(M):
            u_real = np.real(ifft(u_hat))
            U[m] = u_real
            # True derivative u_t = -c * u_x = -c * ifft(i*k*u_hat)
            U_t_true[m] = np.real(ifft(-1j * self.c * k * u_hat))
            u_hat = u_hat * shift_factor

        U_clean = U.copy()
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed or 42)
            sigma = noise_level * np.std(U_clean)
            U = U_clean + rng.normal(0.0, sigma, size=U.shape)

        return SpatiotemporalField(
            id=f"advection_c{self.c}_n{int(noise_level*100)}",
            pde_name=self.name,
            x=grid.x,
            t=time_grid.t,
            u=U,
            channel_names=["u"],
            boundary_condition=self.boundary_condition,
            units={"u": "m/s", "x": "m", "t": "s"},
            u_clean=U_clean,
            u_t_true=U_t_true,
            true_parameters=self.parameters,
            noise_level=noise_level,
            provenance={
                "solver": "Fourier_Exact_Phase_Shift",
                "c": self.c,
                "domain": self.domain,
            },
        )
