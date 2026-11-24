"""
NOMOS 2D Coupled Brusselator Reaction–Diffusion Simulator
PDE:
    u_t = D_u * (u_xx + u_yy) + A - (B + 1) * u + u^2 * v
    v_t = D_v * (v_xx + v_yy) + B * u - u^2 * v
Canonical model of autocatalytic chemical morphogenesis and Turing limit cycles.
"""

from typing import Dict, Optional, Tuple, Callable
import numpy as np
from scipy.fft import fft2, ifft2, fftfreq

from nomos.pde.schema import (
    BoundaryConditionType,
    Grid2D,
    TimeGrid,
    SpatiotemporalField,
)
from nomos.pde.simulators.base import BasePDE2DSimulator


class Brusselator2DSimulator(BasePDE2DSimulator):
    """
    High-precision pseudo-spectral simulator for the 2D Brusselator model.
    Solves stiff diffusion via Integrating-Factor Runge-Kutta 4 (IF-RK4).
    """

    def __init__(
        self,
        D_u: float = 0.1,
        D_v: float = 0.05,
        A: float = 1.0,
        B: float = 3.0,
        domain_x: Tuple[float, float] = (0.0, 2.0 * np.pi),
        domain_y: Tuple[float, float] = (0.0, 2.0 * np.pi),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="brusselator_2d",
            parameters={"D_u": float(D_u), "D_v": float(D_v), "A": float(A), "B": float(B)},
            boundary_condition=boundary_condition,
            domain_x=domain_x,
            domain_y=domain_y,
        )
        self.D_u = float(D_u)
        self.D_v = float(D_v)
        self.A = float(A)
        self.B = float(B)

    def rhs_spatial(self, uv: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Compute true continuous spatial RHS [u_t, v_t].
        uv shape: (Nx, Ny, 2).
        """
        Nx, Ny, _ = uv.shape
        Lx = self.domain_x[1] - self.domain_x[0]
        Ly = self.domain_y[1] - self.domain_y[0]

        kx = (2.0 * np.pi / Lx) * fftfreq(Nx, 1.0 / Nx)
        ky = (2.0 * np.pi / Ly) * fftfreq(Ny, 1.0 / Ny)
        KX, KY = np.meshgrid(kx, ky, indexing="ij")
        K2 = KX**2 + KY**2

        u = uv[..., 0]
        v = uv[..., 1]

        lap_u = np.real(ifft2(-K2 * fft2(u)))
        lap_v = np.real(ifft2(-K2 * fft2(v)))

        u2v = (u**2) * v
        du_dt = self.D_u * lap_u + self.A - (self.B + 1.0) * u + u2v
        dv_dt = self.D_v * lap_v + self.B * u - u2v

        return np.stack([du_dt, dv_dt], axis=-1)

    def simulate(
        self,
        u0: np.ndarray,
        grid: Grid2D,
        time_grid: TimeGrid,
        noise_level: float = 0.0,
        random_seed: Optional[int] = None,
    ) -> SpatiotemporalField:
        """
        Simulate 2D Brusselator using Integrating-Factor RK4.
        """
        Nx = grid.num_points_x
        Ny = grid.num_points_y
        Nt = time_grid.num_steps
        t = time_grid.t
        dt = time_grid.dt

        Lx = self.domain_x[1] - self.domain_x[0]
        Ly = self.domain_y[1] - self.domain_y[0]

        kx = (2.0 * np.pi / Lx) * fftfreq(Nx, 1.0 / Nx)
        ky = (2.0 * np.pi / Ly) * fftfreq(Ny, 1.0 / Ny)
        KX, KY = np.meshgrid(kx, ky, indexing="ij")
        K2 = KX**2 + KY**2

        E_u_half = np.exp(-self.D_u * K2 * (dt / 2.0))
        E_u_full = np.exp(-self.D_u * K2 * dt)
        E_v_half = np.exp(-self.D_v * K2 * (dt / 2.0))
        E_v_full = np.exp(-self.D_v * K2 * dt)

        def nonlinear_rhs(uv_state: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
            u_s = uv_state[..., 0]
            v_s = uv_state[..., 1]
            u2v = (u_s**2) * v_s
            nu = self.A - (self.B + 1.0) * u_s + u2v
            nv = self.B * u_s - u2v
            return nu, nv

        trajectory = np.zeros((Nt, Nx, Ny, 2), dtype=np.float64)
        trajectory[0] = u0.copy()

        curr_uv = u0.copy()

        for n in range(Nt - 1):
            u_curr = curr_uv[..., 0]
            v_curr = curr_uv[..., 1]

            u_hat = fft2(u_curr)
            v_hat = fft2(v_curr)

            # Stage 1
            N_u_1, N_v_1 = nonlinear_rhs(curr_uv)
            N_u_1_hat = fft2(N_u_1)
            N_v_1_hat = fft2(N_v_1)

            # Stage 2
            u_hat_2 = E_u_half * u_hat + (dt / 2.0) * E_u_half * N_u_1_hat
            v_hat_2 = E_v_half * v_hat + (dt / 2.0) * E_v_half * N_v_1_hat
            uv_2 = np.stack([np.real(ifft2(u_hat_2)), np.real(ifft2(v_hat_2))], axis=-1)
            N_u_2, N_v_2 = nonlinear_rhs(uv_2)
            N_u_2_hat = fft2(N_u_2)
            N_v_2_hat = fft2(N_v_2)

            # Stage 3
            u_hat_3 = E_u_half * u_hat + (dt / 2.0) * N_u_2_hat
            v_hat_3 = E_v_half * v_hat + (dt / 2.0) * N_v_2_hat
            uv_3 = np.stack([np.real(ifft2(u_hat_3)), np.real(ifft2(v_hat_3))], axis=-1)
            N_u_3, N_v_3 = nonlinear_rhs(uv_3)
            N_u_3_hat = fft2(N_u_3)
            N_v_3_hat = fft2(N_v_3)

            # Stage 4
            u_hat_4 = E_u_full * u_hat + dt * E_u_half * N_u_3_hat
            v_hat_4 = E_v_full * v_hat + dt * E_v_half * N_v_3_hat
            uv_4 = np.stack([np.real(ifft2(u_hat_4)), np.real(ifft2(v_hat_4))], axis=-1)
            N_u_4, N_v_4 = nonlinear_rhs(uv_4)
            N_u_4_hat = fft2(N_u_4)
            N_v_4_hat = fft2(N_v_4)

            # Combine IF-RK4
            u_hat_next = E_u_full * u_hat + (dt / 6.0) * (
                E_u_full * N_u_1_hat + 2.0 * E_u_half * (N_u_2_hat + N_u_3_hat) + N_u_4_hat
            )
            v_hat_next = E_v_full * v_hat + (dt / 6.0) * (
                E_v_full * N_v_1_hat + 2.0 * E_v_half * (N_v_2_hat + N_v_3_hat) + N_v_4_hat
            )

            curr_uv = np.stack([np.real(ifft2(u_hat_next)), np.real(ifft2(v_hat_next))], axis=-1)
            trajectory[n + 1] = curr_uv

        # Add noise if requested
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed)
            std_u = np.std(trajectory[..., 0])
            std_v = np.std(trajectory[..., 1])
            noise_u = rng.normal(0.0, noise_level * std_u, trajectory[..., 0].shape)
            noise_v = rng.normal(0.0, noise_level * std_v, trajectory[..., 1].shape)
            trajectory_noisy = trajectory.copy()
            trajectory_noisy[..., 0] += noise_u
            trajectory_noisy[..., 1] += noise_v
        else:
            trajectory_noisy = trajectory.copy()

        return SpatiotemporalField(
            id=f"brusselator_2d_{random_seed}",
            pde_name=self.name,
            x=grid.x,
            y=grid.y,
            t=t,
            u=trajectory_noisy,
            channel_names=["u", "v"],
            boundary_condition=self.boundary_condition,
            spatial_dim=2,
            units={"u": "mol/m^2", "v": "mol/m^2", "x": "m", "y": "m", "t": "s"},
            noise_level=noise_level,
            provenance={"simulator": "Brusselator2DSimulator", "method": "IF-RK4"},
        )

    def default_initial_condition(self, grid: Grid2D) -> np.ndarray:
        """Steady-state background with localized central perturbation."""
        X, Y = grid.meshgrid
        # Steady state: u_ss = A, v_ss = B / A
        u_ss = self.A
        v_ss = self.B / self.A
        u0 = np.full((grid.num_points_x, grid.num_points_y), u_ss, dtype=np.float64)
        v0 = np.full((grid.num_points_x, grid.num_points_y), v_ss, dtype=np.float64)

        # Perturbation
        r2 = (X - np.pi)**2 + (Y - np.pi)**2
        pert = np.exp(-r2 / 0.5)
        u0 += 0.5 * pert
        v0 -= 0.5 * pert
        return np.stack([u0, v0], axis=-1)
