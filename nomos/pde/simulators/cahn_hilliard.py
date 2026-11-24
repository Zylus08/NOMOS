"""
NOMOS Cahn–Hilliard Phase Separation PDE Simulator (1D and 2D)
PDE:
    u_t = gamma * lap(u^3 - u - epsilon^2 * lap(u))
        = gamma * lap(u^3) - gamma * lap(u) - gamma * epsilon^2 * lap^2(u)

Canonical physical model of spinodal decomposition, phase separation in binary alloys/fluids,
and interfacial mass-conserving pattern formation (4th-order nonlinear parabolic PDE).
"""

from typing import Dict, Optional, Tuple, Callable
import numpy as np
from scipy.fft import fft, ifft, fftfreq, fft2, ifft2

from nomos.pde.schema import (
    BoundaryConditionType,
    Grid1D,
    Grid2D,
    TimeGrid,
    SpatiotemporalField,
)
from nomos.pde.simulators.base import BasePDESimulator, BasePDE2DSimulator


class CahnHilliard1DSimulator(BasePDESimulator):
    """
    1D Cahn–Hilliard equation simulator:
        u_t = gamma * (u^3 - u - epsilon^2 * u_xx)_xx
    Solved via pseudo-spectral Integrating Factor Runge–Kutta 4 (IF-RK4).
    """

    def __init__(
        self,
        gamma: float = 1.0,
        epsilon: float = 0.05,
        domain: Tuple[float, float] = (0.0, 2.0 * np.pi),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="cahn_hilliard",
            parameters={"gamma": float(gamma), "epsilon": float(epsilon)},
            boundary_condition=boundary_condition,
            domain=domain,
        )
        self.gamma = float(gamma)
        self.epsilon = float(epsilon)

    def rhs_spatial(self, u: np.ndarray, x: np.ndarray) -> np.ndarray:
        """Compute true spatial RHS u_t."""
        N = len(u)
        L = self.domain[1] - self.domain[0]
        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)

        # Dealiasing mask (2/3 rule)
        k_max = np.max(np.abs(k))
        mask = np.abs(k) <= (2.0 / 3.0) * k_max

        # Linear symbol: L_k = gamma * k^2 - gamma * epsilon^2 * k^4
        L_k = self.gamma * (k**2) - self.gamma * (self.epsilon**2) * (k**4)
        linear_part = np.real(ifft(L_k * fft(u)))

        # Nonlinear part: gamma * (u^3)_xx -> -gamma * k^2 * FFT(u^3)
        u3_hat = fft(u**3) * mask
        nonlin_part = np.real(ifft(-self.gamma * (k**2) * u3_hat))

        return linear_part + nonlin_part

    def compute_invariant(self, u: np.ndarray, dx: float) -> float:
        """Total mass M = int u dx is strictly conserved."""
        return float(np.sum(u) * dx)

    def compute_free_energy(self, u: np.ndarray, dx: float) -> float:
        """Ginzburg-Landau free energy: F = int [ 1/4 (u^2 - 1)^2 + 1/2 eps^2 (u_x)^2 ] dx."""
        N = len(u)
        L = self.domain[1] - self.domain[0]
        k = (2.0 * np.pi / L) * fftfreq(N, 1.0 / N)
        u_x = np.real(ifft(1j * k * fft(u)))
        f_bulk = 0.25 * ((u**2 - 1.0) ** 2)
        f_grad = 0.5 * (self.epsilon**2) * (u_x**2)
        return float(np.sum(f_bulk + f_grad) * dx)

    def analytical_solution(
        self, x: np.ndarray, t: float, u0_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> Optional[np.ndarray]:
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

        # Sub-stepping for unconditional stability
        dt_max = 0.0008
        n_sub = max(1, int(np.ceil(dt / dt_max)))
        h = dt / n_sub

        # Linear dispersion operator: L_k = gamma * k^2 - gamma * epsilon^2 * k^4
        L_k = self.gamma * (k**2) - self.gamma * (self.epsilon**2) * (k**4)

        # Integrating factors for sub-step h
        E = np.exp(L_k * h)
        E_half = np.exp(L_k * (h / 2.0))

        def nonlin_k(u_arr: np.ndarray) -> np.ndarray:
            # -gamma * k^2 * FFT(u^3)
            u3_hat = fft(u_arr**3) * mask
            return -self.gamma * (k**2) * u3_hat

        U = np.zeros((M, N), dtype=np.float64)
        U_t_true = np.zeros((M, N), dtype=np.float64)

        u_curr = np.copy(u0)
        U[0, :] = u_curr
        U_t_true[0, :] = self.rhs_spatial(u_curr, grid.x)

        for m in range(1, M):
            for _ in range(n_sub):
                u_hat = fft(u_curr)

                # Stage 1
                k1 = nonlin_k(u_curr)

                # Stage 2
                u2_hat = E_half * (u_hat + 0.5 * h * k1)
                u2 = np.real(ifft(u2_hat))
                k2 = nonlin_k(u2)

                # Stage 3
                u3_hat = E_half * u_hat + 0.5 * h * k2
                u3 = np.real(ifft(u3_hat))
                k3 = nonlin_k(u3)

                # Stage 4
                u4_hat = E * u_hat + h * E_half * k3
                u4 = np.real(ifft(u4_hat))
                k4 = nonlin_k(u4)

                # Assembly
                u_next_hat = E * u_hat + (h / 6.0) * (E * k1 + 2.0 * E_half * k2 + 2.0 * E_half * k3 + k4)
                u_curr = np.real(ifft(u_next_hat))

            U[m, :] = u_curr
            U_t_true[m, :] = self.rhs_spatial(u_curr, grid.x)

        # Noise contamination
        U_noisy = np.copy(U)
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed)
            scale = np.std(U)
            if scale < 1e-12:
                scale = 1.0
            U_noisy += rng.normal(0.0, noise_level * scale, size=U.shape)

        return SpatiotemporalField(
            id=f"cahn_hilliard_{random_seed}",
            pde_name=self.name,
            x=grid.x,
            t=time_grid.t,
            u=U_noisy,
            channel_names=["u"],
            boundary_condition=self.boundary_condition,
            spatial_dim=1,
            noise_level=noise_level,
            u_clean=U,
            u_t_true=U_t_true,
            true_parameters=self.parameters.copy(),
            provenance={"simulator": "CahnHilliard1DSimulator", "method": "IF-RK4"},
        )


