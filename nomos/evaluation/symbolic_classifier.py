"""
NOMOS Scientific Recovery Evaluator & Symbolic Classification System
Milestone M2.1 — Adversarial Verification & Metric Rectification
Agents A01, A03, E01, I01, I02
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import sympy as sp


class RecoveryClass(str, Enum):
    EXACT_SYMBOLIC = "EXACT_SYMBOLIC"
    ALGEBRAICALLY_EQUIVALENT = "ALGEBRAICALLY_EQUIVALENT"
    CORRECT_SUPPORT_APPROXIMATE_COEFFICIENTS = "CORRECT_SUPPORT_APPROXIMATE_COEFFICIENTS"
    APPROXIMATE_VECTOR_FIELD = "APPROXIMATE_VECTOR_FIELD"
    ROLLOUT_ONLY_MATCH = "ROLLOUT_ONLY_MATCH"
    INCORRECT = "INCORRECT"
    UNIDENTIFIABLE = "UNIDENTIFIABLE"
    INVALID_EXPRESSION = "INVALID_EXPRESSION"


@dataclass
class ClassificationResult:
    status: RecoveryClass
    is_exact_or_equivalent: bool
    cand_expr_str: str
    true_expr_str: str
    sympy_cand: Optional[sp.Expr]
    sympy_true: Optional[sp.Expr]
    relative_coefficient_error: Optional[float]
    vector_field_rmse: Optional[float]
    relative_vector_field_error: Optional[float]
    rollout_rmse: Optional[float]
    details: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "is_exact_or_equivalent": self.is_exact_or_equivalent,
            "cand_expr": self.cand_expr_str,
            "true_expr": self.true_expr_str,
            "rel_coef_error": self.relative_coefficient_error,
            "vector_field_rmse": self.vector_field_rmse,
            "rel_vf_error": self.relative_vector_field_error,
            "rollout_rmse": self.rollout_rmse,
            "details": self.details,
        }


def _safe_parse_expr(expr_str: str, symbols_dict: Dict[str, sp.Symbol]) -> Optional[sp.Expr]:
    """Safely parse mathematical expression string into SymPy expression."""
    if not expr_str or not isinstance(expr_str, str):
        return None
    try:
        # Standardize operators
        cleaned = expr_str.strip()
        # Handle python-style or prefix notation if any
        parsed = sp.parse_expr(cleaned, local_dict=symbols_dict)
        return parsed
    except Exception:
        return None


def classify_equation_recovery(
    cand_expr_str: str,
    true_expr_str: str,
    variable_names: List[str],
    domain: Optional[Dict[str, Tuple[float, float]]] = None,
    test_points: Optional[np.ndarray] = None,
    rollout_rmse: Optional[float] = None,
    is_excited: bool = True,
    coef_tol: float = 0.05,
    vector_field_tol: float = 0.15,
    rollout_tol: float = 1.0,
) -> ClassificationResult:
    """
    Rigorously classify equation recovery into one of eight distinct scientific recovery levels.
    Enforces strict mathematical equivalence and prevents heuristic false-positives.
    """
    # 1. Unidentifiable check
    if not is_excited:
        return ClassificationResult(
            status=RecoveryClass.UNIDENTIFIABLE,
            is_exact_or_equivalent=False,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=None,
            sympy_true=None,
            relative_coefficient_error=None,
            vector_field_rmse=None,
            relative_vector_field_error=None,
            rollout_rmse=rollout_rmse,
            details="Phase space trajectory lacks sufficient orbital excitation; system trapped on manifold.",
        )

    # 2. Syntax and Parsing check
    syms = {v: sp.Symbol(v, real=True) for v in variable_names}
    cand_sp = _safe_parse_expr(cand_expr_str, syms)
    true_sp = _safe_parse_expr(true_expr_str, syms)

    if cand_sp is None or true_sp is None:
        return ClassificationResult(
            status=RecoveryClass.INVALID_EXPRESSION,
            is_exact_or_equivalent=False,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=cand_sp,
            sympy_true=true_sp,
            relative_coefficient_error=None,
            vector_field_rmse=None,
            relative_vector_field_error=None,
            rollout_rmse=rollout_rmse,
            details="Expression string failed to parse into valid SymPy AST.",
        )

    # Check for unexpected variables
    free_syms = {s.name for s in cand_sp.free_symbols}
    valid_syms = set(variable_names)
    if not free_syms.issubset(valid_syms):
        return ClassificationResult(
            status=RecoveryClass.INVALID_EXPRESSION,
            is_exact_or_equivalent=False,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=cand_sp,
            sympy_true=true_sp,
            relative_coefficient_error=None,
            vector_field_rmse=None,
            relative_vector_field_error=None,
            rollout_rmse=rollout_rmse,
            details=f"Expression contains variables outside state space: {free_syms - valid_syms}",
        )

    # 3. Domain validation and Singularity check
    # Generate test points if not provided
    if test_points is None:
        rng = np.random.default_rng(42)
        n_pts = 100
        cols = []
        for v in variable_names:
            if domain and v in domain:
                low, high = domain[v]
            else:
                low, high = -2.0, 2.0
            cols.append(rng.uniform(low, high, size=(n_pts, 1)))
        test_points = np.hstack(cols)

    # Evaluate candidate and true numerically on test points
    try:
        f_cand = sp.lambdify([syms[v] for v in variable_names], cand_sp, modules=["numpy"])
        f_true = sp.lambdify([syms[v] for v in variable_names], true_sp, modules=["numpy"])
        
        args = [test_points[:, i] for i in range(len(variable_names))]
        vals_cand = np.asarray(f_cand(*args), dtype=np.float64).ravel()
        vals_true = np.asarray(f_true(*args), dtype=np.float64).ravel()

        if not np.all(np.isfinite(vals_cand)):
            return ClassificationResult(
                status=RecoveryClass.INVALID_EXPRESSION,
                is_exact_or_equivalent=False,
                cand_expr_str=cand_expr_str,
                true_expr_str=true_expr_str,
                sympy_cand=cand_sp,
                sympy_true=true_sp,
                relative_coefficient_error=None,
                vector_field_rmse=None,
                relative_vector_field_error=None,
                rollout_rmse=rollout_rmse,
                details="Candidate expression evaluated to NaN or Inf within valid physical domain.",
            )
    except Exception as e:
        return ClassificationResult(
            status=RecoveryClass.INVALID_EXPRESSION,
            is_exact_or_equivalent=False,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=cand_sp,
            sympy_true=true_sp,
            relative_coefficient_error=None,
            vector_field_rmse=None,
            relative_vector_field_error=None,
            rollout_rmse=rollout_rmse,
            details=f"Numerical evaluation raised runtime error: {e}",
        )

    diff_pts = vals_cand - vals_true
    vf_rmse = float(np.sqrt(np.mean(diff_pts ** 2)))
    true_norm = float(np.sqrt(np.mean(vals_true ** 2))) + 1e-12
    rel_vf_error = float(vf_rmse / true_norm)

    # 4. Symbolic Equivalence Testing via SymPy
    # Check exact syntactic AST match (handling float vs int representations like 1.0*x vs x)
    try:
        is_exact_ast = (cand_sp == true_sp) or (sp.nsimplify(cand_sp) == sp.nsimplify(true_sp))
    except Exception:
        is_exact_ast = (cand_sp == true_sp)

    if is_exact_ast:
        return ClassificationResult(
            status=RecoveryClass.EXACT_SYMBOLIC,
            is_exact_or_equivalent=True,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=cand_sp,
            sympy_true=true_sp,
            relative_coefficient_error=0.0,
            vector_field_rmse=vf_rmse,
            relative_vector_field_error=rel_vf_error,
            rollout_rmse=rollout_rmse,
            details="Syntactically identical SymPy AST match.",
        )

    # Check algebraic equivalence (diff simplifies to zero)
    diff_expr = sp.simplify(cand_sp - true_sp)
    if diff_expr == 0:
        return ClassificationResult(
            status=RecoveryClass.ALGEBRAICALLY_EQUIVALENT,
            is_exact_or_equivalent=True,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=cand_sp,
            sympy_true=true_sp,
            relative_coefficient_error=0.0,
            vector_field_rmse=vf_rmse,
            relative_vector_field_error=rel_vf_error,
            rollout_rmse=rollout_rmse,
            details="Algebraically equivalent (difference simplifies to zero).",
        )

    # Try advanced algebraic simplification (expand, together, trigsimp)
    diff_expanded = sp.expand(diff_expr)
    if diff_expanded == 0:
        return ClassificationResult(
            status=RecoveryClass.ALGEBRAICALLY_EQUIVALENT,
            is_exact_or_equivalent=True,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=cand_sp,
            sympy_true=true_sp,
            relative_coefficient_error=0.0,
            vector_field_rmse=vf_rmse,
            relative_vector_field_error=rel_vf_error,
            rollout_rmse=rollout_rmse,
            details="Algebraically equivalent after polynomial expansion.",
        )

    diff_trig = sp.trigsimp(diff_expr)
    if diff_trig == 0:
        return ClassificationResult(
            status=RecoveryClass.ALGEBRAICALLY_EQUIVALENT,
            is_exact_or_equivalent=True,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=cand_sp,
            sympy_true=true_sp,
            relative_coefficient_error=0.0,
            vector_field_rmse=vf_rmse,
            relative_vector_field_error=rel_vf_error,
            rollout_rmse=rollout_rmse,
            details="Algebraically equivalent after trigonometric simplification.",
        )

    # 5. Check Correct Support with Approximate Coefficients
    # Check if ratio is approximately constant: cand_sp / true_sp ~ c or terms match
    # For single terms:
    ratio_expr = sp.simplify(cand_sp / true_sp) if true_sp != 0 else None
    if ratio_expr is not None and ratio_expr.is_number and not ratio_expr.has(*syms.values()):
        ratio_val = float(ratio_expr)
        rel_coef_err = abs(ratio_val - 1.0)
        if rel_coef_err <= coef_tol:
            return ClassificationResult(
                status=RecoveryClass.CORRECT_SUPPORT_APPROXIMATE_COEFFICIENTS,
                is_exact_or_equivalent=False,
                cand_expr_str=cand_expr_str,
                true_expr_str=true_expr_str,
                sympy_cand=cand_sp,
                sympy_true=true_sp,
                relative_coefficient_error=rel_coef_err,
                vector_field_rmse=vf_rmse,
                relative_vector_field_error=rel_vf_error,
                rollout_rmse=rollout_rmse,
                details=f"Functional support matches ground truth; coefficient error is {rel_coef_err*100:.2f}% (<= {coef_tol*100:.1f}%).",
            )

    # 6. Check Approximate Vector Field
    if rel_vf_error <= vector_field_tol:
        return ClassificationResult(
            status=RecoveryClass.APPROXIMATE_VECTOR_FIELD,
            is_exact_or_equivalent=False,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=cand_sp,
            sympy_true=true_sp,
            relative_coefficient_error=None,
            vector_field_rmse=vf_rmse,
            relative_vector_field_error=rel_vf_error,
            rollout_rmse=rollout_rmse,
            details=f"Structurally non-equivalent, but approximates vector field with relative error {rel_vf_error*100:.2f}% (<= {vector_field_tol*100:.1f}%).",
        )

    # 7. Check Rollout-Only Match
    if rollout_rmse is not None and rollout_rmse <= rollout_tol:
        return ClassificationResult(
            status=RecoveryClass.ROLLOUT_ONLY_MATCH,
            is_exact_or_equivalent=False,
            cand_expr_str=cand_expr_str,
            true_expr_str=true_expr_str,
            sympy_cand=cand_sp,
            sympy_true=true_sp,
            relative_coefficient_error=None,
            vector_field_rmse=vf_rmse,
            relative_vector_field_error=rel_vf_error,
            rollout_rmse=rollout_rmse,
            details=f"Vector field error is large ({rel_vf_error*100:.1f}%), but trajectory rollout matches fortuitously (RMSE {rollout_rmse:.4f} <= {rollout_tol}).",
        )

    # 8. Incorrect
    return ClassificationResult(
        status=RecoveryClass.INCORRECT,
        is_exact_or_equivalent=False,
        cand_expr_str=cand_expr_str,
        true_expr_str=true_expr_str,
        sympy_cand=cand_sp,
        sympy_true=true_sp,
        relative_coefficient_error=None,
        vector_field_rmse=vf_rmse,
        relative_vector_field_error=rel_vf_error,
        rollout_rmse=rollout_rmse,
        details="Expression is structurally and numerically incorrect across vector field and rollout.",
    )
