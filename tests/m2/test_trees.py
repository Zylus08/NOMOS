"""
NOMOS M2 Expression Tree & Protected Operators Tests
Milestone M2 — Phase 13 Testing & Review
Agents D01, D02, E01, E07, G01, G02
"""

import numpy as np
import pytest
import sympy as sp

from nomos.symbolic.primitives import (
    NodeType,
    protected_div,
    protected_log,
    protected_exp,
    protected_sqrt,
    protected_pow,
)
from nomos.symbolic.trees import ExpressionNode, ExpressionTree


def test_protected_operators_no_crashes():
    # Division by zero
    zeros = np.zeros(10)
    ones = np.ones(10)
    div_res = protected_div(ones, zeros)
    assert np.all(np.isfinite(div_res)), "Protected div failed on zeros"
    assert np.all(div_res > 0)

    # Log of negative and zero
    negs = np.array([-5.0, 0.0, -1e-12])
    log_res = protected_log(negs)
    assert np.all(np.isfinite(log_res)), "Protected log failed on non-positives"

    # Exp overflow
    huge = np.array([1000.0, 500.0])
    exp_res = protected_exp(huge)
    assert np.all(np.isfinite(exp_res)), "Protected exp overflowed"

    # Sqrt of negative
    sqrt_res = protected_sqrt(np.array([-4.0, -9.0]))
    assert np.all(np.isfinite(sqrt_res))
    np.testing.assert_allclose(sqrt_res, [2.0, 3.0])


def test_expression_tree_construction_and_eval():
    # Construct: 2.5 * x + sin(v)
    x_node = ExpressionNode(NodeType.VARIABLE, name="x")
    c_node = ExpressionNode(NodeType.CONSTANT, value=2.5)
    mul_node = ExpressionNode(NodeType.MUL, children=[c_node, x_node])

    v_node = ExpressionNode(NodeType.VARIABLE, name="v")
    sin_node = ExpressionNode(NodeType.SIN, children=[v_node])

    add_node = ExpressionNode(NodeType.ADD, children=[mul_node, sin_node])
    tree = ExpressionTree(add_node, variable_names=["x", "v"])

    X = np.array([[2.0, 0.0], [4.0, np.pi / 2.0]])
    vals = tree.evaluate(X)

    # Row 0: 2.5 * 2.0 + sin(0) = 5.0
    # Row 1: 2.5 * 4.0 + sin(pi/2) = 10.0 + 1.0 = 11.0
    np.testing.assert_allclose(vals, [5.0, 11.0], atol=1e-7)


def test_expression_tree_sympy_roundtrip():
    # Construct: x * (1.5 - v)
    expr = sp.parse_expr("x * (1.5 - v)")
    tree = ExpressionTree.from_sympy(expr, variable_names=["x", "v"])

    X = np.array([[2.0, 0.5]])
    val_tree = tree.evaluate(X)[0]
    val_sp = float(expr.subs({"x": 2.0, "v": 0.5}))
    assert np.isclose(val_tree, val_sp)

    re_sympy = tree.to_sympy()
    diff = sp.simplify(re_sympy - expr)
    assert diff == 0, f"Roundtrip mismatch: {re_sympy} vs {expr}"


def test_expression_tree_serialization():
    x_node = ExpressionNode(NodeType.VARIABLE, name="theta")
    tree = ExpressionTree(x_node, ["theta"])
    d = tree.to_dict()
    tree_rec = ExpressionTree.from_dict(d)
    assert tree_rec.to_string() == tree.to_string()
