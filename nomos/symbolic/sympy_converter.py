"""
NOMOS SymPy Expression Generation
Agent E02
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import sympy as sp


def parse_feature_to_sympy(feature_name: str, symbol_dict: Dict[str, sp.Symbol]) -> sp.Expr:
    """
    Safely convert feature string like 'x', 'x^2', 'x*y', 'sin(theta)', '1' into SymPy expression.
    """
    feature_name = feature_name.strip()
    if feature_name == "1":
        return sp.Integer(1)

    # Replace caret with ** for power
    clean_str = feature_name.replace("^", "**")

    # Safe local symbols mapping
    local_dict = dict(symbol_dict)
    local_dict["sin"] = sp.sin
    local_dict["cos"] = sp.cos
    local_dict["exp"] = sp.exp

    return sp.parse_expr(clean_str, local_dict=local_dict)


def matrix_to_sympy_system(
    Xi: np.ndarray,
    feature_names: List[str],
    variable_names: List[str],
    coef_tolerance: float = 1e-6,
) -> Dict[str, sp.Expr]:
    """
    Convert learned coefficient matrix Xi (P x n) and candidate feature names
    into exact SymPy symbolic expressions for each state variable.
    """
    Xi = np.asarray(Xi, dtype=np.float64)
    P, n = Xi.shape
    if P != len(feature_names):
        raise ValueError(f"Feature count mismatch: {P} rows in Xi vs {len(feature_names)} features")
    if n != len(variable_names):
        raise ValueError(f"State dimension mismatch: {n} cols in Xi vs {len(variable_names)} variables")

    symbols = {v: sp.Symbol(v) for v in variable_names}
    parsed_features = [parse_feature_to_sympy(f, symbols) for f in feature_names]

    system_exprs: Dict[str, sp.Expr] = {}

    for col, vname in enumerate(variable_names):
        total_expr = sp.Integer(0)
        for row, feat_expr in enumerate(parsed_features):
            coeff = float(Xi[row, col])
            if abs(coeff) >= coef_tolerance:
                # Add rounded coefficient
                sp_coeff = sp.Float(coeff, 6)
                total_expr += sp_coeff * feat_expr
        system_exprs[vname] = total_expr

    return system_exprs
