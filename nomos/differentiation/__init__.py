"""
NOMOS Differentiation Package Module
"""

from nomos.differentiation.finite_difference import finite_difference
from nomos.differentiation.savitzky_golay import savitzky_golay_derivative
from nomos.differentiation.spline import spline_derivative
from nomos.differentiation.diagnostics import evaluate_derivative_error

__all__ = [
    "finite_difference",
    "savitzky_golay_derivative",
    "spline_derivative",
    "evaluate_derivative_error",
]
