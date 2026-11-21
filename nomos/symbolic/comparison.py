"""
NOMOS Structural & Algebraic Equivalence Testing
Agents E05, E06, E10
"""

from typing import Dict, List, Optional, Tuple, Any
import sympy as sp


def check_algebraic_equivalence(
    discovered_expr: sp.Expr,
    true_expr: sp.Expr,
    tolerance: float = 1e-4,
) -> Tuple[bool, float]:
    """
    Test algebraic equivalence between discovered and ground truth expressions:
        Diff = simplify(discovered - true)
    Checks if maximum coefficient of difference is below tolerance.
    Returns: (is_equivalent, max_residual_coeff)
    """
    diff = sp.simplify(discovered_expr - true_expr)
    if diff == 0:
        return True, 0.0

    # Extract all numerical float atoms from diff
    floats = [abs(float(f)) for f in diff.atoms(sp.Float)]
    if not floats:
        # Check if diff is a constant number
        if diff.is_number:
            max_res = abs(float(diff))
            return max_res <= tolerance, max_res
        return False, 1.0

    max_res = max(floats)
    return max_res <= tolerance, max_res
