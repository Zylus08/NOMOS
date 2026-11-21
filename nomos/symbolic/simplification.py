"""
NOMOS Symbolic Simplification & Formatting
Agents E03 & E04
"""

from typing import Dict, List, Optional, Tuple
import sympy as sp


def simplify_and_format_equation(
    expr: sp.Expr,
    round_decimals: int = 4,
    tolerance: float = 1e-5,
) -> Tuple[sp.Expr, str, str]:
    """
    Simplify expression, prune near-zero coefficients, and generate LaTeX and string formats.
    Returns: (simplified_expr, latex_str, readable_str)
    """
    # Round numerical floats in expression
    def round_floats(val):
        if isinstance(val, sp.Float):
            f_val = float(val)
            if abs(f_val) < tolerance:
                return sp.Integer(0)
            return sp.Float(round(f_val, round_decimals))
        return val

    # Walk and replace
    cleaned_expr = expr.xreplace({n: round_floats(n) for n in expr.atoms(sp.Float)})
    simplified = sp.simplify(cleaned_expr)

    latex_str = sp.latex(simplified)
    readable_str = str(simplified)

    return simplified, latex_str, readable_str
