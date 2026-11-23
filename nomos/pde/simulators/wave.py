"""
NOMOS 1D Wave Equation Simulator
PDE: u_tt = c^2 * u_xx
Formulated as first-order Hamiltonian system:
    u_t = v
    v_t = c^2 * u_xx
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


class WaveEquationSimulator(BasePDESimulator):
    """
    Simulates the 1D Hyperbolic Wave Equation:
        u_tt = c^2 * u_xx
    Implemented in first-order state space:
        u_t = v
        v_t = c^2 * u_xx
    Conserves total energy: E = 1/2 * int (v^2 + c^2 * u_x^2) dx.
    """

    def __init__(
        self,
        c: float = 1.0,
        domain: Tuple[float, float] = (0.0, 2.0 * np.pi),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="wave_equation",
            parameters={"c": float(c)},
            boundary_condition=boundary_condition,
            domain=domain,
        )
        self.c = float(c)

    def rhs_spatial(self, state: np.ndarray, x: np.ndarray) -> np.ndarray:
        """
        Input state shape: (N, 2) where col 0 is u, col 1 is v.
        Output shape: (N, 2) representing [u_t, v_t] = [v, c^2 * u_xx].
        """
        u = state[:, 0]
        v = state[:, 1]
        N = len(u)
        L = self.domain[1] - self.domain[0]
        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)

        u_hat = fft(u)
        u_xx = np.real(ifft(-(k**2) * u_hat))

        out = np.zeros_like(state)
        out[:, 0] = v
        out[:, 1] = (self.c**2) * u_xx
        return out

    def compute_energy(self, u: np.ndarray, v: np.ndarray, dx: float) -> float:
        """Total Hamiltonian wave energy: E = 1/2 * int (v^2 + c^2 * u_x^2) dx."""
        N = len(u)
        L = self.domain[1] - self.domain[0]
        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)
        u_x = np.real(ifft(1j * k * fft(u)))
        e_density = 0.5 * (v**2 + (self.c**2) * (u_x**2))
        return float(np.sum(e_density) * dx)

    def analytical_solution(
        self, x: np.ndarray, t: float, u0_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> Optional[np.ndarray]:
        """
        d'Alembert solution for standing/travelling wave with zero initial velocity:
        u(x, t) = 1/2 * [u0(x - c*t) + u0(x + c*t)].
        For u0(x) = sin(x): u(x, t) = sin(x) * cos(c*t).
        """
        return np.sin(x) * np.cos(self.c * t)

    def simulate(
        self,
        u0: np.ndarray,
        grid: Grid1D,
        time_grid: TimeGrid,
        v0: Optional[np.ndarray] = None,
        noise_level: float = 0.0,
        random_seed: Optional[int] = None,
    ) -> SpatiotemporalField:
        N = grid.num_points
        M = time_grid.num_steps
        L = self.domain[1] - self.domain[0]
        dt = time_grid.dt

        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)
        omega = self.c * np.abs(k)

        # Exact harmonic oscillator solution for each Fourier mode in periodic domain:
        # u_hat_k(t) = u_hat_k(0) * cos(omega_k * t) + (v_hat_k(0) / omega_k) * sin(omega_k * t)
        # v_hat_k(t) = -u_hat_k(0) * omega_k * sin(omega_k * t) + v_hat_k(0) * cos(omega_k * t)
        u_init = np.asarray(u0, dtype=np.float64)
        v_init = np.zeros(N, dtype=np.float64) if v0 is None else np.asarray(v0, dtype=np.float64)

        u_hat_0 = fft(u_init)
        v_hat_0 = fft(v_init)

        U = np.zeros((M, N), dtype=np.float64)
        V = np.zeros((M, N), dtype=np.float64)
        U_t_true = np.zeros((M, N), dtype=np.float64)

        for m, t_m in enumerate(time_grid.t):
            cos_wt = np.cos(omega * t_m)
            sin_wt = np.sin(omega * t_m)
            # Handle k=0 (omega=0) limit safely
            sinc_wt = np.zeros_like(omega)
            sinc_wt[0] = t_m
            sinc_wt[1:] = sin_wt[1:] / omega[1:]

            u_hat_t = u_hat_0 * cos_wt + v_hat_0 * sinc_wt
            v_hat_t = -u_hat_0 * omega * sin_wt + v_hat_0 * cos_wt

            u_real = np.real(ifft(u_hat_t))
            v_real = np.real(ifft(v_hat_t))

            U[m] = u_real
            V[m] = v_real
            U_t_true[m] = v_real

        U_clean = U.copy()
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed or 42)
            sigma = noise_level * np.std(U_clean)
            U = U_clean + rng.normal(0.0, sigma, size=U.shape)

        return SpatiotemporalField(
            id=f"wave_c{self.c}_n{int(noise_level*100)}",
            pde_name=self.name,
            x=grid.x,
            t=time_grid.t,
            u=U,
            channel_names=["u"],
            boundary_condition=self.boundary_condition,
            units={"u": "m", "x": "m", "t": "s"},
            u_clean=U_clean,
            u_t_true=U_t_true,
            true_parameters=self.parameters,
            noise_level=noise_level,
            provenance={
                "solver": "Fourier_Exact_Modal_Harmonic",
                "c": self.c,
                "domain": self.domain,
                "velocity_v": V,
            },
        )