class CahnHilliard2DSimulator(BasePDE2DSimulator):
    """
    2D Cahn–Hilliard equation simulator:
        u_t = gamma * lap(u^3 - u - epsilon^2 * lap(u))
    Solves 2D spinodal decomposition and bicontinuous coarsening patterns.
    """

    def __init__(
        self,
        gamma: float = 1.0,
        epsilon: float = 0.08,
        domain_x: Tuple[float, float] = (0.0, 2.0 * np.pi),
        domain_y: Tuple[float, float] = (0.0, 2.0 * np.pi),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="cahn_hilliard_2d",
            parameters={"gamma": float(gamma), "epsilon": float(epsilon)},
            boundary_condition=boundary_condition,
            domain_x=domain_x,
            domain_y=domain_y,
        )
        self.gamma = float(gamma)
        self.epsilon = float(epsilon)

    def rhs_spatial(self, u: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Compute true spatial RHS u_t. u shape: (Nx, Ny)."""
        Nx, Ny = u.shape[:2]
        u_field = u[..., 0] if u.ndim == 3 else u

        Lx = self.domain_x[1] - self.domain_x[0]
        Ly = self.domain_y[1] - self.domain_y[0]

        kx = (2.0 * np.pi / Lx) * fftfreq(Nx, 1.0 / Nx)
        ky = (2.0 * np.pi / Ly) * fftfreq(Ny, 1.0 / Ny)
        KX, KY = np.meshgrid(kx, ky, indexing="ij")
        K2 = KX**2 + KY**2

        # 2/3 mask
        mask = (np.abs(KX) <= (2.0 / 3.0) * np.max(np.abs(kx))) & (np.abs(KY) <= (2.0 / 3.0) * np.max(np.abs(ky)))

        # Linear symbol: gamma * K2 - gamma * epsilon^2 * K4
        L_K = self.gamma * K2 - self.gamma * (self.epsilon**2) * (K2**2)
        linear_part = np.real(ifft2(L_K * fft2(u_field)))

        # Nonlinear part: -gamma * K2 * FFT(u^3)
        u3_hat = fft2(u_field**3) * mask
        nonlin_part = np.real(ifft2(-self.gamma * K2 * u3_hat))

        res = linear_part + nonlin_part
        if u.ndim == 3:
            return res[..., None]
        return res

    def simulate(
        self,
        u0: np.ndarray,
        grid: Grid2D,
        time_grid: TimeGrid,
        noise_level: float = 0.0,
        random_seed: Optional[int] = None,
    ) -> SpatiotemporalField:
        Nx = grid.num_points_x
        Ny = grid.num_points_y
        Nt = time_grid.num_steps
        dt = time_grid.dt

        Lx = self.domain_x[1] - self.domain_x[0]
        Ly = self.domain_y[1] - self.domain_y[0]

        kx = (2.0 * np.pi / Lx) * fftfreq(Nx, 1.0 / Nx)
        ky = (2.0 * np.pi / Ly) * fftfreq(Ny, 1.0 / Ny)
        KX, KY = np.meshgrid(kx, ky, indexing="ij")
        K2 = KX**2 + KY**2

        mask = (np.abs(KX) <= (2.0 / 3.0) * np.max(np.abs(kx))) & (np.abs(KY) <= (2.0 / 3.0) * np.max(np.abs(ky)))
        L_K = self.gamma * K2 - self.gamma * (self.epsilon**2) * (K2**2)

        dt_max = 0.0005
        n_sub = max(1, int(np.ceil(dt / dt_max)))
        h = dt / n_sub

        E = np.exp(L_K * h)
        E_half = np.exp(L_K * (h / 2.0))

        def nonlin_k(u_arr: np.ndarray) -> np.ndarray:
            u3_hat = fft2(u_arr**3) * mask
            return -self.gamma * K2 * u3_hat

        U = np.zeros((Nt, Nx, Ny), dtype=np.float64)
        U_t_true = np.zeros((Nt, Nx, Ny), dtype=np.float64)

        u_curr = np.copy(u0[..., 0] if u0.ndim == 3 else u0)
        U[0, :, :] = u_curr
        U_t_true[0, :, :] = self.rhs_spatial(u_curr, grid.x, grid.y)

        for m in range(1, Nt):
            for _ in range(n_sub):
                u_hat = fft2(u_curr)

                k1 = nonlin_k(u_curr)
                u2 = np.real(ifft2(E_half * (u_hat + 0.5 * h * k1)))
                k2 = nonlin_k(u2)
                u3 = np.real(ifft2(E_half * u_hat + 0.5 * h * k2))
                k3 = nonlin_k(u3)
                u4 = np.real(ifft2(E * u_hat + h * E_half * k3))
                k4 = nonlin_k(u4)

                u_next_hat = E * u_hat + (h / 6.0) * (E * k1 + 2.0 * E_half * k2 + 2.0 * E_half * k3 + k4)
                u_curr = np.real(ifft2(u_next_hat))

            U[m, :, :] = u_curr
            U_t_true[m, :, :] = self.rhs_spatial(u_curr, grid.x, grid.y)

        U_out = U[..., None]
        U_t_out = U_t_true[..., None]
        U_noisy = np.copy(U_out)

        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed)
            scale = np.std(U_out)
            if scale < 1e-12:
                scale = 1.0
            U_noisy += rng.normal(0.0, noise_level * scale, size=U_out.shape)

        return SpatiotemporalField(
            id=f"cahn_hilliard_2d_{random_seed}",
            pde_name=self.name,
            x=grid.x,
            y=grid.y,
            t=time_grid.t,
            u=U_noisy,
            channel_names=["u"],
            boundary_condition=self.boundary_condition,
            spatial_dim=2,
            noise_level=noise_level,
            u_clean=U_out,
            u_t_true=U_t_out,
            true_parameters=self.parameters.copy(),
            provenance={"simulator": "CahnHilliard2DSimulator", "method": "IF-RK4"},
        )
