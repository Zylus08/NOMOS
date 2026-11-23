"""
NOMOS 1D Kuramoto–Sivashinsky (KS) Chaotic PDE Simulator
PDE: u_t + u * u_x + u_xx + u_xxxx = 0  ==>  u_t = -u * u_x - u_xx - u_xxxx
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


class KuramotoSivashinskySimulator(BasePDESimulator):
    """
    Simulates the 1D Kuramoto–Sivashinsky (KS) Equation:
        u_t = -u * u_x - u_xx - u_xxxx
    Models flame front instabilities, reaction-diffusion chaos, and fluid film waves.
    Solved via Exponential Time Differencing (ETD-RK4) or integrating factor RK4 on periodic grid.
    """

    def __init__(
        self,
        domain: Tuple[float, float] = (0.0, 32.0 * np.pi),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="kuramoto_sivashinsky",
            parameters={"nonlin_coeff": 1.0, "diff_coeff": 1.0, "hyperdiff_coeff": 1.0},
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
        # u_xx has Fourier symbol -k^2, so -u_xx has +k^2
        # u_xxxx has Fourier symbol k^4, so -u_xxxx has -k^4
        linear_symbol = (k**2) - (k**4)
        linear_part = np.real(ifft(linear_symbol * u_hat))

        # Nonlinear term: u * u_x = 1/2 * (u^2)_x
        u2_hat = fft(u**2) * mask
        u_nonlin = np.real(ifft(0.5 * 1j * k * u2_hat))

        return -u_nonlin + linear_part

    def compute_invariant(self, u: np.ndarray, dx: float) -> float:
        """Mean spatial field: M = int u dx (strictly conserved)."""
        return float(np.sum(u) * dx)

    def analytical_solution(
        self, x: np.ndarray, t: float, u0_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> Optional[np.ndarray]:
        # KS has no closed-form analytical solution due to spatiotemporal chaos
        return None

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

        # Linear dispersion relation: L_k = k^2 - k^4
        L_k = (k**2) - (k**4)

        # Integrating Factor method (ETD): let v = exp(-L*t) * u
        # dv/dt = exp(-L*t) * N(exp(L*t) * v)
        E = np.exp(L_k * dt)
        E_half = np.exp(L_k * (dt / 2.0))

        def nonlin_k(u_vec):
            # Returns Fourier transform of nonlinear term: -0.5 * d(u^2)/dx
            u2_hat = fft(u_vec**2) * mask
            return -0.5 * 1j * k * u2_hat

        U = np.zeros((M, N), dtype=np.float64)
        U_t_true = np.zeros((M, N), dtype=np.float64)
        u_curr = np.asarray(u0, dtype=np.float64).copy()

        for m in range(M):
            # Compute spatial RHS directly for ground-truth derivative
            u_hat_curr = fft(u_curr)
            lin_curr = np.real(ifft(L_k * u_hat_curr))
            nonlin_curr = np.real(ifft(nonlin_k(u_curr)))
            rhs_curr = nonlin_curr + lin_curr

            U[m] = u_curr
            U_t_true[m] = rhs_curr

            # 4th-order Integrating Factor Runge-Kutta
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
            id=f"ks_chaotic_n{int(noise_level*100)}",
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
                "solver": "Integrating_Factor_PseudoSpectral_RK4",
                "domain": self.domain,
            },
        )
