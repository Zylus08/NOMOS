"""
NOMOS Symbolic Package Module
"""

from nomos.symbolic.representation import equation_to_dict, system_to_json
from nomos.symbolic.sympy_converter import parse_feature_to_sympy, matrix_to_sympy_system
from nomos.symbolic.simplification import simplify_and_format_equation
from nomos.symbolic.comparison import check_algebraic_equivalence
from nomos.symbolic.complexity import compute_equation_complexity
from nomos.symbolic.dimensional import DimensionalConsistencyChecker

__all__ = [
    "equation_to_dict",
    "system_to_json",
    "parse_feature_to_sympy",
    "matrix_to_sympy_system",
    "simplify_and_format_equation",
    "check_algebraic_equivalence",
    "compute_equation_complexity",
    "DimensionalConsistencyChecker",
]
