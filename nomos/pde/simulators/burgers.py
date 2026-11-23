"""
NOMOS 1D Viscous Burgers' Equation Simulator
PDE: u_t + u * u_x = nu * u_xx  ==>  u_t = -u * u_x + nu * u_xx
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


class BurgersSimulator(BasePDESimulator):
    """
    Simulates the 1D Viscous Burgers' Equation:
        u_t = -u * u_x + nu * u_xx
    High-precision pseudo-spectral method with Orszag 2/3 de-aliasing and RK4 time stepping.
    """

    def __init__(
        self,
        nu: float = 0.05,
        domain: Tuple[float, float] = (0.0, 2.0 * np.pi),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="viscous_burgers",
            parameters={"nu": float(nu)},
            boundary_condition=boundary_condition,
            domain=domain,
        )
        self.nu = float(nu)

    def rhs_spatial(self, u: np.ndarray, x: np.ndarray) -> np.ndarray:
        N = len(u)
        L = self.domain[1] - self.domain[0]
        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)

        # De-aliasing mask: 2/3 rule
        k_max = np.max(np.abs(k))
        mask = np.abs(k) <= (2.0 / 3.0) * k_max

        u_hat = fft(u)
        u_x = np.real(ifft(1j * k * u_hat))
        u_xx = np.real(ifft(-(k**2) * u_hat))

        # Nonlinear term with de-aliasing
        adv_hat = fft(u * u_x) * mask
        u_adv = np.real(ifft(adv_hat))

        return -u_adv + self.nu * u_xx

    def compute_invariant(self, u: np.ndarray, dx: float) -> float:
        """Total mass M = int u dx is conserved under periodic boundary conditions."""
        return float(np.sum(u) * dx)

    def analytical_solution(
        self, x: np.ndarray, t: float, u0_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> Optional[np.ndarray]:
        # Burgers travelling wave analytical solution: u(x, t) = c * (1 - tanh(c*(x - c*t)/(2*nu)))
        c = 1.0
        return 0.5 * c * (1.0 - np.tanh(c * (x - 0.5 * c * t - np.pi) / (4.0 * self.nu)))

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
        k_max = np.max(np.abs(k))
        mask = np.abs(k) <= (2.0 / 3.0) * k_max

        def compute_rhs(u_vec):
            u_hat_local = fft(u_vec)
            u_x_local = np.real(ifft(1j * k * u_hat_local))
            u_xx_local = np.real(ifft(-(k**2) * u_hat_local))
            adv_hat_local = fft(u_vec * u_x_local) * mask
            u_adv_local = np.real(ifft(adv_hat_local))
            return -u_adv_local + self.nu * u_xx_local

        U = np.zeros((M, N), dtype=np.float64)
        U_t_true = np.zeros((M, N), dtype=np.float64)

        u_curr = np.asarray(u0, dtype=np.float64).copy()

        for m in range(M):
            rhs_curr = compute_rhs(u_curr)
            U[m] = u_curr
            U_t_true[m] = rhs_curr

            # 4th-order Runge-Kutta step
            k1 = rhs_curr
            k2 = compute_rhs(u_curr + 0.5 * dt * k1)
            k3 = compute_rhs(u_curr + 0.5 * dt * k2)
            k4 = compute_rhs(u_curr + dt * k3)

            u_curr = u_curr + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

        U_clean = U.copy()
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed or 42)
            sigma = noise_level * np.std(U_clean)
            U = U_clean + rng.normal(0.0, sigma, size=U.shape)

        return SpatiotemporalField(
            id=f"burgers_nu{self.nu}_n{int(noise_level*100)}",
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
                "solver": "Dealiased_PseudoSpectral_RK4",
                "nu": self.nu,
                "domain": self.domain,
            },
        )
