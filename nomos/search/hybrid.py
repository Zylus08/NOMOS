"""
NOMOS Neural-Guided Hybrid Search Engine
Milestone M2 — Phase 5 Neural Guidance Integration
Agents D11 & D15
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from nomos.symbolic.trees import ExpressionTree
from nomos.search.beam import StructuredBeamSearch
from nomos.search.genetic import GeneticProgrammingSearch
from nomos.search.pareto import ParetoFrontier, CandidateLaw
from nomos.neural.surrogate import NeuralDynamicsSurrogate
from nomos.neural.guidance import NeuralGuidanceEngine, GuidanceProfile


class NeuralGuidedSearch:
    """
    Hybrid discovery engine combining Neural Dynamics Surrogate with symbolic search.
    Architecture:
        Observations -> Neural Surrogate -> Jacobian Guidance -> Prioritized Symbolic Search -> Continuous Refit
    Supports fair evaluation budget tracking and unguided ablation comparison.
    """

    def __init__(
        self,
        variable_names: List[str],
        base_search_method: str = "beam",  # 'beam' or 'genetic'
        max_evals: int = 1200,
        enable_guidance: bool = True,
        seed: int = 42,
    ):
        self.variable_names = list(variable_names)
        self.base_search_method = base_search_method
        self.max_evals = max_evals
        self.enable_guidance = enable_guidance
        self.seed = seed

        self.surrogate: Optional[NeuralDynamicsSurrogate] = None
        self.guidance_profile: Optional[GuidanceProfile] = None
        self.total_evals = 0

    def set_surrogate(self, surrogate: NeuralDynamicsSurrogate):
        self.surrogate = surrogate

    def search(
        self,
        X: np.ndarray,
        y: np.ndarray,
        target_dim: int = 0,
    ) -> Tuple[ParetoFrontier, Dict[str, Any]]:
        """
        Execute symbolic search for state variable target_dim.
        """
        guidance_priorities = None

        if self.enable_guidance and self.surrogate is not None:
            engine = NeuralGuidanceEngine(self.surrogate, self.variable_names)
            self.guidance_profile = engine.extract_guidance(X, target_dim=target_dim)
            guidance_priorities = self.guidance_profile.state_importance

        # Instantiate base search engine with equalized evaluation budgets
        if self.base_search_method == "beam":
            searcher = StructuredBeamSearch(
                variable_names=self.variable_names,
                beam_width=20 if self.enable_guidance else 15,
                max_depth=3,
                max_evals=self.max_evals,
                enable_trig=True,
                enable_rational=True,
            )
            pareto = searcher.search(X, y, guidance_priorities=guidance_priorities)
            self.total_evals = searcher.total_evals
        elif self.base_search_method == "genetic":
            searcher = GeneticProgrammingSearch(
                variable_names=self.variable_names,
                population_size=30,
                generations=15,
                max_depth=3,
                max_evals=self.max_evals,
                seed=self.seed,
            )
            pareto = searcher.search(X, y, neural_guidance_probs=guidance_priorities)
            self.total_evals = searcher.total_evals
        else:
            raise ValueError(f"Unknown base search method: {self.base_search_method}")

        metadata = {
            "method": f"neural_guided_{self.base_search_method}" if self.enable_guidance else f"pure_{self.base_search_method}",
            "guidance_enabled": self.enable_guidance,
            "total_candidate_evaluations": self.total_evals,
            "recommended_primitives": self.guidance_profile.recommended_primitives if self.guidance_profile else [],
        }
        return pareto, metadata
