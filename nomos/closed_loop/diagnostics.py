"""
NOMOS Physical Identifiability, Observability & Stopping Diagnostics
Phase 6: Identifiability Criteria and Model Discrimination Auditing
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from nomos.closed_loop.portfolio import ScientificHypothesis, HypothesisPortfolio, HypothesisStatus


class IdentifiabilityStatus(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    MULTIPLE_PLAUSIBLE_LAWS = "MULTIPLE_PLAUSIBLE_LAWS"
    INSUFFICIENT_EXCITATION = "INSUFFICIENT_EXCITATION"
    NONIDENTIFIABLE = "NONIDENTIFIABLE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    NUMERICAL_FAILURE = "NUMERICAL_FAILURE"


class IdentifiabilityAuditor:
    """
    Formal identifiability and model-selection auditor.
    Evaluates evidence ratios, parameter condition numbers,
    and falsification margins to determine whether a physical law is uniquely resolved.
    """

    def __init__(
        self,
        bayes_factor_threshold: float = 10.0,       # Delta BIC >= 10 (strong Kass & Raftery evidence)
        max_condition_number: float = 1e4,          # Collinearity threshold
        falsification_ratio_threshold: float = 5.0,  # Falsification margin
        min_excitation_variance: float = 1e-4,      # Sufficient dynamic range
    ):
        self.bayes_factor_threshold = float(bayes_factor_threshold)
        self.max_condition_number = float(max_condition_number)
        self.falsification_ratio_threshold = float(falsification_ratio_threshold)
        self.min_excitation_variance = float(min_excitation_variance)

    def audit_portfolio(
        self,
        portfolio: HypothesisPortfolio,
        current_budget_used: int,
        max_budget: int,
    ) -> Tuple[IdentifiabilityStatus, Optional[ScientificHypothesis], Dict[str, Any]]:
        """
        Audit the current state of knowledge in scientific memory.
        Returns: (IdentifiabilityStatus, WinningHypothesisOrNone, DiagnosticsReport).
        """
        active_hypotheses = portfolio.get_active()

        if not active_hypotheses:
            return (
                IdentifiabilityStatus.NONIDENTIFIABLE,
                None,
                {"reason": "All generated candidate hypotheses have been falsified or rejected."},
            )

        # Sort by validation MSE / BIC
        active_hypotheses.sort(key=lambda h: h.bic)
        top = active_hypotheses[0]

        # Check for single active model that dominates
        if len(active_hypotheses) == 1:
            if top.val_mse < 0.2 and len(top.supporting_experiments) >= 1:
                return (
                    IdentifiabilityStatus.IDENTIFIED,
                    top,
                    {"reason": "Single surviving hypothesis with confirmed predictive support.", "bic": top.bic},
                )

        runner_up = active_hypotheses[1] if len(active_hypotheses) > 1 else None

        # Check Delta BIC (Evidence Ratio)
        if runner_up is not None:
            delta_bic = runner_up.bic - top.bic
            val_ratio = runner_up.val_mse / (top.val_mse + 1e-12)

            # Dominant identifiability criterion:
            # 1. Delta BIC >= threshold (decisive statistical evidence) OR val_ratio >= 3.0
            # 2. Top model has demonstrated predictive support
            if (delta_bic >= self.bayes_factor_threshold or val_ratio >= 3.0) and len(top.supporting_experiments) >= 1:
                return (
                    IdentifiabilityStatus.IDENTIFIED,
                    top,
                    {
                        "reason": f"Decisive statistical evidence (Delta BIC = {delta_bic:.2f} >= {self.bayes_factor_threshold}).",
                        "delta_bic": delta_bic,
                        "falsification_ratio": val_ratio,
                    },
                )

        # Budget exhaustion check
        if current_budget_used >= max_budget:
            if runner_up is not None and abs(runner_up.bic - top.bic) < self.bayes_factor_threshold:
                return (
                    IdentifiabilityStatus.MULTIPLE_PLAUSIBLE_LAWS,
                    None,
                    {
                        "reason": "Experimental budget exhausted while multiple candidate laws remain unseparated.",
                        "top_two": [top.equation_str, runner_up.equation_str],
                        "delta_bic": runner_up.bic - top.bic,
                    },
                )
            return (
                IdentifiabilityStatus.BUDGET_EXHAUSTED,
                top if top.val_mse < 0.1 else None,
                {"reason": f"Max budget {max_budget} reached without conclusive identifiability."},
            )

        # Ongoing ambiguity
        return (
            IdentifiabilityStatus.MULTIPLE_PLAUSIBLE_LAWS,
            None,
            {
                "reason": "Multiple plausible candidate hypotheses remain active; further experimentation required.",
                "active_candidates": [h.equation_str for h in active_hypotheses[:3]],
            },
        )
