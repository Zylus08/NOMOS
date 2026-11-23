"""
NOMOS 2D Coupled FitzHugh–Nagumo Excitable Medium Simulator
PDE:
    u_t = D_u * (u_xx + u_yy) + u - u^3 - v
    v_t = D_v * (v_xx + v_yy) + eps * (u - a1 * v - a0)
Models electrical wave propagation in cardiac tissue, neuronal axons, and spiral wave turbulence.
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


class FitzHughNagumoSimulator(BasePDE2DSimulator):
    """
    High-precision pseudo-spectral simulator for the 2D FitzHugh–Nagumo excitable medium.
    Solves diffusion via Integrating-Factor Runge-Kutta 4 (IF-RK4).
    """

    def __init__(
        self,
        D_u: float = 1.0,
        D_v: float = 0.0,
        eps: float = 0.05,
        a1: float = 0.5,
        a0: float = 0.0,
        domain_x: Tuple[float, float] = (-10.0, 10.0),
        domain_y: Tuple[float, float] = (-10.0, 10.0),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="fitzhugh_nagumo_2d",
            parameters={
                "D_u": float(D_u),
                "D_v": float(D_v),
                "eps": float(eps),
                "a1": float(a1),
                "a0": float(a0),
            },
            boundary_condition=boundary_condition,
            domain_x=domain_x,
            domain_y=domain_y,
        )
        self.D_u = float(D_u)
        self.D_v = float(D_v)
        self.eps = float(eps)
        self.a1 = float(a1)
        self.a0 = float(a0)

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

        du_dt = self.D_u * lap_u + u - (u**3) - v
        dv_dt = self.D_v * lap_v + self.eps * (u - self.a1 * v - self.a0)

        return np.stack([du_dt, dv_dt], axis=-1)

    def default_initial_condition(self, grid: Grid2D) -> np.ndarray:
        """
        Broken-wavefront initial condition producing spiral wave re-entry:
        u is a front across x=0 for y>0, v is a gradient along y.
        """
        X, Y = grid.meshgrid
        u = np.where((X > -2.0) & (X < 2.0) & (Y > 0.0), 1.0, -1.0)
        v = np.where(Y > 0.0, 0.5, -0.5)
        return np.stack([u, v], axis=-1)

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
        M = time_grid.num_steps
        dt = time_grid.dt

        Lx = self.domain_x[1] - self.domain_x[0]
        Ly = self.domain_y[1] - self.domain_y[0]

        kx = (2.0 * np.pi / Lx) * fftfreq(Nx, 1.0 / Nx)
        ky = (2.0 * np.pi / Ly) * fftfreq(Ny, 1.0 / Ny)
        KX, KY = np.meshgrid(kx, ky, indexing="ij")
        K2 = KX**2 + KY**2

        # Integrating Factor operators
        Lu = -self.D_u * K2
        Lv = -self.D_v * K2

        Eu = np.exp(Lu * dt)
        Eu_half = np.exp(Lu * (0.5 * dt))
        Ev = np.exp(Lv * dt)
        Ev_half = np.exp(Lv * (0.5 * dt))

        def kinetics(u_val, v_val):
            ru = u_val - (u_val**3) - v_val
            rv = self.eps * (u_val - self.a1 * v_val - self.a0)
            return ru, rv

        UV_clean = np.zeros((M, Nx, Ny, 2), dtype=np.float64)
        UV_t_true = np.zeros((M, Nx, Ny, 2), dtype=np.float64)

        current_uv = np.array(u0, dtype=np.float64, copy=True)
        if current_uv.shape != (Nx, Ny, 2):
            raise ValueError(f"u0 shape must be ({Nx}, {Ny}, 2), got {current_uv.shape}")

        UV_clean[0] = current_uv
        UV_t_true[0] = self.rhs_spatial(current_uv, grid.x, grid.y)

        # IF-RK4 Integration
        for step in range(1, M):
            u = current_uv[..., 0]
            v = current_uv[..., 1]

            u_hat = fft2(u)
            v_hat = fft2(v)

            # k1
            ru1, rv1 = kinetics(u, v)
            k1_u = fft2(ru1)
            k1_v = fft2(rv1)

            # k2
            u2 = np.real(ifft2(Eu_half * (u_hat + 0.5 * dt * k1_u)))
            v2 = np.real(ifft2(Ev_half * (v_hat + 0.5 * dt * k1_v)))
            ru2, rv2 = kinetics(u2, v2)
            k2_u = fft2(ru2)
            k2_v = fft2(rv2)

            # k3
            u3 = np.real(ifft2(Eu_half * u_hat + 0.5 * dt * k2_u))
            v3 = np.real(ifft2(Ev_half * v_hat + 0.5 * dt * k2_v))
            ru3, rv3 = kinetics(u3, v3)
            k3_u = fft2(ru3)
            k3_v = fft2(rv3)

            # k4
            u4 = np.real(ifft2(Eu * u_hat + dt * Eu_half * k3_u))
            v4 = np.real(ifft2(Ev * v_hat + dt * Ev_half * k3_v))
            ru4, rv4 = kinetics(u4, v4)
            k4_u = fft2(ru4)
            k4_v = fft2(rv4)

            # Combine
            u_next_hat = Eu * u_hat + (dt / 6.0) * (Eu * k1_u + 2.0 * Eu_half * (k2_u + k3_u) + k4_u)
            v_next_hat = Ev * v_hat + (dt / 6.0) * (Ev * k1_v + 2.0 * Ev_half * (k2_v + k3_v) + k4_v)

            u_next = np.real(ifft2(u_next_hat))
            v_next = np.real(ifft2(v_next_hat))

            current_uv[..., 0] = u_next
            current_uv[..., 1] = v_next

            UV_clean[step] = current_uv
            UV_t_true[step] = self.rhs_spatial(current_uv, grid.x, grid.y)

        UV_obs = UV_clean.copy()
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed if random_seed is not None else 42)
            for c in range(2):
                std_c = np.std(UV_clean[..., c])
                noise_c = rng.normal(0.0, noise_level * (std_c if std_c > 1e-8 else 1.0), UV_clean[..., c].shape)
                UV_obs[..., c] = UV_clean[..., c] + noise_c

        import uuid
        return SpatiotemporalField(
            id=str(uuid.uuid4())[:8],
            pde_name=self.name,
            x=grid.x,
            y=grid.y,
            t=time_grid.t,
            u=UV_obs,
            channel_names=["u", "v"],
            boundary_condition=self.boundary_condition,
            spatial_dim=2,
            units={"u": "mV", "v": "au", "x": "mm", "y": "mm", "t": "ms"},
            u_clean=UV_clean,
            u_t_true=UV_t_true,
            true_parameters=self.parameters.copy(),
            noise_level=noise_level,
            provenance={
                "solver": "pseudo_spectral_IF_RK4",
                "grid_x": Nx,
                "grid_y": Ny,
                "time_steps": M,
            },
        )
