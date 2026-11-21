"""
NOMOS Symbolic Mathematics Tests
Agents E02, E03, E05, E06, E07, E08
"""

import numpy as np
import pytest
import sympy as sp
from nomos.symbolic import (
    matrix_to_sympy_system,
    simplify_and_format_equation,
    check_algebraic_equivalence,
    compute_equation_complexity,
    DimensionalConsistencyChecker,
)


def test_matrix_to_sympy():
    Xi = np.array([[0.0, -1.0], [1.0, 0.0]])
    feat_names = ["x", "v"]
    var_names = ["x", "v"]

    sym_sys = matrix_to_sympy_system(Xi, feat_names, var_names)
    assert "x" in sym_sys and "v" in sym_sys
    assert str(sym_sys["x"]) == "1.0*v"
    assert str(sym_sys["v"]) == "-1.0*x"


def test_algebraic_equivalence_exact():
    x, y = sp.symbols("x y")
    expr1 = 2.0 * x + 3.0 * y
    expr2 = 2.0 * x + 3.0 * y
    is_eq, res = check_algebraic_equivalence(expr1, expr2)
    assert is_eq
    assert res == 0.0


def test_algebraic_equivalence_factored():
    x, y = sp.symbols("x y")
    expr1 = x * (1.5 - y)
    expr2 = 1.5 * x - x * y
    is_eq, res = check_algebraic_equivalence(expr1, expr2)
    assert is_eq
    assert res < 1e-10


def test_complexity_monotonicity():
    x = sp.Symbol("x")
    simple_expr = x
    complex_expr = x ** 3 + 2.0 * sp.sin(x) + 4.0 * x
    c_simple = compute_equation_complexity(simple_expr)
    c_complex = compute_equation_complexity(complex_expr)
    assert c_complex > c_simple


def test_dimensional_consistency():
    checker = DimensionalConsistencyChecker(
        variable_dimensions={"x": {"L": 1}, "v": {"L": 1, "T": -1}}
    )
    x, v = sp.symbols("x v")
    # Both terms in dx/dt must have L*T^-1
    consistent_expr = v  # [L/T]
    assert checker.check_expression(consistent_expr)
