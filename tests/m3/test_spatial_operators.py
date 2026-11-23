"""
Project NOMOS — Milestone M3 Spatial Differential Operator Tests
Phase 3 Verification: Finite difference stencils, periodic spectral differentiation, and boundary guards.
"""

import pytest
import numpy as np

from nomos.pde.operators import (
    finite_difference_1d,
    spectral_derivative_1d,
    compute_derivative,
    compute_pde_derivatives_matrix,
)


class TestSpatialOperators:

    def test_spectral_vs_analytic_sine(self):
        """Spectral derivative of sin(x) on [0, 2*pi] must match cos(x) to machine precision."""
        N = 64
        x = np.linspace(0, 2 * np.pi, N, endpoint=False)
        dx = float(2 * np.pi / N)
        u = np.sin(x)

        # 1st derivative: cos(x)
        u_x_spec = spectral_derivative_1d(u, dx=dx, order=1, periodic=True)
        u_x_true = np.cos(x)
        assert np.max(np.abs(u_x_spec - u_x_true)) < 1e-12

        # 2nd derivative: -sin(x)
        u_xx_spec = spectral_derivative_1d(u, dx=dx, order=2, periodic=True)
        u_xx_true = -np.sin(x)
        assert np.max(np.abs(u_xx_spec - u_xx_true)) < 1e-12

        # 3rd derivative: -cos(x)
        u_xxx_spec = spectral_derivative_1d(u, dx=dx, order=3, periodic=True)
        u_xxx_true = -np.cos(x)
        assert np.max(np.abs(u_xxx_spec - u_xxx_true)) < 1e-11

        # 4th derivative: sin(x)
        u_xxxx_spec = spectral_derivative_1d(u, dx=dx, order=4, periodic=True)
        u_xxxx_true = np.sin(x)
        assert np.max(np.abs(u_xxxx_spec - u_xxxx_true)) < 1e-9

    def test_spectral_nonperiodic_guard(self):
        """Spectral differentiation must strictly raise ValueError when periodic=False."""
        u = np.linspace(0, 1, 10)
        with pytest.raises(ValueError, match="strictly requires periodic boundary conditions"):
            spectral_derivative_1d(u, dx=0.1, order=1, periodic=False)

    def test_finite_difference_orders(self):
        """Test 4th order finite difference stencils for 1st, 2nd, 3rd, and 4th derivatives."""
        N = 128
        x = np.linspace(0, 2 * np.pi, N, endpoint=False)
        dx = float(2 * np.pi / N)
        u = np.sin(x)

        # 1st order centered FD error should be O(dx^4)
        u_x_fd = finite_difference_1d(u, dx=dx, order=1, accuracy=4, periodic=True)
        err_1 = np.max(np.abs(u_x_fd - np.cos(x)))
        assert err_1 < 1e-4

        # 2nd order centered FD
        u_xx_fd = finite_difference_1d(u, dx=dx, order=2, accuracy=4, periodic=True)
        err_2 = np.max(np.abs(u_xx_fd - (-np.sin(x))))
        assert err_2 < 1e-4

        # 3rd order centered FD
        u_xxx_fd = finite_difference_1d(u, dx=dx, order=3, periodic=True)
        err_3 = np.max(np.abs(u_xxx_fd - (-np.cos(x))))
        assert err_3 < 1e-3

        # 4th order centered FD
        u_xxxx_fd = finite_difference_1d(u, dx=dx, order=4, periodic=True)
        err_4 = np.max(np.abs(u_xxxx_fd - np.sin(x)))
        assert err_4 < 1e-2

    def test_derivatives_matrix_keys(self):
        """Verify that compute_pde_derivatives_matrix constructs all standard candidate terms."""
        M, N = 10, 32
        u = np.ones((M, N))
        derivs = compute_pde_derivatives_matrix(u, dx=0.1, dt=0.05, periodic=True)

        for expected in ["u", "u_t", "u_x", "u_xx", "u_xxx", "u_xxxx", "u^2", "u^3", "u*u_x"]:
            assert expected in derivs
            assert derivs[expected].shape == (M, N)
