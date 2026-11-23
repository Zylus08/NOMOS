"""
NOMOS 2D Incompressible Navier–Stokes Simulator (Vorticity–Streamfunction Formulation)
PDE:
    omega_t + u * omega_x + v * omega_y = nu * (omega_xx + omega_yy) + f_omega
    u = psi_y,  v = -psi_x
    laplacian(psi) = -omega
Features:
- Analytically divergence-free velocity field: div(u) == 0 to machine precision
- Spectral Poisson inversion for streamfunction psi
- 2/3 Orszag spectral de-aliasing for quadratic advection
- Integrating Factor RK4 (IF-RK4) for exact viscous dissipation
- Exact Taylor–Green vortex analytical decay validation
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


class NavierStokes2DSimulator(BasePDE2DSimulator):
    """
    2D Incompressible Navier–Stokes pseudo-spectral solver on periodic domains.
    Computes vorticity omega and divergence-free velocities (u, v).
    """

    def __init__(
        self,
        nu: float = 0.01,
        domain_x: Tuple[float, float] = (0.0, 2.0 * np.pi),
        domain_y: Tuple[float, float] = (0.0, 2.0 * np.pi),
        boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC,
    ):
        super().__init__(
            name="navier_stokes_2d",
            parameters={"nu": float(nu)},
            boundary_condition=boundary_condition,
            domain_x=domain_x,
            domain_y=domain_y,
        )
        self.nu = float(nu)

    def _setup_spectral_operators(self, Nx: int, Ny: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        Lx = self.domain_x[1] - self.domain_x[0]
        Ly = self.domain_y[1] - self.domain_y[0]

        kx = (2.0 * np.pi / Lx) * fftfreq(Nx, 1.0 / Nx)
        ky = (2.0 * np.pi / Ly) * fftfreq(Ny, 1.0 / Ny)
        KX, KY = np.meshgrid(kx, ky, indexing="ij")
        K2 = KX**2 + KY**2

        # 2/3 Orszag de-aliasing mask
        k_max_x = np.max(np.abs(kx))
        k_max_y = np.max(np.abs(ky))
        dealias_mask = (np.abs(KX) <= (2.0 / 3.0) * k_max_x) & (np.abs(KY) <= (2.0 / 3.0) * k_max_y)

        # Poisson solver operator: laplacian(psi) = -omega  =>  psi_hat = omega_hat / K2 (with 0 mode set to 0)
        inv_K2 = np.zeros_like(K2)
        nonzero = K2 > 1e-12
        inv_K2[nonzero] = 1.0 / K2[nonzero]

        return KX, KY, K2, inv_K2, dealias_mask

    def streamfunction_and_velocity(
        self, omega: np.ndarray, KX: np.ndarray, KY: np.ndarray, inv_K2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Recover streamfunction psi and divergence-free velocities (u, v) from vorticity omega.
        u = psi_y, v = -psi_x
        """
        omega_hat = fft2(omega)
        psi_hat = omega_hat * inv_K2

        # In Fourier space:
        # u = psi_y  =>  u_hat = 1j * KY * psi_hat
        # v = -psi_x =>  v_hat = -1j * KX * psi_hat
        u_hat = 1j * KY * psi_hat
        v_hat = -1j * KX * psi_hat

        psi = np.real(ifft2(psi_hat))
        u = np.real(ifft2(u_hat))
        v = np.real(ifft2(v_hat))

        return psi, u, v

    def rhs_spatial(self, state: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Compute true spatial RHS for vorticity:
        omega_t = -u * omega_x - v * omega_y + nu * laplacian(omega)
        Input state shape: (Nx, Ny, 3) representing [omega, u, v] or (Nx, Ny) representing omega.
        """
        if state.ndim == 3:
            omega = state[..., 0]
        else:
            omega = state

        Nx, Ny = omega.shape
        KX, KY, K2, inv_K2, dealias_mask = self._setup_spectral_operators(Nx, Ny)

        # Spectral Poisson solve
        psi, u, v = self.streamfunction_and_velocity(omega, KX, KY, inv_K2)

        # Gradients of vorticity
        omega_hat = fft2(omega) * dealias_mask
        omega_x = np.real(ifft2(1j * KX * omega_hat))
        omega_y = np.real(ifft2(1j * KY * omega_hat))

        # Advective term
        advection = u * omega_x + v * omega_y

        # Viscous diffusion
        lap_omega = np.real(ifft2(-K2 * omega_hat))

        d_omega_dt = -advection + self.nu * lap_omega

        if state.ndim == 3:
            # For 3-channel state [omega, u, v], compute velocity time derivatives as well
            # u_t = (psi_t)_y, v_t = -(psi_t)_x
            d_omega_hat = fft2(d_omega_dt)
            d_psi_hat = d_omega_hat * inv_K2
            du_dt = np.real(ifft2(1j * KY * d_psi_hat))
            dv_dt = np.real(ifft2(-1j * KX * d_psi_hat))
            return np.stack([d_omega_dt, du_dt, dv_dt], axis=-1)

        return d_omega_dt

    def taylor_green_solution(self, x: np.ndarray, y: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Analytical Taylor–Green vortex decay:
        psi(x, y, t) = cos(x) * cos(y) * exp(-2 * nu * t)
        u(x, y, t)   = -cos(x) * sin(y) * exp(-2 * nu * t)
        v(x, y, t)   = +sin(x) * cos(y) * exp(-2 * nu * t)
        omega(x, y, t) = 2 * cos(x) * cos(y) * exp(-2 * nu * t)
        """
        X, Y = np.meshgrid(x, y, indexing="ij")
        decay = np.exp(-2.0 * self.nu * t)
        psi = np.cos(X) * np.cos(Y) * decay
        u = -np.cos(X) * np.sin(Y) * decay
        v = np.sin(X) * np.cos(Y) * decay
        omega = 2.0 * np.cos(X) * np.cos(Y) * decay
        return psi, u, v, omega

    def analytical_solution(
        self, x: np.ndarray, y: np.ndarray, t: float, u0_func: Optional[Callable] = None
    ) -> Optional[np.ndarray]:
        _, u, v, omega = self.taylor_green_solution(x, y, t)
        return np.stack([omega, u, v], axis=-1)

    def compute_energy(self, u: np.ndarray, v: np.ndarray, dx: float, dy: float) -> float:
        """Total kinetic energy: E = 0.5 * int (u^2 + v^2) dx dy."""
        return float(0.5 * np.sum(u**2 + v**2) * dx * dy)

    def compute_enstrophy(self, omega: np.ndarray, dx: float, dy: float) -> float:
        """Total enstrophy: Z = 0.5 * int (omega^2) dx dy."""
        return float(0.5 * np.sum(omega**2) * dx * dy)

    def compute_divergence(self, u: np.ndarray, v: np.ndarray, dx: float, dy: float) -> float:
        """Max absolute numerical divergence of velocity field: max |u_x + v_y|."""
        Nx, Ny = u.shape
        Lx = self.domain_x[1] - self.domain_x[0]
        Ly = self.domain_y[1] - self.domain_y[0]
        kx = (2.0 * np.pi / Lx) * fftfreq(Nx, 1.0 / Nx)
        ky = (2.0 * np.pi / Ly) * fftfreq(Ny, 1.0 / Ny)
        KX, KY = np.meshgrid(kx, ky, indexing="ij")

        div_hat = 1j * KX * fft2(u) + 1j * KY * fft2(v)
        div = np.real(ifft2(div_hat))
        return float(np.max(np.abs(div)))

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

        KX, KY, K2, inv_K2, dealias_mask = self._setup_spectral_operators(Nx, Ny)

        # Viscous Integrating Factor
        L = -self.nu * K2
        E = np.exp(L * dt)
        E_half = np.exp(L * (0.5 * dt))

        def nonlinear_rhs_hat(omega_real: np.ndarray) -> np.ndarray:
            _, u_vel, v_vel = self.streamfunction_and_velocity(omega_real, KX, KY, inv_K2)
            om_hat = fft2(omega_real) * dealias_mask
            om_x = np.real(ifft2(1j * KX * om_hat))
            om_y = np.real(ifft2(1j * KY * om_hat))
            advec = u_vel * om_x + v_vel * om_y
            return fft2(-advec) * dealias_mask

        # Initial state setup
        if u0.ndim == 3:
            curr_omega = np.array(u0[..., 0], dtype=np.float64, copy=True)
        else:
            curr_omega = np.array(u0, dtype=np.float64, copy=True)

        State_clean = np.zeros((M, Nx, Ny, 3), dtype=np.float64)
        State_t_true = np.zeros((M, Nx, Ny, 3), dtype=np.float64)

        _, u_init, v_init = self.streamfunction_and_velocity(curr_omega, KX, KY, inv_K2)
        State_clean[0] = np.stack([curr_omega, u_init, v_init], axis=-1)
        State_t_true[0] = self.rhs_spatial(State_clean[0], grid.x, grid.y)

        # IF-RK4 Time Integration
        for step in range(1, M):
            om_hat = fft2(curr_omega)

            # k1
            k1_hat = nonlinear_rhs_hat(curr_omega)

            # k2
            om2 = np.real(ifft2(E_half * (om_hat + 0.5 * dt * k1_hat)))
            k2_hat = nonlinear_rhs_hat(om2)

            # k3
            om3 = np.real(ifft2(E_half * om_hat + 0.5 * dt * k2_hat))
            k3_hat = nonlinear_rhs_hat(om3)

            # k4
            om4 = np.real(ifft2(E * om_hat + dt * E_half * k3_hat))
            k4_hat = nonlinear_rhs_hat(om4)

            # Combine
            om_next_hat = E * om_hat + (dt / 6.0) * (E * k1_hat + 2.0 * E_half * (k2_hat + k3_hat) + k4_hat)
            curr_omega = np.real(ifft2(om_next_hat))

            _, u_step, v_step = self.streamfunction_and_velocity(curr_omega, KX, KY, inv_K2)
            State_clean[step] = np.stack([curr_omega, u_step, v_step], axis=-1)
            State_t_true[step] = self.rhs_spatial(State_clean[step], grid.x, grid.y)

        # Noise injection
        State_obs = State_clean.copy()
        if noise_level > 0.0:
            rng = np.random.RandomState(random_seed if random_seed is not None else 42)
            for c in range(3):
                std_c = np.std(State_clean[..., c])
                noise_c = rng.normal(0.0, noise_level * (std_c if std_c > 1e-8 else 1.0), State_clean[..., c].shape)
                State_obs[..., c] = State_clean[..., c] + noise_c

        import uuid
        return SpatiotemporalField(
            id=str(uuid.uuid4())[:8],
            pde_name=self.name,
            x=grid.x,
            y=grid.y,
            t=time_grid.t,
            u=State_obs,
            channel_names=["omega", "u", "v"],
            boundary_condition=self.boundary_condition,
            spatial_dim=2,
            units={"omega": "1/s", "u": "m/s", "v": "m/s", "x": "m", "y": "m", "t": "s"},
            u_clean=State_clean,
            u_t_true=State_t_true,
            true_parameters=self.parameters.copy(),
            noise_level=noise_level,
            provenance={
                "solver": "vorticity_streamfunction_spectral_IF_RK4",
                "grid_x": Nx,
                "grid_y": Ny,
                "time_steps": M,
                "dealiasing": "2/3 Orszag",
            },
        )
