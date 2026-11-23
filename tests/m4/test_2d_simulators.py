"""
Project NOMOS — Milestone M4 2D PDE Simulators Tests
Verifies Gray-Scott, FitzHugh-Nagumo, and Navier-Stokes 2D solvers.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid2D, TimeGrid
from nomos.pde.simulators.gray_scott import GrayScottSimulator
from nomos.pde.simulators.fitzhugh_nagumo import FitzHughNagumoSimulator
from nomos.pde.simulators.navier_stokes_2d import NavierStokes2DSimulator


class Test2DPDESimulators:

    def test_gray_scott_positivity_and_mass_variation(self):
        """Gray-Scott must maintain chemical positivity (u,v >= 0) while total mass is non-conserved."""
        grid = Grid2D.create((0.0, 2.5), (0.0, 2.5), 32, 32)
        t_grid = TimeGrid.create((0.0, 0.4), 10)
        sim = GrayScottSimulator(D_u=0.16, D_v=0.08, F=0.035, k=0.060)

        u0 = sim.default_initial_condition(grid)
        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)

        # Positivity
        assert np.all(field.u[..., 0] >= 0.0)
        assert np.all(field.u[..., 1] >= 0.0)
        assert not np.any(np.isnan(field.u))

        # Mass is not conserved
        m0 = sim.compute_invariant(field.u[0], grid.dx, grid.dy)
        m_end = sim.compute_invariant(field.u[-1], grid.dx, grid.dy)
        assert abs(m_end - m0) > 1e-4

    def test_fitzhugh_nagumo_bounded_dynamics(self):
        """FitzHugh-Nagumo excitable media integration must remain stable and bounded."""
        grid = Grid2D.create((-10.0, 10.0), (-10.0, 10.0), 32, 32)
        t_grid = TimeGrid.create((0.0, 0.5), 10)
        sim = FitzHughNagumoSimulator(D_u=1.0, D_v=0.0, eps=0.05, a1=0.5, a0=0.0)

        u0 = sim.default_initial_condition(grid)
        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)

        assert not np.any(np.isnan(field.u))
        # Amplitude bounded
        assert np.max(np.abs(field.u[..., 0])) < 5.0
        assert np.max(np.abs(field.u[..., 1])) < 5.0

    def test_navier_stokes_incompressibility_machine_precision(self):
        """Navier-Stokes velocity field must be divergence-free to machine precision."""
        grid = Grid2D.create((0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi), 32, 32)
        t_grid = TimeGrid.create((0.0, 0.5), 10)
        sim = NavierStokes2DSimulator(nu=0.01)

        _, u0, v0, om0 = sim.taylor_green_solution(grid.x, grid.y, 0.0)
        field = sim.simulate(om0, grid, t_grid, noise_level=0.0)

        # Max divergence of velocity field
        div_max = sim.compute_divergence(
            field.u[-1, :, :, 1], field.u[-1, :, :, 2], grid.dx, grid.dy
        )
        assert div_max < 1e-13

    def test_navier_stokes_taylor_green_analytical_decay(self):
        """Navier-Stokes vorticity must match exact analytical Taylor-Green decay."""
        grid = Grid2D.create((0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi), 32, 32)
        t_grid = TimeGrid.create((0.0, 1.0), 20)
        sim = NavierStokes2DSimulator(nu=0.02)

        _, u0, v0, om0 = sim.taylor_green_solution(grid.x, grid.y, 0.0)
        field = sim.simulate(om0, grid, t_grid, noise_level=0.0)

        # Compare with exact analytical solution at t=1.0
        _, _, _, om_exact_end = sim.taylor_green_solution(grid.x, grid.y, 1.0)
        om_num_end = field.u[-1, :, :, 0]

        max_err = np.max(np.abs(om_num_end - om_exact_end))
        assert max_err < 1e-10
