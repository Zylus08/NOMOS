"""
NOMOS Typed Symbolic Primitives & Domain Protection
Milestone M2 — Phase 2 Expression Representation
Agents D01, D02, E01, E07
"""

from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Tuple, Any
import numpy as np


class NodeType(Enum):
    # Terminals
    VARIABLE = auto()
    CONSTANT = auto()
    CONTROL = auto()

    # Unary operators
    NEG = auto()
    SIN = auto()
    COS = auto()
    EXP = auto()
    LOG = auto()
    ABS = auto()
    SQRT = auto()

    # Binary operators
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()


# Domain-safe operator functions
# Explicitly documented hypothesis class: protected operators guarantee finiteness and numerical stability
# without producing silent NaNs or zero-division crashes.

EPSILON = 1e-8
MAX_EXP_ARG = 50.0


def protected_div(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Protected division: a / b.
    If |b| < 1e-8, uses sgn(b) * 1e-8 (or 1e-8 if b==0).
    """
    denom = np.copy(b)
    mask = np.abs(denom) < EPSILON
    denom[mask] = np.where(denom[mask] >= 0, EPSILON, -EPSILON)
    return a / denom


def protected_log(a: np.ndarray) -> np.ndarray:
    """
    Protected natural logarithm: ln(|a|).
    For |a| < 1e-8, clamps to ln(1e-8).
    """
    safe_a = np.clip(np.abs(a), EPSILON, 1e20)
    return np.log(safe_a)


def protected_exp(a: np.ndarray) -> np.ndarray:
    """
    Protected exponential with overflow ceiling: exp(clamp(a, -50, 50)).
    Prevents floating-point infinity overflow.
    """
    safe_a = np.clip(a, -MAX_EXP_ARG, MAX_EXP_ARG)
    return np.exp(safe_a)


def protected_sqrt(a: np.ndarray) -> np.ndarray:
    """
    Protected square root: sqrt(|a|).
    """
    return np.sqrt(np.abs(a))


def protected_pow(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Domain-safe general power:
    For non-integer b, computes sign(a) * |a|^b or |a|^b to preserve real domain.
    """
    # If b is scalar integer
    if isinstance(b, (int, np.integer)) or (isinstance(b, float) and b.is_integer()):
        int_b = int(b)
        if int_b < 0:
            return protected_div(np.ones_like(a), a ** (-int_b))
        return a ** int_b

    safe_base = np.abs(a) + EPSILON
    clipped_b = np.clip(b, -10.0, 10.0)
    return safe_base ** clipped_b
