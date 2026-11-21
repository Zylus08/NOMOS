"""
NOMOS Physical Dimensional Consistency Checking
Agents A06 & E08
"""

from typing import Dict, List, Optional, Tuple, Any
import sympy as sp


class DimensionalConsistencyChecker:
    """
    Verifies physical dimension homogeneity across additive terms in discovered equations.
    """

    def __init__(self, variable_dimensions: Optional[Dict[str, Dict[str, int]]] = None):
        # Maps var -> {'L': 1, 'T': -1, 'M': 0}
        self.var_dims = variable_dimensions or {}

    def check_expression(self, expr: sp.Expr) -> bool:
        """
        Check that all terms in a sum have identical dimensional exponents.
        If dimensions are unspecified, returns True (vacuously consistent).
        """
        if not self.var_dims:
            return True

        if not expr.is_Add:
            return True

        # Check each summand
        terms = expr.args
        term_dims = []
        for term in terms:
            dim_vec = {"L": 0, "T": 0, "M": 0}
            for sym in term.free_symbols:
                s_name = sym.name
                if s_name in self.var_dims:
                    for base, power in self.var_dims[s_name].items():
                        dim_vec[base] = dim_vec.get(base, 0) + power
            term_dims.append(dim_vec)

        # Verify all terms match first term
        first = term_dims[0]
        for td in term_dims[1:]:
            if td != first:
                return False
        return True
