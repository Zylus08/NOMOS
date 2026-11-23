"""
Project NOMOS — Milestone M2.1 Regression Test Suite
Adversarial Scientific Verification & Regression Defense
"""

import pytest
import numpy as np
import sympy as sp

from nomos.evaluation.symbolic_classifier import (
    RecoveryClass,
    classify_equation_recovery,
)
from nomos.sparse.stlsq import STLSQ
from nomos.library.polynomial import PolynomialLibrary
from nomos.physics.harmonic_oscillator import HarmonicOscillator
from nomos.physics.solvers import simulate_system
from nomos.pipeline.m2_pipeline import M2DiscoveryEngine, M2DiscoveryConfig
from nomos.data.schema import Trajectory, TrajectoryDataset


class TestRationalKineticsVerification:
    """Rigorous verification that spurious rational expressions are never marked exact."""

    def test_rational_spurious_rejection(self):
        """Verify that 0.5286 / x is strictly rejected as EXACT_SYMBOLIC or ALGEBRAICALLY_EQUIVALENT."""
        cand_eq = "0.5286 / x"
        true_eq = "(2.0 * x) / (1.0 + x) - 0.5 * x"
        vars = ["x"]
        grid = np.linspace(0.1, 5.0, 50).reshape(-1, 1)

        result = classify_equation_recovery(
            cand_expr_str=cand_eq,
            true_expr_str=true_eq,
            variable_names=vars,
            test_points=grid,
            rollout_rmse=0.41,
        )

        assert result.status not in [
            RecoveryClass.EXACT_SYMBOLIC,
            RecoveryClass.ALGEBRAICALLY_EQUIVALENT,
            RecoveryClass.CORRECT_SUPPORT_APPROXIMATE_COEFFICIENTS,
        ], f"Spurious rational model must NOT be marked exact! Got: {result.status}"
        assert result.status in [RecoveryClass.APPROXIMATE_VECTOR_FIELD, RecoveryClass.ROLLOUT_ONLY_MATCH]
        assert not result.is_exact_or_equivalent

    def test_rational_exact_symbolic(self):
        """Verify that the true Michaelis-Menten expression is certified as EXACT_SYMBOLIC."""
        cand_eq = "(2.0 * x) / (1.0 + x) - 0.5 * x"
        true_eq = "(2.0 * x) / (1.0 + x) - 0.5 * x"
        vars = ["x"]
        grid = np.linspace(0.1, 5.0, 50).reshape(-1, 1)

        result = classify_equation_recovery(
            cand_expr_str=cand_eq,
            true_expr_str=true_eq,
            variable_names=vars,
            test_points=grid,
            rollout_rmse=0.0,
        )

        assert result.status == RecoveryClass.EXACT_SYMBOLIC
        assert result.is_exact_or_equivalent

    def test_rational_algebraic_equivalent(self):
        """Verify that common-denominator expanded Michaelis-Menten is ALGEBRAICALLY_EQUIVALENT."""
        cand_eq = "(1.5 * x - 0.5 * x**2) / (1.0 + x)"
        true_eq = "(2.0 * x) / (1.0 + x) - 0.5 * x"
        vars = ["x"]
        grid = np.linspace(0.1, 5.0, 50).reshape(-1, 1)

        result = classify_equation_recovery(
            cand_expr_str=cand_eq,
            true_expr_str=true_eq,
            variable_names=vars,
            test_points=grid,
            rollout_rmse=0.0,
        )

        assert result.status in [RecoveryClass.EXACT_SYMBOLIC, RecoveryClass.ALGEBRAICALLY_EQUIVALENT]
        assert result.is_exact_or_equivalent


