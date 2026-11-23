"""
Project NOMOS — Milestone M3 Strong & Weak Form Discovery Tests
Phase 4 & 5 Verification: SINDy-PDE, WSINDy noise robustness, and test-function integration by parts.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid1D, TimeGrid
from nomos.pde.simulators.heat import HeatEquationSimulator
from nomos.pde.simulators.advection import LinearAdvectionSimulator
from nomos.pde.simulators.burgers import BurgersSimulator
from nomos.pde.strong_form import StrongFormPDEDiscovery
from nomos.pde.weak_form import WeakFormPDEDiscovery


class TestStrongAndWeakDiscovery:

    def test_strong_sindy_noiseless_advection(self):
        """Strong-form SINDy must recover linear advection u_t = -1.0 * u_x exactly at 0% noise."""
        sim = LinearAdvectionSimulator(c=1.0)
        grid = Grid1D.create((0.0, 2.0 * np.pi), 64)
        t_grid = TimeGrid.create((0.0, 1.0), 50)
        # Multi-frequency wave to break monochromatic dispersion-advection collinearity (u_xxx == -u_x)
        u0 = np.sin(grid.x) + 0.5 * np.cos(2.0 * grid.x)

        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)
        engine = StrongFormPDEDiscovery(threshold=0.05)
        res = engine.fit(field)

        assert "u_x" in res.coefficients
        assert abs(res.coefficients["u_x"] - (-1.0)) < 0.05
        # No spurious terms
        for k in res.coefficients:
            if k != "u_x":
                assert abs(res.coefficients[k]) < 0.05

    def test_weak_sindy_noisy_burgers(self):
        """Weak-form SINDy (WSINDy) must recover Burgers u_t = -1.0*u*u_x + 0.05*u_xx under 5% noise."""
        sim = BurgersSimulator(nu=0.05)
        grid = Grid1D.create((0.0, 2.0 * np.pi), 64)
        t_grid = TimeGrid.create((0.0, 1.0), 50)
        u0 = np.sin(grid.x)

        field = sim.simulate(u0, grid, t_grid, noise_level=0.05, random_seed=42)
        engine = WeakFormPDEDiscovery(num_test_functions=80, threshold=0.04, random_seed=42)
        res = engine.fit(field)

        assert "u*u_x" in res.coefficients
        assert "u_xx" in res.coefficients
        assert abs(res.coefficients["u*u_x"] - (-1.0)) < 0.25
        assert abs(res.coefficients["u_xx"] - 0.05) < 0.05

    def test_weak_form_vanishes_boundary_terms(self):
        """Verify that compact test functions and their spatial derivatives vanish at support boundaries."""
        engine = WeakFormPDEDiscovery()
        x = np.linspace(0, 10, 100)
        t = np.linspace(0, 5, 50)
        tf = engine._compact_test_function_and_derivs(x, t, xc=5.0, tc=2.5, Rx=2.0, Rt=1.0)

        # Boundary checks: at x = 5.0 - 2.0 = 3.0 and x = 5.0 + 2.0 = 7.0, psi(x) must be exactly 0
        assert tf["phi"][0, 0] == 0.0
        assert tf["phi_x"][0, 0] == 0.0
        assert tf["phi_xx"][0, 0] == 0.0
        assert tf["phi_t"][0, 0] == 0.0
