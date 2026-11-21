"""
NOMOS Multi-Objective Pareto Frontier Archive
Milestone M2 — Phase 6 Pareto Optimization
Agents A06, D14
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from nomos.symbolic.trees import ExpressionTree


@dataclass
class CandidateLaw:
    tree: ExpressionTree
    mse: float
    complexity: float
    rollout_rmse: float = float("inf")
    latex_str: str = ""
    is_stable: bool = True

    def dominates(self, other: "CandidateLaw") -> bool:
        """
        Pareto dominance: self dominates other if:
        1. self is <= other in all objectives (MSE, complexity)
        2. self is strictly < other in at least one objective
        """
        better_or_equal = (self.mse <= other.mse) and (self.complexity <= other.complexity)
        strictly_better = (self.mse < other.mse) or (self.complexity < other.complexity)
        return better_or_equal and strictly_better


class ParetoFrontier:
    """
    Maintains non-dominated Pareto frontier of candidate mathematical laws.
    """

    def __init__(self, max_capacity: int = 50):
        self.candidates: List[CandidateLaw] = []
        self.max_capacity = max_capacity

    def add(self, candidate: CandidateLaw):
        # Check if dominated by existing member
        for existing in self.candidates:
            if existing.dominates(candidate):
                return  # Suboptimal, reject

        # Remove existing members dominated by candidate
        self.candidates = [ex for ex in self.candidates if not candidate.dominates(ex)]
        self.candidates.append(candidate)

        # Sort by complexity ascending
        self.candidates.sort(key=lambda c: (c.complexity, c.mse))

        # Enforce max capacity
        if len(self.candidates) > self.max_capacity:
            self.candidates = self.candidates[: self.max_capacity]

    def get_best(self, complexity_weight: float = 0.01) -> CandidateLaw:
        """Select law minimizing combined score = MSE + complexity_weight * Complexity."""
        if not self.candidates:
            raise RuntimeError("Pareto frontier is empty")
        return min(self.candidates, key=lambda c: c.mse + complexity_weight * c.complexity)

    def to_summary(self) -> List[Dict[str, Any]]:
        return [
            {
                "expression": c.tree.to_string(),
                "mse": float(c.mse),
                "complexity": float(c.complexity),
                "rollout_rmse": float(c.rollout_rmse),
                "is_stable": c.is_stable,
            }
            for c in self.candidates
        ]