class TestHarmonicBaselineParity:
    """Verify the collinearity mathematics of harmonic oscillator SINDy."""

    def test_harmonic_fair_multi_orbit_recovery(self):
        """Multi-orbit SINDy must recover the harmonic oscillator exactly with 0 rollout error."""
        system = HarmonicOscillator()
        t_eval = np.linspace(0, 10, 500)

        # Multi-orbit training on two energy levels (r=1.0 and r=sqrt(2.5))
        sim1 = simulate_system(system, x0=np.array([1.0, 0.0]), t_span=(0, 10), t_eval=t_eval)
        sim2 = simulate_system(system, x0=np.array([1.5, 0.5]), t_span=(0, 10), t_eval=t_eval)
        X = np.vstack([sim1.x, sim2.x])
        X_dot = np.vstack([sim1.x_dot_true, sim2.x_dot_true])

        lib = PolynomialLibrary(degree=2, include_bias=True)
        Theta = lib.fit_transform(X)

        opt = STLSQ(threshold=0.05, alpha=1e-5)
        opt_res = opt.fit(Theta, X_dot)
        coef = opt_res.coef

        # Equation 0 (x_dot = 1.0 * v): lib features = [1, x, v, x^2, xv, v^2]
        # x is idx 1, v is idx 2
        assert abs(coef[2, 0] - 1.0) < 1e-3
        assert np.max(np.abs(coef[[0, 1, 3, 4, 5], 0])) < 1e-3

        # Equation 1 (v_dot = -1.0 * x)
        assert abs(coef[1, 1] - (-1.0)) < 1e-3
        assert np.max(np.abs(coef[[0, 2, 3, 4, 5], 1])) < 1e-3

    def test_harmonic_single_orbit_d3_collinearity(self):
        """Single-orbit degree 3 SINDy must demonstrate energy manifold rank deficiency / high condition number."""
        system = HarmonicOscillator()
        t_eval = np.linspace(0, 10, 500)

        sim = simulate_system(system, x0=np.array([1.0, 0.0]), t_span=(0, 10), t_eval=t_eval)
        X = sim.x

        lib = PolynomialLibrary(degree=3, include_bias=True)
        Theta = lib.fit_transform(X)

        # Check condition number of Theta: should be ill-conditioned on a single orbit
        cond = np.linalg.cond(Theta)
        assert cond > 1e4, f"Degree 3 library on single circle must be ill-conditioned! Got cond={cond}"


class TestDomainSingularityDetection:
    """Verify that poles and singularities inside domain are trapped."""

    def test_internal_singularity_detection(self):
        """An expression with a pole at x=2 inside domain [0.1, 5.0] must be flagged."""
        cand_eq = "1.0 / (x - 2.0)"
        true_eq = "x"
        vars = ["x"]
        grid = np.linspace(0.1, 5.0, 50).reshape(-1, 1)

        result = classify_equation_recovery(
            cand_expr_str=cand_eq,
            true_expr_str=true_eq,
            variable_names=vars,
            test_points=grid,
            rollout_rmse=0.1,
        )

        assert result.status in [
            RecoveryClass.INVALID_EXPRESSION,
            RecoveryClass.INCORRECT,
            RecoveryClass.APPROXIMATE_VECTOR_FIELD,
            RecoveryClass.ROLLOUT_ONLY_MATCH,
        ]
        assert not result.is_exact_or_equivalent


class TestSearchDeterminism:
    """Verify deterministic repeatability across random seeds."""

    def test_pure_beam_determinism(self):
        """PureBeam on harmonic oscillator must produce identical equations with seed 42."""
        system = HarmonicOscillator()
        t_eval = np.linspace(0, 10, 200)
        sim = simulate_system(system, x0=np.array([1.0, 0.0]), t_span=(0, 10), t_eval=t_eval)
        traj = Trajectory(id="t1", t=sim.t, x=sim.x, x_dot_true=sim.x_dot_true)
        dataset = TrajectoryDataset(system_name="harmonic_oscillator", variable_names=["x", "v"], trajectories=[traj])

        cfg1 = M2DiscoveryConfig(search_strategy="beam", enable_neural_guidance=False, seed=42)
        engine1 = M2DiscoveryEngine(cfg1)
        res1 = engine1.fit(dataset)

        cfg2 = M2DiscoveryConfig(search_strategy="beam", enable_neural_guidance=False, seed=42)
        engine2 = M2DiscoveryEngine(cfg2)
        res2 = engine2.fit(dataset)

        assert res1.discovered_equations == res2.discovered_equations, "Search must be 100% deterministic under identical seeds!"
