"""
NOMOS 1D Korteweg–de Vries (KdV) Equation Simulator
PDE: u_t + 6 * u * u_x + u_xxx = 0  ==>  u_t = -6 * u * u_x - u_xxx
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


class KdVSimulator(BasePDESimulator):
    """
    Simulates the 1D Korteweg–de Vries (KdV) Equation:
        u_t = -6 * u * u_x - u_xxx
    Features solitary wave (soliton) solutions and infinite conserved invariants.
    De-aliased pseudo-spectral RK4 integration.
    """

    def __init__(
        self,
        domain: Tuple[float, float] = (-10.0, 10.0),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="kdv_equation",
            parameters={"nonlin_coeff": 6.0, "disp_coeff": 1.0},
            boundary_condition=boundary_condition,
            domain=domain,
        )

    def rhs_spatial(self, u: np.ndarray, x: np.ndarray) -> np.ndarray:
        N = len(u)
        L = self.domain[1] - self.domain[0]
        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)

        k_max = np.max(np.abs(k))
        mask = np.abs(k) <= (2.0 / 3.0) * k_max

        u_hat = fft(u)
        # u_xxx = ifft(-i * k^3 * u_hat)
        u_xxx = np.real(ifft(-1j * (k**3) * u_hat))

        # Nonlinear term: (u^2)_x = 2 * u * u_x
        # 6 * u * u_x = 3 * (u^2)_x
        u2_hat = fft(u**2) * mask
        u_nonlin = np.real(ifft(3.0 * 1j * k * u2_hat))

        return -u_nonlin - u_xxx

    def compute_invariant(self, u: np.ndarray, dx: float) -> float:
        """KdV mass invariant: M = int u dx."""
        return float(np.sum(u) * dx)

    def compute_momentum(self, u: np.ndarray, dx: float) -> float:
        """KdV momentum invariant: P = 1/2 * int u^2 dx."""
        return float(0.5 * np.sum(u**2) * dx)

    def analytical_1soliton(self, x: np.ndarray, t: float, c: float = 2.0, x0: float = 0.0) -> np.ndarray:
        """
        Analytical 1-soliton solution:
        u(x, t) = 0.5 * c * sech^2( 0.5 * sqrt(c) * (x - c*t - x0) )
        """
        xi = 0.5 * np.sqrt(c) * (x - c * t - x0)
        return 0.5 * c * (1.0 / np.cosh(xi))**2

    def analytical_solution(
        self, x: np.ndarray, t: float, u0_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> Optional[np.ndarray]:
        return self.analytical_1soliton(x, t)

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

        # Dispersive linear operator in Fourier space: L = +i * k^3
        L_k = 1j * (k**3)
        E = np.exp(L_k * dt)
        E_half = np.exp(L_k * (dt / 2.0))

        def nonlin_k(u_vec):
            u2_hat = fft(u_vec**2) * mask
            return -3.0 * 1j * k * u2_hat

        U = np.zeros((M, N), dtype=np.float64)
        U_t_true = np.zeros((M, N), dtype=np.float64)
        u_curr = np.asarray(u0, dtype=np.float64).copy()

        for m in range(M):
            u_hat_curr = fft(u_curr)
            # Compute true spatial RHS for evaluator: -6*u*u_x - u_xxx
            u_xxx_real = np.real(ifft(L_k * u_hat_curr))
            u_nonlin_real = np.real(ifft(nonlin_k(u_curr)))
            U[m] = u_curr
            U_t_true[m] = u_nonlin_real + u_xxx_real

            # 4th-order Integrating Factor Runge-Kutta step
            Na = nonlin_k(u_curr)
            a = np.real(ifft(E_half * (u_hat_curr + 0.5 * dt * Na)))

            Nb = nonlin_k(a)
            b = np.real(ifft(E_half * u_hat_curr + 0.5 * dt * Nb))

            Nc = nonlin_k(b)
            c = np.real(ifft(E * u_hat_curr + dt * E_half * Nc))

            Nd = nonlin_k(c)

            u_hat_next = E * u_hat_curr + (dt / 6.0) * (E * Na + 2.0 * E_half * (Nb + Nc) + Nd)
            u_curr = np.real(ifft(u_hat_next))

        U_clean = U.copy()
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed or 42)
            sigma = noise_level * np.std(U_clean)
            U = U_clean + rng.normal(0.0, sigma, size=U.shape)

        return SpatiotemporalField(
            id=f"kdv_soliton_n{int(noise_level*100)}",
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
                "domain": self.domain,
            },
        )
