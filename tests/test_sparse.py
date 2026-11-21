"""
NOMOS Sparse Optimization & Edge Case Tests
Agents G02, G06, D01, D02, D03, D05, D06
"""

import numpy as np
import pytest
from nomos.sparse import STLSQ, ridge_solve, active_set_refit, compute_information_criteria


def test_stlsq_exact_sparse_recovery():
    rng = np.random.default_rng(42)
    M = 200
    P = 10
    n = 2

    # Orthogonal or well-conditioned candidate library
    Theta = rng.normal(0, 1, size=(M, P))
    # True sparse coefficient matrix: only columns 1 and 3 active
    Xi_true = np.zeros((P, n))
    Xi_true[1, 0] = 3.0
    Xi_true[4, 0] = -2.5
    Xi_true[2, 1] = 1.8
    Xi_true[7, 1] = -4.0

    X_dot = Theta @ Xi_true

    opt = STLSQ(threshold=0.5, alpha=1e-6, normalize_columns=True, refit_active_set=True)
    res = opt.fit(Theta, X_dot)

    assert res.converged
    np.testing.assert_array_equal(res.support, Xi_true != 0.0)
    np.testing.assert_allclose(res.coef, Xi_true, atol=1e-5)


def test_stlsq_rank_deficient_handling():
    rng = np.random.default_rng(42)
    M = 100
    # Duplicate columns (col 2 is identical to col 1)
    col = rng.normal(0, 1, size=(M, 1))
    Theta = np.column_stack([col, col, rng.normal(0, 1, size=(M, 3))])
    y = 2.0 * col

    # Must solve without raising LinAlgError
    Xi, cond = ridge_solve(Theta, y, alpha=1e-4)
    assert np.all(np.isfinite(Xi))


def test_stlsq_overly_high_threshold():
    # If threshold is higher than all coefficients, returns zero matrix gracefully
    Theta = np.eye(5)
    X_dot = np.ones((5, 1)) * 0.01

    opt = STLSQ(threshold=1.0)
    res = opt.fit(Theta, X_dot)
    assert not np.any(res.support)
    np.testing.assert_allclose(res.coef, 0.0)
