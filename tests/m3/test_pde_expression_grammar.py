"""
Project NOMOS — Milestone M3 Differential Grammar & Neural Guidance Tests
Phase 6 & 7 Verification: AST differential evaluation, SymPy equivalence, and Conv1D surrogate.
"""

import pytest
import numpy as np
import sympy as sp

from nomos.pde.schema import Grid1D, TimeGrid
from nomos.pde.grammar import (
    DiffNode,
    DiffNodeType,
    check_differential_algebraic_equivalence,
)
from nomos.pde.simulators.heat import HeatEquationSimulator
from nomos.pde.neural_surrogate import Conv1DPDESurrogate, NeuralPDESurrogateTrainer


class TestGrammarAndNeuralGuidance:

    def test_differential_ast_evaluation(self):
        """Verify DiffNode spatial evaluation of d(u^2)/dx on numerical grid."""
        N = 64
        x = np.linspace(0, 2 * np.pi, N, endpoint=False)
        dx = float(2 * np.pi / N)
        u = np.sin(x)[None, :]  # Shape (1, N)

        # Build AST: DiffNode DIFF_X( POW(u, 2) )
        term_u = DiffNode(DiffNodeType.FIELD_VAR, name="u")
        pow_node = DiffNode(DiffNodeType.POW, value=2, children=[term_u])
        diff_node = DiffNode(DiffNodeType.DIFF_X, children=[pow_node])

        # Evaluate AST
        val = diff_node.evaluate({"u": u}, dx=dx, periodic=True)

        # Analytical: d(sin^2(x))/dx = 2 * sin(x) * cos(x) = sin(2x)
        expected = np.sin(2.0 * x)[None, :]
        assert np.max(np.abs(val - expected)) < 1e-3

    def test_differential_algebraic_equivalence_sympy(self):
        """Verify SymPy recognition that d(u^2)/dx == 2*u*u_x."""
        eq1 = "Dx(u**2)"
        eq2 = "2 * u * Dx(u)"
        assert check_differential_algebraic_equivalence(eq1, eq2)

        eq3 = "Dxx(u)"
        eq4 = "Dx(Dx(u))"
        assert check_differential_algebraic_equivalence(eq3, eq4)

        eq_non_equiv = "u * Dx(u)"
        assert not check_differential_algebraic_equivalence(eq1, eq_non_equiv)

    def test_conv1d_neural_surrogate_training(self):
        """Verify Conv1DPDESurrogate forward pass and trainer execution."""
        sim = HeatEquationSimulator(alpha=0.1)
        grid = Grid1D.create((0.0, 2.0 * np.pi), 32)
        t_grid = TimeGrid.create((0.0, 0.5), 20)
        u0 = np.sin(grid.x)

        field = sim.simulate(u0, grid, t_grid, noise_level=0.0)

        trainer = NeuralPDESurrogateTrainer(epochs=15, random_seed=42)
        metrics = trainer.fit(field)

        assert metrics["final_loss"] < 0.1
        assert metrics["training_time"] > 0.0

        # Operator sensitivities
        sens = trainer.compute_operator_sensitivities(field, ["u_xx", "u_x", "u*u_x"])
        assert "u_xx" in sens
        assert sens["u_xx"] > 0.0
