"""
Project NOMOS — Milestone M4 Coupled AST Grammar & Scale-Adaptive Search Tests
Verifies 2D AST nodes, SymPy algebraic equivalence, and Burgers recovery resolution.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid1D, TimeGrid
from nomos.pde.grammar import DiffNode, DiffNodeType, check_differential_algebraic_equivalence
from nomos.pde.simulators.burgers import BurgersSimulator
from nomos.pde.symbolic_search import DifferentialBeamSearch


class TestCoupledASTGrammar:

    def test_sympy_differential_algebraic_equivalences(self):
        """Verify formal SymPy canonical algebraic equivalence for 1D and 2D operators."""
        # 2D Laplacian identity
        assert check_differential_algebraic_equivalence("Laplacian(u)", "u_xx + u_yy")
        # Product rule
        assert check_differential_algebraic_equivalence("Dx(u**2)", "2*u*u_x")
        # Linearity
        assert check_differential_algebraic_equivalence("Dx(u + v)", "u_x + v_x")

    def test_differential_ast_2d_laplacian_evaluation(self):
        """Verify AST DiffNode evaluates 2D Laplacian on multi-dimensional array."""
        u_node = DiffNode(DiffNodeType.FIELD_VAR, name="u")
        lap_node = DiffNode(DiffNodeType.LAPLACIAN, children=[u_node])

        x = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        y = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        X, Y = np.meshgrid(x, y, indexing="ij")
        U_2d = np.sin(X) * np.sin(Y)
        # Analytical laplacian of sin(x)*sin(y) is -2*sin(x)*sin(y)
        expected_lap = -2.0 * np.sin(X) * np.sin(Y)

        U_tensor = U_2d[None, ...]  # shape (1, 32, 32)
        dx = x[1] - x[0]
        dy = y[1] - y[0]

        computed_lap = lap_node.evaluate({"u": U_tensor}, dx=dx, dy=dy, periodic=True, method="spectral")
        err = np.max(np.abs(computed_lap[0] - expected_lap))
        assert err < 1e-10

    def test_scale_adaptive_burgers_recovery(self):
        """Verify scale-adaptive scoring recovers exact 2-term Burgers equation (nu*u_xx - u*u_x)."""
        sim = BurgersSimulator(nu=0.05)
        grid = Grid1D.create((0.0, 2.0 * np.pi), 64)
        t_grid = TimeGrid.create((0.0, 1.0), 50)
        u0 = np.sin(grid.x)
        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)

        searcher = DifferentialBeamSearch(scoring_mode="adaptive", complexity_penalty=1e-4)
        res = searcher.fit(field)

        assert "u_xx" in res.coefficients
        assert "u*u_x" in res.coefficients
        assert abs(res.coefficients["u_xx"] - 0.05) < 0.01
        assert abs(res.coefficients["u*u_x"] - (-1.0)) < 0.05
