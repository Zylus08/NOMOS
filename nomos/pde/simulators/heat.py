"""
NOMOS 1D Heat Equation Simulator
PDE: u_t = alpha * u_xx
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


class HeatEquationSimulator(BasePDESimulator):
    """
    Simulates the 1D Linear Heat / Diffusion Equation:
        u_t = alpha * u_xx
    Default: periodic domain [0, 2*pi] with alpha = 0.1.
    """

    def __init__(
        self,
        alpha: float = 0.1,
        domain: Tuple[float, float] = (0.0, 2.0 * np.pi),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="heat_equation",
            parameters={"alpha": float(alpha)},
            boundary_condition=boundary_condition,
            domain=domain,
        )
        self.alpha = float(alpha)

    def rhs_spatial(self, u: np.ndarray, x: np.ndarray) -> np.ndarray:
        """Compute alpha * u_xx using periodic Fourier differentiation."""
        N = len(u)
        L = self.domain[1] - self.domain[0]
        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)
        u_hat = fft(u)
        u_xx = np.real(ifft(-(k**2) * u_hat))
        return self.alpha * u_xx

    def analytical_solution(
        self, x: np.ndarray, t: float, u0_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> Optional[np.ndarray]:
        """
        Analytical solution for fundamental harmonic u0(x) = sin(k0 * x).
        u(x, t) = exp(-alpha * k0^2 * t) * sin(k0 * x).
        """
        k0 = 1.0
        return np.exp(-self.alpha * (k0**2) * t) * np.sin(k0 * x)

    def compute_invariant(self, u: np.ndarray, dx: float) -> float:
        """Total thermal mass integral: M = int u dx (strictly conserved under periodic BC)."""
        return float(np.sum(u) * dx)

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

        # Spatial frequencies k = (2*pi/L) * [0, 1, ..., N/2, -N/2+1, ..., -1]
        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)

        # Exact integrating factor in Fourier space: u_hat(t+dt) = exp(-alpha * k^2 * dt) * u_hat(t)
        decay = np.exp(-self.alpha * (k**2) * dt)

        U = np.zeros((M, N), dtype=np.float64)
        U_t_true = np.zeros((M, N), dtype=np.float64)
        u_current = np.asarray(u0, dtype=np.float64)
        u_hat = fft(u_current)

        for m in range(M):
            u_real = np.real(ifft(u_hat))
            U[m] = u_real
            # True derivative u_t = alpha * u_xx
            U_t_true[m] = np.real(ifft(-(k**2) * self.alpha * u_hat))
            u_hat = u_hat * decay

        U_clean = U.copy()
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed or 42)
            sigma = noise_level * np.std(U_clean)
            U = U_clean + rng.normal(0.0, sigma, size=U.shape)

        return SpatiotemporalField(
            id=f"heat_a{self.alpha}_n{int(noise_level*100)}",
            pde_name=self.name,
            x=grid.x,
            t=time_grid.t,
            u=U,
            channel_names=["u"],
            boundary_condition=self.boundary_condition,
            units={"u": "K", "x": "m", "t": "s"},
            u_clean=U_clean,
            u_t_true=U_t_true,
            true_parameters=self.parameters,
            noise_level=noise_level,
            provenance={
                "solver": "Fourier_Exact_Integrating_Factor",
                "alpha": self.alpha,
                "domain": self.domain,
            },
        )
