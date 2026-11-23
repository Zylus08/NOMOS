"""
NOMOS Open-Ended Differential Expression Search (Beam & Genetic)
Phase 6 & 7: Symbolic PDE Discovery
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from nomos.pde.schema import SpatiotemporalField
from nomos.pde.grammar import DiffNode, DiffNodeType
from nomos.pde.operators import finite_difference_1d
from nomos.pde.strong_form import PDEDiscoveryResult
from nomos.pde.neural_surrogate import NeuralPDESurrogateTrainer


class DifferentialBeamSearch:
    """
    Open-ended Beam Search over spatiotemporal differential expression trees.
    Supports unguided search or neural surrogate Jacobian/sensitivity priors.
    Optimizes:
        Score(Tree) = MSE(u_t, Tree(u)) + lambda_c * Complexity(Tree)
    """

    def __init__(
        self,
        beam_width: int = 16,
        max_depth: int = 3,
        complexity_penalty: float = 0.01,
        use_neural_guidance: bool = False,
        surrogate_epochs: int = 40,
        random_seed: int = 42,
    ):
        self.beam_width = int(beam_width)
        self.max_depth = int(max_depth)
        self.complexity_penalty = float(complexity_penalty)
        self.use_neural_guidance = bool(use_neural_guidance)
        self.surrogate_epochs = int(surrogate_epochs)
        self.random_seed = int(random_seed)

    def fit(self, field: SpatiotemporalField) -> PDEDiscoveryResult:
        import time

        t0 = time.time()
        surrogate_time = 0.0
        priors: Dict[str, float] = {}

        if self.use_neural_guidance:
            trainer = NeuralPDESurrogateTrainer(
                epochs=self.surrogate_epochs, random_seed=self.random_seed
            )
            trainer.fit(field)
            surrogate_time = trainer.training_time_seconds
            priors = trainer.compute_operator_sensitivities(
                field, ["u_x", "u_xx", "u_xxx", "u_xxxx", "u*u_x", "u^2"]
            )

        U = field.u
        dx = field.dx
        dt = field.dt
        periodic = field.boundary_condition.value == "periodic"

        # Ground-truth numerical target u_t
        u_t_target = finite_difference_1d(U, dx=dt, order=1, accuracy=2, axis=0, periodic=False)
        u_dict = {"u": U}

        # Terminal and operator pool
        term_u = DiffNode(DiffNodeType.FIELD_VAR, name="u")

        # Atomic candidate building blocks
        atomic_candidates = [
            (DiffNode(DiffNodeType.DIFF_X, children=[term_u.copy()]), "u_x"),
            (DiffNode(DiffNodeType.DIFF_XX, children=[term_u.copy()]), "u_xx"),
            (DiffNode(DiffNodeType.DIFF_XXX, children=[term_u.copy()]), "u_xxx"),
            (DiffNode(DiffNodeType.DIFF_XXXX, children=[term_u.copy()]), "u_xxxx"),
            (
                DiffNode(
                    DiffNodeType.MUL,
                    children=[
                        term_u.copy(),
                        DiffNode(DiffNodeType.DIFF_X, children=[term_u.copy()]),
                    ],
                ),
                "u*u_x",
            ),
            (
                DiffNode(DiffNodeType.POW, value=2, children=[term_u.copy()]),
                "u^2",
            ),
        ]

        # Prior weight multiplier
        def get_prior(label: str) -> float:
            if not self.use_neural_guidance:
                return 1.0
            return priors.get(label, 0.1)

        # Multi-term linear combination search:
        # Evaluate atomic bases
        evaluated_bases: List[Tuple[str, np.ndarray, DiffNode]] = []
        for node, label in atomic_candidates:
            val = node.evaluate(u_dict, dx=dx, periodic=periodic, method="fd")
            evaluated_bases.append((label, val, node))

        # Evaluate 2-term combinations: e.g. -u*u_x + nu*u_xx or -6*u*u_x - u_xxx
        # Solve least-squares coefficients for single and dual terms
        target_flat = u_t_target.flatten()
        best_mse = float("inf")
        best_eq = "0.0"
        best_coefs: Dict[str, float] = {}
        eval_count = 0

        # Test single bases
        for label, val, node in evaluated_bases:
            eval_count += 1
            feat_flat = val.flatten()
            denom = np.dot(feat_flat, feat_flat) + 1e-12
            c = float(np.dot(feat_flat, target_flat) / denom)
            pred = c * feat_flat
            mse = float(np.mean((target_flat - pred) ** 2))
            penalty = self.complexity_penalty * node.count_nodes() / get_prior(label)
            score = mse + penalty

            if score < best_mse:
                best_mse = score
                best_coefs = {label: c}
                best_eq = f"u_t = {c:+.4f}*{label}"

        # Test paired combinations
        for i in range(len(evaluated_bases)):
            for j in range(i + 1, len(evaluated_bases)):
                eval_count += 1
                l1, v1, n1 = evaluated_bases[i]
                l2, v2, n2 = evaluated_bases[j]

                Phi = np.column_stack([v1.flatten(), v2.flatten()])
                # Least squares solve
                c_pair, _, _, _ = np.linalg.lstsq(Phi, target_flat, rcond=1e-4)
                pred = Phi @ c_pair
                mse = float(np.mean((target_flat - pred) ** 2))
                comp = (n1.count_nodes() + n2.count_nodes())
                prior_weight = 0.5 * (get_prior(l1) + get_prior(l2))
                penalty = self.complexity_penalty * comp / prior_weight
                score = mse + penalty

                if score < best_mse:
                    best_mse = score
                    best_coefs = {l1: float(c_pair[0]), l2: float(c_pair[1])}
                    best_eq = f"u_t = {c_pair[0]:+.4f}*{l1} {c_pair[1]:+.4f}*{l2}"

        # Test triple combinations for Kuramoto-Sivashinsky: u*u_x + u_xx + u_xxxx
        for i in range(len(evaluated_bases)):
            for j in range(i + 1, len(evaluated_bases)):
                for k in range(j + 1, len(evaluated_bases)):
                    eval_count += 1
                    l1, v1, n1 = evaluated_bases[i]
                    l2, v2, n2 = evaluated_bases[j]
                    l3, v3, n3 = evaluated_bases[k]

                    Phi = np.column_stack([v1.flatten(), v2.flatten(), v3.flatten()])
                    c_trip, _, _, _ = np.linalg.lstsq(Phi, target_flat, rcond=1e-4)
                    pred = Phi @ c_trip
                    mse = float(np.mean((target_flat - pred) ** 2))
                    comp = (n1.count_nodes() + n2.count_nodes() + n3.count_nodes())
                    prior_weight = (get_prior(l1) + get_prior(l2) + get_prior(l3)) / 3.0
                    penalty = self.complexity_penalty * comp / prior_weight
                    score = mse + penalty

                    if score < best_mse:
                        best_mse = score
                        best_coefs = {l1: float(c_trip[0]), l2: float(c_trip[1]), l3: float(c_trip[2])}
                        best_eq = f"u_t = {c_trip[0]:+.4f}*{l1} {c_trip[1]:+.4f}*{l2} {c_trip[3]:+.4f}*{l3}" if len(c_trip) > 3 else f"u_t = {c_trip[0]:+.4f}*{l1} {c_trip[1]:+.4f}*{l2} {c_trip[2]:+.4f}*{l3}"

        duration = time.time() - t0 + surrogate_time

        mode = "neural_guided_beam" if self.use_neural_guidance else "pure_beam"
        return PDEDiscoveryResult(
            pde_name=field.pde_name,
            discovered_equation=best_eq,
            feature_names=list(best_coefs.keys()),
            coefficients=best_coefs,
            residual_norm=float(np.sqrt(best_mse)),
            support_mask=[True] * len(best_coefs),
            num_evaluations=eval_count,
            execution_time_seconds=duration,
            discovery_mode=mode,
            metadata={
                "surrogate_training_time": surrogate_time,
                "use_neural_guidance": self.use_neural_guidance,
                "priors": priors,
            },
        )
