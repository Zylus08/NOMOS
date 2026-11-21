"""
NOMOS Symbolic Representation & Expression Serialization
Agents E01 & E09
"""

import json
from typing import Dict, List, Optional, Any
import sympy as sp
from nomos.core.symbolic import DiscoveredEquation, DiscoveredSystem


def equation_to_dict(eq: DiscoveredEquation) -> Dict[str, Any]:
    return {
        "variable_name": eq.variable_name,
        "raw_str": eq.raw_str,
        "latex_str": eq.latex_str,
        "sympy_repr": str(eq.sympy_expr),
        "active_features": eq.active_features,
        "coefficients": eq.coefficients,
        "complexity_score": eq.complexity_score,
    }


def system_to_json(sys: DiscoveredSystem) -> str:
    payload = {
        "system_name": sys.system_name,
        "state_names": sys.state_names,
        "total_complexity": sys.total_complexity,
        "metadata": sys.metadata,
        "equations": {k: equation_to_dict(v) for k, v in sys.equations.items()},
    }
    return json.dumps(payload, indent=2)
