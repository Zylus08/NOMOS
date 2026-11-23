"""
Project NOMOS — Milestone M4 Active Identifiability Tests
Verifies model disagreement calculation, optimal experiment selection, and hypothesis falsification.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid1D, TimeGrid
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.pde.operators import compute_derivative
from nomos.pde.active_identifiability import ActiveIdentifiabilityEngine


class TestActiveIdentifiability:

    def test_traveling_wave_degeneracy_detection(self):
        """Verify engine detects zero model disagreement on single KdV soliton."""
        sim = KdVSimulator(domain=(-10.0, 10.0))
        grid = Grid1D.create((-10.0, 10.0), 128)
        dx = grid.dx

        # Impostor: u_t = -2.0 * u_x
        def m1_impostor(u):
            ux = compute_derivative(u, dx=dx, order=1, method="spectral", periodic=True)
            return -2.0 * ux

        # True: u_t = -6.0 * u * u_x - u_xxx
        def m2_true(u):
            ux = compute_derivative(u, dx=dx, order=1, method="spectral", periodic=True)
            uxxx = compute_derivative(u, dx=dx, order=3, method="spectral", periodic=True)
            return -6.0 * u * ux - uxxx

        engine = ActiveIdentifiabilityEngine()
        u0_single = sim.analytical_1soliton(grid.x, 0.0, c=2.0)
        d_single = engine.compute_model_disagreement(m1_impostor, m2_true, u0_single)

        # Disagreement on single soliton must be negligible (< 1e-4)
        assert d_single < 1e-4

        # Disagreement on multi-soliton or wave packet must be substantial (> 0.5)
        u0_2soliton = sim.analytical_1soliton(grid.x, 0.0, c=4.0, x0=-4.0) + sim.analytical_1soliton(grid.x, 0.0, c=2.0, x0=2.0)
        d_multi = engine.compute_model_disagreement(m1_impostor, m2_true, u0_2soliton)
        assert d_multi > 0.5

    def test_active_vs_fixed_experiment_selection(self):
        """Active selection must pick the maximally discriminative experiment."""
        sim = KdVSimulator(domain=(-10.0, 10.0))
        grid = Grid1D.create((-10.0, 10.0), 128)
        dx = grid.dx

        def m1_impostor(u):
            ux = compute_derivative(u, dx=dx, order=1, method="spectral", periodic=True)
            return -2.0 * ux

        def m2_true(u):
            ux = compute_derivative(u, dx=dx, order=1, method="spectral", periodic=True)
            uxxx = compute_derivative(u, dx=dx, order=3, method="spectral", periodic=True)
            return -6.0 * u * ux - uxxx

        u0_single = sim.analytical_1soliton(grid.x, 0.0, c=2.0)
        u0_multi = sim.analytical_1soliton(grid.x, 0.0, c=4.0, x0=-4.0) + sim.analytical_1soliton(grid.x, 0.0, c=2.0, x0=2.0)

        pool = [("single_soliton", u0_single), ("multi_soliton", u0_multi)]
        engine = ActiveIdentifiabilityEngine()

        best_label, best_u0, max_d, _ = engine.select_optimal_experiment(m1_impostor, m2_true, pool)
        assert best_label == "multi_soliton"
        assert max_d > 0.5
