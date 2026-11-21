"""
NOMOS Core Symbolic Interfaces
Agent A03 & E01
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import sympy as sp


@dataclass
class DiscoveredEquation:
    """Represents a discovered scalar differential equation for state variable x_i."""
    variable_name: str
    sympy_expr: sp.Expr
    latex_str: str
    raw_str: str
    active_features: List[str]
    coefficients: Dict[str, float]
    complexity_score: float


@dataclass
class DiscoveredSystem:
    """Collection of discovered differential equations governing a dynamical system."""
    equations: Dict[str, DiscoveredEquation]
    system_name: str
    state_names: List[str]
    total_complexity: float
    metadata: Dict[str, Any]
