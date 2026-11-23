"""
Unit Tests for NOMOS Scientific Recovery Classifier
Milestone M2.1 — Section 5 Verification
Agents A01, A03, E01, I01
"""

import numpy as np
import pytest
import sympy as sp

from nomos.evaluation.symbolic_classifier import (
    RecoveryClass,
    classify_equation_recovery,
)


def test_classifier_exact_symbolic():
    res = classify_equation_recovery(
        cand_expr_str="v",
        true_expr_str="v",
        variable_names=["x", "v"],
    )
    assert res.status == RecoveryClass.EXACT_SYMBOLIC
    assert res.is_exact_or_equivalent

    res2 = classify_equation_recovery(
        cand_expr_str="-1.0 * x",
        true_expr_str="-x",
        variable_names=["x", "v"],
    )
    assert res2.status == RecoveryClass.EXACT_SYMBOLIC
    assert res2.is_exact_or_equivalent


def test_classifier_algebraically_equivalent():
    # Factored vs expanded
    res = classify_equation_recovery(
        cand_expr_str="x * (1.0 - x)",
        true_expr_str="x - x**2",
        variable_names=["x"],
    )
    assert res.status == RecoveryClass.ALGEBRAICALLY_EQUIVALENT
    assert res.is_exact_or_equivalent

    # Trigonometric identity
    res2 = classify_equation_recovery(
        cand_expr_str="cos(theta)**2 + sin(theta)**2",
        true_expr_str="1.0",
        variable_names=["theta"],
    )
    assert res2.status == RecoveryClass.ALGEBRAICALLY_EQUIVALENT
    assert res2.is_exact_or_equivalent


def test_classifier_correct_support_approximate_coefficients():
    # True: -9.81*sin(theta), Candidate: -9.5*sin(theta) -> error ~3.1% <= 5%
    res = classify_equation_recovery(
        cand_expr_str="-9.5 * sin(theta)",
        true_expr_str="-9.81 * sin(theta)",
        variable_names=["theta", "omega"],
        coef_tol=0.05,
    )
    assert res.status == RecoveryClass.CORRECT_SUPPORT_APPROXIMATE_COEFFICIENTS
    assert not res.is_exact_or_equivalent
    assert res.relative_coefficient_error is not None
    assert res.relative_coefficient_error < 0.05


def test_classifier_approximate_vector_field():
    # Small angle Taylor approximation: -8.125 * theta vs -9.81 * sin(theta) over small angle
    test_pts = np.linspace(-0.6, 0.6, 100)[:, np.newaxis]
    res = classify_equation_recovery(
        cand_expr_str="-8.125 * theta",
        true_expr_str="-9.81 * sin(theta)",
        variable_names=["theta"],
        test_points=test_pts,
        vector_field_tol=0.20,
    )
    assert res.status == RecoveryClass.APPROXIMATE_VECTOR_FIELD
    assert not res.is_exact_or_equivalent


def test_classifier_rational_kinetics_rollout_only_match():
    # Forensic reproduction of M2 rational kinetics claim:
    # True: 2*x/(1+x) - 0.5*x, Cand: 0.5286 / x
    # Over domain [0.1, 5.0], vector field error is large (~60-90%),
    # but rollout RMSE on test trajectory was 0.411.
    pts = np.linspace(0.1, 5.0, 100)[:, np.newaxis]
    res = classify_equation_recovery(
        cand_expr_str="0.5286 / x",
        true_expr_str="2.0 * x / (1.0 + x) - 0.5 * x",
        variable_names=["x"],
        test_points=pts,
        rollout_rmse=0.411,
        rollout_tol=1.0,
    )
    # Must NOT be EXACT or ALGEBRAICALLY_EQUIVALENT
    assert res.status == RecoveryClass.ROLLOUT_ONLY_MATCH
    assert not res.is_exact_or_equivalent


def test_classifier_incorrect():
    res = classify_equation_recovery(
        cand_expr_str="x**3 + 5.0",
        true_expr_str="v",
        variable_names=["x", "v"],
        rollout_rmse=999.0,
    )
    assert res.status == RecoveryClass.INCORRECT
    assert not res.is_exact_or_equivalent


def test_classifier_unidentifiable():
    res = classify_equation_recovery(
        cand_expr_str="v",
        true_expr_str="v",
        variable_names=["x", "v"],
        is_excited=False,
    )
    assert res.status == RecoveryClass.UNIDENTIFIABLE
    assert not res.is_exact_or_equivalent


def test_classifier_invalid_expression():
    # Syntax error
    res_syntax = classify_equation_recovery(
        cand_expr_str="x + * y",
        true_expr_str="x",
        variable_names=["x", "y"],
    )
    assert res_syntax.status == RecoveryClass.INVALID_EXPRESSION

    # Unknown variable
    res_unknown = classify_equation_recovery(
        cand_expr_str="z + 1.0",
        true_expr_str="x",
        variable_names=["x"],
    )
    assert res_unknown.status == RecoveryClass.INVALID_EXPRESSION

    # Singular division at x=1
    singular_pts = np.array([[1.0]])
    res_singular = classify_equation_recovery(
        cand_expr_str="1.0 / (x - 1.0)",
        true_expr_str="x",
        variable_names=["x"],
        test_points=singular_pts,
    )
    assert res_singular.status == RecoveryClass.INVALID_EXPRESSION
