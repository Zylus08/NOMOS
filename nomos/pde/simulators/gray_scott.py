"""
NOMOS 2D Coupled Gray–Scott Reaction–Diffusion Simulator
PDE:
    u_t = D_u * (u_xx + u_yy) - u * v^2 + F * (1 - u)
    v_t = D_v * (v_xx + v_yy) + u * v^2 - (F + k) * v
Models spot division, labyrinthine patterns, and solitary waves in chemical kinetics.
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


class GrayScottSimulator(BasePDE2DSimulator):
    """
    High-precision pseudo-spectral simulator for the 2D Gray–Scott model.
    Solves stiff diffusion via Integrating-Factor Runge-Kutta 4 (IF-RK4).
    """

    def __init__(
        self,
        D_u: float = 0.16,
        D_v: float = 0.08,
        F: float = 0.035,
        k: float = 0.060,
        domain_x: Tuple[float, float] = (0.0, 2.5),
        domain_y: Tuple[float, float] = (0.0, 2.5),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="gray_scott_2d",
            parameters={"D_u": float(D_u), "D_v": float(D_v), "F": float(F), "k": float(k)},
            boundary_condition=boundary_condition,
            domain_x=domain_x,
            domain_y=domain_y,
        )
        self.D_u = float(D_u)
        self.D_v = float(D_v)
        self.F = float(F)
        self.k = float(k)

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

        # 2D Spectral Laplacians
        lap_u = np.real(ifft2(-K2 * fft2(u)))
        lap_v = np.real(ifft2(-K2 * fft2(v)))

        # Nonlinear reaction terms
        uv2 = u * (v**2)
        du_dt = self.D_u * lap_u - uv2 + self.F * (1.0 - u)
        dv_dt = self.D_v * lap_v + uv2 - (self.F + self.k) * v

        return np.stack([du_dt, dv_dt], axis=-1)

    def default_initial_condition(self, grid: Grid2D) -> np.ndarray:
        """
        Standard Pearson spot-perturbation initial condition:
        u = 1.0 everywhere, v = 0.0 everywhere, except a central square where
        u = 0.5 and v = 0.25 plus slight noise.
        """
        X, Y = grid.meshgrid
        Lx = self.domain_x[1] - self.domain_x[0]
        Ly = self.domain_y[1] - self.domain_y[0]
        cx = self.domain_x[0] + 0.5 * Lx
        cy = self.domain_y[0] + 0.5 * Ly
        r = 0.15 * min(Lx, Ly)

        u = np.ones((grid.num_points_x, grid.num_points_y), dtype=np.float64)
        v = np.zeros((grid.num_points_x, grid.num_points_y), dtype=np.float64)

        mask = (np.abs(X - cx) < r) & (np.abs(Y - cy) < r)
        u[mask] = 0.50
        v[mask] = 0.25

        return np.stack([u, v], axis=-1)

    def compute_total_mass(self, uv: np.ndarray, dx: float, dy: float) -> Tuple[float, float]:
        """Compute integral mass M_u = int u dx dy, M_v = int v dx dy."""
        u = uv[..., 0]
        v = uv[..., 1]
        m_u = float(np.sum(u) * dx * dy)
        m_v = float(np.sum(v) * dx * dy)
        return m_u, m_v

    def compute_invariant(self, uv: np.ndarray, dx: float, dy: float) -> Optional[float]:
        """Returns total chemical mass M = int (u + v) dx dy (strictly non-conserved)."""
        mu, mv = self.compute_total_mass(uv, dx, dy)
        return mu + mv

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

        # Integrating Factor operators:
        # L_u = -D_u * K2, L_v = -D_v * K2
        Lu = -self.D_u * K2
        Lv = -self.D_v * K2

        Eu = np.exp(Lu * dt)
        Eu_half = np.exp(Lu * (0.5 * dt))
        Ev = np.exp(Lv * dt)
        Ev_half = np.exp(Lv * (0.5 * dt))

        def reactions(u_real, v_real):
            # Positivity guard
            u_pos = np.maximum(u_real, 0.0)
            v_pos = np.maximum(v_real, 0.0)
            uv2 = u_pos * (v_pos**2)
            ru = -uv2 + self.F * (1.0 - u_pos)
            rv = +uv2 - (self.F + self.k) * v_pos
            return ru, rv

        # State storage: (M, Nx, Ny, 2)
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
            ru1, rv1 = reactions(u, v)
            k1_u = fft2(ru1)
            k1_v = fft2(rv1)

            # k2
            u2 = np.real(ifft2(Eu_half * (u_hat + 0.5 * dt * k1_u)))
            v2 = np.real(ifft2(Ev_half * (v_hat + 0.5 * dt * k1_v)))
            ru2, rv2 = reactions(u2, v2)
            k2_u = fft2(ru2)
            k2_v = fft2(rv2)

            # k3
            u3 = np.real(ifft2(Eu_half * u_hat + 0.5 * dt * k2_u))
            v3 = np.real(ifft2(Ev_half * v_hat + 0.5 * dt * k2_v))
            ru3, rv3 = reactions(u3, v3)
            k3_u = fft2(ru3)
            k3_v = fft2(rv3)

            # k4
            u4 = np.real(ifft2(Eu * u_hat + dt * Eu_half * k3_u))
            v4 = np.real(ifft2(Ev * v_hat + dt * Ev_half * k3_v))
            ru4, rv4 = reactions(u4, v4)
            k4_u = fft2(ru4)
            k4_v = fft2(rv4)

            # Combine
            u_next_hat = Eu * u_hat + (dt / 6.0) * (Eu * k1_u + 2.0 * Eu_half * (k2_u + k3_u) + k4_u)
            v_next_hat = Ev * v_hat + (dt / 6.0) * (Ev * k1_v + 2.0 * Ev_half * (k2_v + k3_v) + k4_v)

            u_next = np.maximum(np.real(ifft2(u_next_hat)), 0.0)
            v_next = np.maximum(np.real(ifft2(v_next_hat)), 0.0)

            current_uv[..., 0] = u_next
            current_uv[..., 1] = v_next

            UV_clean[step] = current_uv
            UV_t_true[step] = self.rhs_spatial(current_uv, grid.x, grid.y)

        # Measurement noise injection
        UV_obs = UV_clean.copy()
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed if random_seed is not None else 42)
            for c in range(2):
                std_c = np.std(UV_clean[..., c])
                noise_c = rng.normal(0.0, noise_level * (std_c if std_c > 1e-8 else 1.0), UV_clean[..., c].shape)
                UV_obs[..., c] = np.maximum(UV_clean[..., c] + noise_c, 0.0)

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
            units={"u": "mol/m^2", "v": "mol/m^2", "x": "m", "y": "m", "t": "s"},
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
