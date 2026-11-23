"""
Project NOMOS — Milestone M4 2D Weak-Form Discovery Tests (WSINDy-2D)
Verifies 3D space-time test functions, boundary vanishing, and coupled reaction-diffusion recovery.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid2D, TimeGrid
from nomos.pde.simulators.fitzhugh_nagumo import FitzHughNagumoSimulator
from nomos.pde.weak_form_2d import WeakForm2DPDEDiscovery


class TestWSINDy2D:

    def test_compact_test_function_vanishing_boundaries(self):
        """Test functions and derivatives must vanish at compact support boundaries."""
        engine = WeakForm2DPDEDiscovery()
        coord = np.linspace(0, 10, 100)
        center = 5.0
        radius = 2.0

        val, d1, d2, mask = engine._1d_compact_poly(coord, center, radius)
        # Inside support
        assert val[50] > 0.0
        # Exactly outside support: |coord - 5| >= 2.0 (i.e. <= 3.0 or >= 7.0)
        assert val[0] == 0.0
        assert val[-1] == 0.0
        assert d1[0] == 0.0
        assert d2[0] == 0.0

    def test_wsindy_2d_fitzhugh_nagumo_recovery(self):
        """WSINDy-2D must isolate exact support for FitzHugh-Nagumo u_t under noise."""
        grid = Grid2D.create((-10.0, 10.0), (-10.0, 10.0), 32, 32)
        t_grid = TimeGrid.create((0.0, 1.0), 40)
        sim = FitzHughNagumoSimulator(D_u=1.0, D_v=0.0, eps=0.05, a1=0.5, a0=0.0)

        u0 = sim.default_initial_condition(grid)
        field = sim.simulate(u0, grid, t_grid, noise_level=0.01, random_seed=42)

        engine = WeakForm2DPDEDiscovery(num_test_functions=80, threshold=0.02, random_seed=42)
        res = engine.fit_channel(field, "u", ["lap_u", "u", "u^3", "v"])

        assert "lap_u" in res.coefficients
        assert "u" in res.coefficients
        assert "u^3" in res.coefficients
        assert "v" in res.coefficients

        # Check coefficient accuracy
        assert abs(res.coefficients["lap_u"] - 1.0) < 0.05
        assert abs(res.coefficients["u"] - 1.0) < 0.05
        assert abs(res.coefficients["u^3"] - (-1.0)) < 0.05
        assert abs(res.coefficients["v"] - (-1.0)) < 0.05
