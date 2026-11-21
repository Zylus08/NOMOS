"""
NOMOS M2 Identifiability, Uncertainty & Adversarial Tests
Milestone M2 — Phase 13 Testing & Review
Agents A07, G06, G07, G08, G09
"""

import numpy as np
import pytest

from nomos.symbolic.primitives import NodeType
from nomos.symbolic.trees import ExpressionNode, ExpressionTree
from nomos.search.pareto import CandidateLaw, ParetoFrontier
from nomos.evaluation.identifiability import (
    check_trajectory_excitation,
    audit_identifiability,
    IdentifiabilityStatus,
)


def test_insufficient_excitation_detector():
    # Trajectory stuck at fixed point (x=0, v=0)
    X_flat = np.zeros((100, 2))
    y = np.zeros((100, 1))

    frontier = ParetoFrontier()
    tree = ExpressionTree(ExpressionNode(NodeType.CONSTANT, value=0.0), ["x", "v"])
    frontier.add(CandidateLaw(tree=tree, mse=0.0, complexity=1.0))

    report = audit_identifiability(X_flat, y, frontier)
    assert report.status == IdentifiabilityStatus.INSUFFICIENT_EVIDENCE
    assert not report.is_sufficiently_excited


def test_multiple_plausible_laws_detector():
    # Create two distinct laws with nearly identical MSE
    X = np.linspace(0.1, 1.0, 50)[:, np.newaxis]
    y = 2.0 * X.ravel()

    frontier = ParetoFrontier()
    t1 = ExpressionTree(ExpressionNode(NodeType.VARIABLE, name="x"), ["x"])
    t2 = ExpressionTree(
        ExpressionNode(
            NodeType.ADD,
            children=[
                ExpressionNode(NodeType.VARIABLE, name="x"),
                ExpressionNode(NodeType.CONSTANT, value=0.001),
            ],
        ),
        ["x"],
    )

    frontier.add(CandidateLaw(tree=t1, mse=0.0102, complexity=2.0))
    frontier.add(CandidateLaw(tree=t2, mse=0.0100, complexity=4.0))

    report = audit_identifiability(X, y, frontier, mse_tolerance_ratio=1.10)
    assert report.status == IdentifiabilityStatus.MULTIPLE_PLAUSIBLE_LAWS
    assert len(report.alternative_equations) >= 1
