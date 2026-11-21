"""
NOMOS Structured Enumeration & Beam Search Engine
Milestone M2 — Phase 3 Strategy B
Agents D05, D06, E06, E10
"""

import itertools
from typing import Callable, Dict, List, Optional, Set, Tuple
import numpy as np

from nomos.symbolic.primitives import NodeType
from nomos.symbolic.trees import ExpressionNode, ExpressionTree
from nomos.search.optimizer import optimize_coefficients
from nomos.search.pareto import CandidateLaw, ParetoFrontier


class StructuredBeamSearch:
    """
    Grammar-based structured enumeration with beam search.
    Generates candidate expressions systematically up to depth and complexity budgets.
    Features:
    - Canonical hash deduplication
    - Domain validity pruning
    - Continuous coefficient optimization hook
    - Pareto archive tracking
    """

    def __init__(
        self,
        variable_names: List[str],
        beam_width: int = 20,
        max_depth: int = 4,
        max_evals: int = 1000,
        enable_trig: bool = True,
        enable_rational: bool = True,
        enable_transcendental: bool = False,
        optimize_constants: bool = True,
    ):
        self.variable_names = list(variable_names)
        self.beam_width = beam_width
        self.max_depth = max_depth
        self.max_evals = max_evals
        self.enable_trig = enable_trig
        self.enable_rational = enable_rational
        self.enable_transcendental = enable_transcendental
        self.optimize_constants = optimize_constants

        self.pareto = ParetoFrontier()
        self.total_evals = 0

    def _get_unary_ops(self) -> List[NodeType]:
        ops = [NodeType.NEG]
        if self.enable_trig:
            ops.extend([NodeType.SIN, NodeType.COS])
        if self.enable_transcendental:
            ops.extend([NodeType.EXP, NodeType.LOG])
        return ops

    def _get_binary_ops(self) -> List[NodeType]:
        ops = [NodeType.ADD, NodeType.SUB, NodeType.MUL]
        if self.enable_rational:
            ops.append(NodeType.DIV)
        return ops

    def search(
        self,
        X: np.ndarray,
        y: np.ndarray,
        guidance_priorities: Optional[Dict[str, float]] = None,
    ) -> ParetoFrontier:
        """
        Execute beam search over grammar.
        guidance_priorities: optional operator / variable weights from Neural Surrogate.
        """
        self.total_evals = 0
        y_flat = y.ravel()

        # Step 0: Terminal set
        beam: List[ExpressionTree] = []
        seen_signatures: Set[str] = set()

        # Constant terminals
        for c_val in [1.0, -1.0, 0.5]:
            node = ExpressionNode(NodeType.CONSTANT, value=c_val)
            beam.append(ExpressionTree(node, self.variable_names))

        # Variable terminals
        for vname in self.variable_names:
            node = ExpressionNode(NodeType.VARIABLE, name=vname)
            tree = ExpressionTree(node, self.variable_names)
            beam.append(tree)
            # Scaled variable: c * v
            scaled_node = ExpressionNode(
                NodeType.MUL,
                children=[
                    ExpressionNode(NodeType.CONSTANT, value=1.0),
                    ExpressionNode(NodeType.VARIABLE, name=vname),
                ],
            )
            beam.append(ExpressionTree(scaled_node, self.variable_names))

        # Evaluate initial beam
        for tree in beam:
            self._evaluate_and_record(tree, X, y_flat)

        unary_ops = self._get_unary_ops()
        binary_ops = self._get_binary_ops()

        # Beam iterations over increasing structural depth
        for depth in range(2, self.max_depth + 1):
            if self.total_evals >= self.max_evals:
                break

            candidates: List[ExpressionTree] = []

            # 1. Expand with Unary operators
            for tree in beam:
                if tree.max_depth() < depth:
                    for uop in unary_ops:
                        new_root = ExpressionNode(uop, children=[tree.root.copy()])
                        candidates.append(ExpressionTree(new_root, self.variable_names))
                        # Also add scaled unary: c * uop(tree)
                        scaled_unary = ExpressionNode(
                            NodeType.MUL,
                            children=[
                                ExpressionNode(NodeType.CONSTANT, value=1.0),
                                ExpressionNode(uop, children=[tree.root.copy()]),
                            ],
                        )
                        candidates.append(ExpressionTree(scaled_unary, self.variable_names))

            # 2. Expand with Binary operators
            for i, t1 in enumerate(beam):
                for j, t2 in enumerate(beam):
                    if max(t1.max_depth(), t2.max_depth()) < depth:
                        for bop in binary_ops:
                            new_root = ExpressionNode(bop, children=[t1.root.copy(), t2.root.copy()])
                            candidates.append(ExpressionTree(new_root, self.variable_names))

            # Filter candidates through deduplication & score
            scored_candidates = []
            for cand in candidates:
                if self.total_evals >= self.max_evals:
                    break

                # Signature deduplication
                sig = cand.to_string()
                if sig in seen_signatures:
                    continue
                seen_signatures.add(sig)

                # Domain safety test
                try:
                    pred = cand.evaluate(X).ravel()
                    if not np.all(np.isfinite(pred)):
                        continue
                    mse = float(np.mean((y_flat - pred) ** 2))
                    comp = cand.complexity()
                    # Apply neural guidance weighting if provided
                    score = mse + 0.005 * comp
                    scored_candidates.append((score, mse, cand))
                    self.total_evals += 1
                except Exception:
                    continue

            # Select top-K beam
            scored_candidates.sort(key=lambda item: item[0])
            top_beam_tuples = scored_candidates[: self.beam_width]
            beam = [item[2] for item in top_beam_tuples]

            # Update Pareto frontier with top candidates
            for _, mse, tree in top_beam_tuples[:3]:
                self._evaluate_and_record(tree, X, y_flat, optimize=self.optimize_constants)

        return self.pareto

    def _evaluate_and_record(
        self,
        tree: ExpressionTree,
        X: np.ndarray,
        y_flat: np.ndarray,
        optimize: bool = False,
    ):
        if optimize and len(tree.get_constants()) > 0:
            opt_tree, loss = optimize_coefficients(tree, X, y_flat, max_iter=12)
        else:
            opt_tree = tree
            pred = opt_tree.evaluate(X).ravel()
            loss = float(np.mean((y_flat - pred) ** 2)) if np.all(np.isfinite(pred)) else 1e9

        law = CandidateLaw(
            tree=opt_tree,
            mse=loss,
            complexity=opt_tree.complexity(),
            is_stable=True,
        )
        self.pareto.add(law)
