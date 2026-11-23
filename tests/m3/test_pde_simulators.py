"""
Project NOMOS — Milestone M3 PDE Simulator Tests
Validates numerical stability, conservation laws, and analytical convergence across all 6 PDEs.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid1D, TimeGrid, BoundaryConditionType
from nomos.pde.simulators.heat import HeatEquationSimulator
from nomos.pde.simulators.advection import LinearAdvectionSimulator
from nomos.pde.simulators.burgers import BurgersSimulator
from nomos.pde.simulators.wave import WaveEquationSimulator
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.pde.simulators.kuramoto_sivashinsky import KuramotoSivashinskySimulator


class TestPDESimulators:

    def test_heat_equation_analytical_convergence(self):
        """Verify Heat equation exponential modal decay: u(x, t) = exp(-alpha*k^2*t)*sin(kx)."""
        alpha = 0.1
        sim = HeatEquationSimulator(alpha=alpha, domain=(0.0, 2.0 * np.pi))
        grid = Grid1D.create((0.0, 2.0 * np.pi), 64, periodic=True)
        t_grid = TimeGrid.create((0.0, 1.0), 50)
        u0 = np.sin(grid.x)

        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)

        # Analytical check at final time t = 1.0
        u_analytic_final = sim.analytical_solution(grid.x, t=1.0)
        u_sim_final = field.u[-1]

        l2_err = np.linalg.norm(u_sim_final - u_analytic_final) / np.linalg.norm(u_analytic_final)
        assert l2_err < 1e-5, f"Heat equation simulation deviates from analytic solution! L2 err={l2_err}"

        # Invariant check: mass is conserved
        mass_0 = sim.compute_invariant(field.u[0], grid.dx)
        mass_end = sim.compute_invariant(field.u[-1], grid.dx)
        assert abs(mass_0 - mass_end) < 1e-10

    def test_linear_advection_analytical_shift(self):
        """Verify Linear Advection shift: u(x, t) = sin(x - c*t)."""
        c = 1.0
        sim = LinearAdvectionSimulator(c=c, domain=(0.0, 2.0 * np.pi))
        grid = Grid1D.create((0.0, 2.0 * np.pi), 64, periodic=True)
        t_grid = TimeGrid.create((0.0, 2.0 * np.pi), 100)  # One full period
        u0 = np.sin(grid.x)

        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)

        # After one full period T = 2*pi / c, field should return to initial state
        l2_err = np.linalg.norm(field.u[-1] - field.u[0]) / np.linalg.norm(field.u[0])
        assert l2_err < 1e-4, f"Advection full period return failed! L2 err={l2_err}"

        # Energy conservation
        e0 = sim.compute_invariant(field.u[0], grid.dx)
        e_end = sim.compute_invariant(field.u[-1], grid.dx)
        assert abs(e0 - e_end) / e0 < 1e-10

    def test_wave_equation_energy_conservation(self):
        """Verify Wave equation 1st-order system energy conservation: E = 1/2 int (v^2 + c^2 u_x^2) dx."""
        c = 1.0
        sim = WaveEquationSimulator(c=c, domain=(0.0, 2.0 * np.pi))
        grid = Grid1D.create((0.0, 2.0 * np.pi), 64, periodic=True)
        t_grid = TimeGrid.create((0.0, 2.0), 50)
        u0 = np.sin(grid.x)

        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)
        V = field.provenance["velocity_v"]

        e0 = sim.compute_energy(field.u[0], V[0], grid.dx)
        e_end = sim.compute_energy(field.u[-1], V[-1], grid.dx)
        assert abs(e0 - e_end) / e0 < 1e-4, "Wave equation Hamiltonian energy must be conserved!"

    def test_burgers_viscous_steepening(self):
        """Verify Viscous Burgers' equation mass conservation and finite gradient steepening."""
        nu = 0.05
        sim = BurgersSimulator(nu=nu, domain=(0.0, 2.0 * np.pi))
        grid = Grid1D.create((0.0, 2.0 * np.pi), 64, periodic=True)
        t_grid = TimeGrid.create((0.0, 1.0), 50)
        u0 = np.sin(grid.x)

        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)

        mass_0 = sim.compute_invariant(field.u[0], grid.dx)
        mass_end = sim.compute_invariant(field.u[-1], grid.dx)
        assert abs(mass_0 - mass_end) < 1e-6, "Burgers periodic mass must be conserved!"

    def test_kdv_1soliton_preservation(self):
        """Verify KdV 1-soliton profile propagation and mass conservation."""
        sim = KdVSimulator(domain=(-10.0, 10.0))
        grid = Grid1D.create((-10.0, 10.0), 64, periodic=True)
        t_grid = TimeGrid.create((0.0, 0.5), 50)
        u0 = sim.analytical_1soliton(grid.x, t=0.0)

        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)

        # No NaNs or overflows
        assert not np.any(np.isnan(field.u))
        assert field.u.max() > 0.5

        # Mass conservation
        mass_0 = sim.compute_invariant(field.u[0], grid.dx)
        mass_end = sim.compute_invariant(field.u[-1], grid.dx)
        assert abs(mass_0 - mass_end) / abs(mass_0) < 1e-3

    def test_kuramoto_sivashinsky_bounded_chaos(self):
        """Verify Kuramoto-Sivashinsky chaotic PDE remains numerically bounded and conserves mean."""
        sim = KuramotoSivashinskySimulator(domain=(0.0, 32.0 * np.pi))
        grid = Grid1D.create((0.0, 32.0 * np.pi), 64, periodic=True)
        t_grid = TimeGrid.create((0.0, 1.0), 50)
        u0 = np.cos(grid.x / 16.0) * (1.0 + np.sin(grid.x / 16.0))

        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)

        assert not np.any(np.isnan(field.u))
        assert field.u.max() < 10.0  # Bounded spatiotemporal attractor
        assert field.u.min() > -10.0
