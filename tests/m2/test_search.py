"""
NOMOS M2 Search Algorithms & Optimizer Tests
Milestone M2 — Phase 13 Testing & Review
Agents D03, D05, D12, D14, G01, G03
"""

import numpy as np
import pytest

from nomos.symbolic.primitives import NodeType
from nomos.symbolic.trees import ExpressionNode, ExpressionTree
from nomos.search.optimizer import optimize_coefficients
from nomos.search.pareto import CandidateLaw, ParetoFrontier
from nomos.search.beam import StructuredBeamSearch
from nomos.search.genetic import GeneticProgrammingSearch


def test_continuous_coefficient_optimization():
    # Target: y = 3.5 * x - 2.1
    x = np.linspace(-2.0, 2.0, 50)[:, np.newaxis]
    y_true = 3.5 * x.ravel() - 2.1

    # Initial tree with wrong constants: 1.0 * x + 0.0
    c1 = ExpressionNode(NodeType.CONSTANT, value=1.0)
    x_node = ExpressionNode(NodeType.VARIABLE, name="x")
    mul_node = ExpressionNode(NodeType.MUL, children=[c1, x_node])
    c2 = ExpressionNode(NodeType.CONSTANT, value=0.0)
    add_node = ExpressionNode(NodeType.ADD, children=[mul_node, c2])

    tree = ExpressionTree(add_node, ["x"])
    opt_tree, loss = optimize_coefficients(tree, x, y_true, max_iter=40)

    constants = opt_tree.get_constants()
    assert len(constants) == 2
    assert loss < 1e-4, f"Optimization loss {loss} too high"
    np.testing.assert_allclose(constants, [3.5, -2.1], atol=1e-2)


def test_pareto_frontier_dominance():
    frontier = ParetoFrontier(max_capacity=10)
    t1 = ExpressionTree(ExpressionNode(NodeType.CONSTANT, value=1.0), ["x"])
    t2 = ExpressionTree(ExpressionNode(NodeType.CONSTANT, value=2.0), ["x"])

    # c1 is accurate but complex
    c1 = CandidateLaw(tree=t1, mse=0.01, complexity=10.0)
    # c2 is inaccurate and complex (dominated by c1)
    c2 = CandidateLaw(tree=t2, mse=0.05, complexity=12.0)
    # c3 is less accurate but very simple (Pareto non-dominated)
    c3 = CandidateLaw(tree=t1, mse=0.08, complexity=2.0)

    frontier.add(c1)
    frontier.add(c2)
    frontier.add(c3)

    assert len(frontier.candidates) == 2  # c2 should have been rejected/pruned
    assert c1 in frontier.candidates
    assert c3 in frontier.candidates


def test_structured_beam_search_recovery():
    # Target: y = -1.0 * x
    X = np.linspace(-3.0, 3.0, 60)[:, np.newaxis]
    y = -1.0 * X.ravel()

    searcher = StructuredBeamSearch(
        variable_names=["x"],
        beam_width=15,
        max_depth=3,
        max_evals=250,
        enable_trig=False,
    )
    pareto = searcher.search(X, y)
    best = pareto.get_best(complexity_weight=0.005)
    pred = best.tree.evaluate(X).ravel()
    mse = np.mean((y - pred) ** 2)
    assert mse < 1e-4, f"Beam search failed to recover linear law: MSE={mse}"


def test_genetic_programming_search():
    # Target: y = 2.0 * x
    X = np.linspace(-2.0, 2.0, 50)[:, np.newaxis]
    y = 2.0 * X.ravel()

    gp = GeneticProgrammingSearch(
        variable_names=["x"],
        population_size=30,
        generations=15,
        max_depth=3,
        max_evals=300,
        seed=123,
    )
    pareto = gp.search(X, y)
    best = pareto.get_best(complexity_weight=0.005)
    pred = best.tree.evaluate(X).ravel()
    mse = np.mean((y - pred) ** 2)
    assert mse < 0.1, f"GP search error {mse} exceeds threshold"
