"""
NOMOS Evolutionary Symbolic Regression Engine (Genetic Programming)
Milestone M2 — Phase 3 Strategy A
Agents D03, D04, E05
"""

import copy
from typing import Dict, List, Optional, Tuple
import numpy as np

from nomos.symbolic.primitives import NodeType
from nomos.symbolic.trees import ExpressionNode, ExpressionTree
from nomos.search.optimizer import optimize_coefficients
from nomos.search.pareto import CandidateLaw, ParetoFrontier


class GeneticProgrammingSearch:
    """
    Original Genetic Programming engine for open-ended symbolic regression.
    Features:
    - Ramped half-and-half tree generation
    - Tournament selection & elitism
    - Subtree mutation & point mutation
    - Subtree crossover
    - Parsimony bloat control
    - Continuous parameter optimization
    - Pareto archive tracking
    """

    def __init__(
        self,
        variable_names: List[str],
        population_size: int = 50,
        generations: int = 25,
        tournament_size: int = 4,
        crossover_prob: float = 0.7,
        mutation_prob: float = 0.3,
        parsimony_weight: float = 0.005,
        max_depth: int = 4,
        max_evals: int = 1500,
        enable_trig: bool = True,
        enable_rational: bool = True,
        seed: int = 42,
    ):
        self.variable_names = list(variable_names)
        self.population_size = population_size
        self.generations = generations
        self.tournament_size = tournament_size
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.parsimony_weight = parsimony_weight
        self.max_depth = max_depth
        self.max_evals = max_evals
        self.enable_trig = enable_trig
        self.enable_rational = enable_rational
        self.seed = seed

        self.rng = np.random.default_rng(seed)
        self.pareto = ParetoFrontier()
        self.total_evals = 0

    def _random_terminal(self) -> ExpressionNode:
        if self.rng.random() < 0.6:
            vname = self.rng.choice(self.variable_names)
            return ExpressionNode(NodeType.VARIABLE, name=vname)
        else:
            c_val = float(self.rng.uniform(-2.0, 2.0))
            return ExpressionNode(NodeType.CONSTANT, value=c_val)

    def _random_operator(self) -> NodeType:
        ops = [NodeType.ADD, NodeType.SUB, NodeType.MUL, NodeType.NEG]
        if self.enable_trig:
            ops.extend([NodeType.SIN, NodeType.COS])
        if self.enable_rational:
            ops.append(NodeType.DIV)
        return self.rng.choice(ops)

    def _generate_random_tree(self, max_depth: int, method: str = "grow") -> ExpressionNode:
        """Generate random expression tree via 'full' or 'grow' methods."""
        if max_depth <= 1:
            return self._random_terminal()

        if method == "grow" and self.rng.random() < 0.4:
            return self._random_terminal()

        op = self._random_operator()
        # Unary operators
        if op in (NodeType.NEG, NodeType.SIN, NodeType.COS, NodeType.EXP, NodeType.LOG, NodeType.ABS, NodeType.SQRT):
            child = self._generate_random_tree(max_depth - 1, method)
            return ExpressionNode(op, children=[child])
        else:
            # Binary operators
            left = self._generate_random_tree(max_depth - 1, method)
            right = self._generate_random_tree(max_depth - 1, method)
            return ExpressionNode(op, children=[left, right])

    def _init_population(self) -> List[ExpressionTree]:
        """Ramped half-and-half initialization."""
        pop = []
        depths = list(range(2, self.max_depth + 1))
        for i in range(self.population_size):
            depth = depths[i % len(depths)]
            method = "full" if (i % 2 == 0) else "grow"
            root = self._generate_random_tree(depth, method)
            pop.append(ExpressionTree(root, self.variable_names))
        return pop

    def _fitness(self, tree: ExpressionTree, X: np.ndarray, y_flat: np.ndarray) -> float:
        self.total_evals += 1
        try:
            pred = tree.evaluate(X).ravel()
            if not np.all(np.isfinite(pred)):
                return 1e10
            mse = float(np.mean((y_flat - pred) ** 2))
            comp = tree.complexity()
            return mse + self.parsimony_weight * comp
        except Exception:
            return 1e10

    def _tournament(self, population: List[ExpressionTree], fitnesses: List[float]) -> ExpressionTree:
        cand_indices = self.rng.choice(len(population), size=self.tournament_size, replace=False)
        best_idx = min(cand_indices, key=lambda idx: fitnesses[idx])
        return population[best_idx].copy()

    def _mutate(self, tree: ExpressionTree) -> ExpressionTree:
        new_tree = tree.copy()
        # Collect all nodes
        nodes = []
        def collect(node: ExpressionNode):
            nodes.append(node)
            for c in node.children:
                collect(c)
        collect(new_tree.root)

        target = self.rng.choice(nodes)
        if target.node_type == NodeType.CONSTANT:
            target.value += float(self.rng.normal(0, 0.2))
        else:
            sub = self._generate_random_tree(max_depth=2, method="grow")
            target.node_type = sub.node_type
            target.name = sub.name
            target.value = sub.value
            target.children = sub.children
        return new_tree

    def _crossover(self, p1: ExpressionTree, p2: ExpressionTree) -> ExpressionTree:
        child = p1.copy()
        # Find nodes in child
        c_nodes = []
        def collect(node: ExpressionNode):
            c_nodes.append(node)
            for c in node.children:
                collect(c)
        collect(child.root)

        p2_nodes = []
        def collect2(node: ExpressionNode):
            p2_nodes.append(node)
            for c in node.children:
                collect2(c)
        collect2(p2.root)

        target = self.rng.choice(c_nodes)
        donor = self.rng.choice(p2_nodes).copy()

        target.node_type = donor.node_type
        target.name = donor.name
        target.value = donor.value
        target.children = donor.children
        return child

    def search(
        self,
        X: np.ndarray,
        y: np.ndarray,
        neural_guidance_probs: Optional[Dict[str, float]] = None,
    ) -> ParetoFrontier:
        """
        Run evolutionary symbolic regression.
        neural_guidance_probs: optional operator / variable probabilities.
        """
        self.total_evals = 0
        y_flat = y.ravel()
        population = self._init_population()

        for gen in range(self.generations):
            if self.total_evals >= self.max_evals:
                break

            fitnesses = [self._fitness(t, X, y_flat) for t in population]

            # Update Pareto frontier with top individuals of this generation
            sorted_indices = np.argsort(fitnesses)
            for idx in sorted_indices[:5]:
                t = population[idx]
                if t.max_depth() <= self.max_depth + 1:
                    opt_t, loss = optimize_coefficients(t, X, y_flat, max_iter=20)
                    law = CandidateLaw(
                        tree=opt_t,
                        mse=loss,
                        complexity=opt_t.complexity(),
                        is_stable=True,
                    )
                    self.pareto.add(law)

            # Elitism: carry over top 2
            next_pop = [population[sorted_indices[0]].copy(), population[sorted_indices[1]].copy()]

            while len(next_pop) < self.population_size:
                p1 = self._tournament(population, fitnesses)
                if self.rng.random() < self.crossover_prob:
                    p2 = self._tournament(population, fitnesses)
                    child = self._crossover(p1, p2)
                else:
                    child = p1.copy()

                if self.rng.random() < self.mutation_prob:
                    child = self._mutate(child)

                if child.max_depth() <= self.max_depth + 2:
                    next_pop.append(child)
                else:
                    next_pop.append(p1)

            population = next_pop

        return self.pareto
