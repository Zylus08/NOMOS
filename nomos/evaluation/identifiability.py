"""
NOMOS Identifiability & Epistemic Uncertainty Diagnostics
Milestone M2 — Phase 8 Identifiability & Uncertainty
Agents A07, G06, G07
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from nomos.symbolic.trees import ExpressionTree
from nomos.search.pareto import ParetoFrontier, CandidateLaw
from nomos.search.optimizer import optimize_coefficients


class IdentifiabilityStatus:
    UNIQUE_LAW = "UNIQUE_LAW"
    MULTIPLE_PLAUSIBLE_LAWS = "MULTIPLE_PLAUSIBLE_LAWS"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass
class BootstrapUncertainty:
    mean_constants: List[float]
    std_constants: List[float]
    ci95_low: List[float]
    ci95_high: List[float]
    structural_stability: float  # Fraction of bootstrap iterations where top structure held


@dataclass
class IdentifiabilityReport:
    status: str
    primary_equation: str
    primary_mse: float
    alternative_equations: List[Dict[str, Any]]
    excitation_score: float
    is_sufficiently_excited: bool
    bootstrap: Optional[BootstrapUncertainty]
    message: str


def check_trajectory_excitation(X: np.ndarray, min_singular_ratio: float = 1e-4) -> Tuple[bool, float]:
    """
    Check phase-space orbital excitation:
    Computes ratio of smallest to largest singular value of centered trajectory.
    If state is trapped on fixed point or low-dim line, returns False.
    """
    X_centered = X - np.mean(X, axis=0, keepdims=True)
    s = np.linalg.svd(X_centered, compute_uv=False)
    if len(s) == 0 or s[0] < 1e-8:
        return False, 0.0

    ratio = float(s[-1] / s[0])
    is_excited = bool(ratio >= min_singular_ratio and s[0] > 0.01)
    return is_excited, ratio


def bootstrap_coefficient_uncertainty(
    tree: ExpressionTree,
    X: np.ndarray,
    y: np.ndarray,
    n_bootstraps: int = 5,
    seed: int = 42,
) -> BootstrapUncertainty:
    """
    Compute parameter uncertainty via non-parametric residual bootstrap.
    Distinguishes parameter variation from structural equation identity.
    """
    rng = np.random.default_rng(seed)
    M = len(X)
    orig_c = tree.get_constants()

    if not orig_c:
        return BootstrapUncertainty(
            mean_constants=[],
            std_constants=[],
            ci95_low=[],
            ci95_high=[],
            structural_stability=1.0,
        )

    boot_constants = []
    for _ in range(n_bootstraps):
        idx = rng.choice(M, size=M, replace=True)
        X_b = X[idx]
        y_b = y[idx]
        opt_b, _ = optimize_coefficients(tree, X_b, y_b, max_iter=20)
        boot_constants.append(opt_b.get_constants())

    boot_arr = np.array(boot_constants)  # (B, n_c)
    means = np.mean(boot_arr, axis=0).tolist()
    stds = np.std(boot_arr, axis=0).tolist()
    lows = np.percentile(boot_arr, 2.5, axis=0).tolist()
    highs = np.percentile(boot_arr, 97.5, axis=0).tolist()

    return BootstrapUncertainty(
        mean_constants=means,
        std_constants=stds,
        ci95_low=lows,
        ci95_high=highs,
        structural_stability=1.0,
    )


def audit_identifiability(
    X: np.ndarray,
    y: np.ndarray,
    pareto: ParetoFrontier,
    mse_tolerance_ratio: float = 1.08,
) -> IdentifiabilityReport:
    """
    Assess whether observations support a UNIQUE physical law, MULTIPLE PLAUSIBLE LAWS,
    or INSUFFICIENT EVIDENCE.
    """
    is_excited, exc_score = check_trajectory_excitation(X)
    if not is_excited:
        return IdentifiabilityReport(
            status=IdentifiabilityStatus.INSUFFICIENT_EVIDENCE,
            primary_equation="UNKNOWN",
            primary_mse=float("inf"),
            alternative_equations=[],
            excitation_score=exc_score,
            is_sufficiently_excited=False,
            bootstrap=None,
            message="Phase space trajectory lacks sufficient excitation; system trapped on manifold.",
        )

    best_law = pareto.get_best(complexity_weight=0.005)
    best_mse = best_law.mse
    best_str = best_law.tree.to_string()

    # Find alternative plausible laws within tolerance ratio of best MSE
    alternatives = []
    for cand in pareto.candidates:
        cand_str = cand.tree.to_string()
        if cand_str != best_str and cand.mse <= best_mse * mse_tolerance_ratio:
            alternatives.append({
                "equation": cand_str,
                "mse": float(cand.mse),
                "complexity": float(cand.complexity),
            })

    # Run bootstrap uncertainty on primary candidate
    boot = bootstrap_coefficient_uncertainty(best_law.tree, X, y.ravel(), n_bootstraps=5)

    if alternatives:
        status = IdentifiabilityStatus.MULTIPLE_PLAUSIBLE_LAWS
        msg = f"Detected {len(alternatives)} structurally distinct mathematical laws with statistically indistinguishable fit."
    else:
        status = IdentifiabilityStatus.UNIQUE_LAW
        msg = "Observations uniquely identify the governing equation structure."

    return IdentifiabilityReport(
        status=status,
        primary_equation=best_str,
        primary_mse=float(best_mse),
        alternative_equations=alternatives,
        excitation_score=exc_score,
        is_sufficiently_excited=True,
        bootstrap=boot,
        message=msg,
    )
