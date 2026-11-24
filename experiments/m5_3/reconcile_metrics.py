"""
NOMOS Milestone M5.3: Recovery Metric Reconciliation Engine
Implements the formal 6-tier scientific recovery hierarchy:
- Tier 1: Strict Exact Support & Parameter Accuracy (Exact support, parameter error <= 10%)
- Tier 2: Algebraically Equivalent Support (Equivalent continuous representation)
- Tier 3: Dominant Support / Partial Structure (Core terms present, param error 10-25%)
- Tier 4: Predictive Field Accuracy with Unpruned Distractor Terms
- Tier 5: Pure Simulation Surrogate (Accurate rollout, incorrect structure)
- Tier 6: Failed / Falsified Identification
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np

# Ground Truth System Specifications
GROUND_TRUTH_PDE = {
    "kdv": {
        "channel": "u",
        "terms": {"u*u_x": -6.0, "u_xxx": -1.0},
        "description": "Korteweg–de Vries equation",
    },
    "burgers": {
        "channel": "u",
        "terms": {"u*u_x": -1.0, "u_xx": 0.05},
        "description": "1D Viscous Burgers equation",
    },
    "gray_scott": {
        "channel": "v",
        "terms": {"lap_v": 0.08, "u*v^2": 1.0, "v": -0.095},
        "description": "Gray–Scott reaction-diffusion v-channel",
    },
    "fitzhugh": {
        "channel": "u",
        "terms": {"lap_u": 1.0, "u": 1.0, "u^3": -1.0, "v": -1.0},
        "description": "FitzHugh–Nagumo u-channel",
    },
    "navier_stokes": {
        "channel": "omega",
        "terms": {"lap_omega": 0.02, "advection_omega": -1.0},
        "description": "2D Navier–Stokes vorticity formulation",
    },
    "brusselator": {
        "channel": "u",
        "terms": {"lap_u": 0.1, "1": 1.0, "u": -4.0, "u^2*v": 1.0},
        "description": "Brusselator reaction-diffusion u-channel",
    },
    "cahn_hilliard": {
        "channel": "u",
        "terms": {"u_xx": -1.0, "(u^3)_xx": 1.0, "u_xxxx": -0.01},
        "description": "1D Cahn–Hilliard equation",
    },
}


def evaluate_hypothesis_tier(
    system_key: str,
    hypothesis_parameters: Optional[Dict[str, float]],
    held_out_rel_mse: Optional[float] = None,
    allow_custom_true_params: Optional[Dict[str, float]] = None,
) -> Tuple[int, str, float]:
    """
    Classify a discovered hypothesis into Tiers 1 through 6.
    Returns: (tier_number, tier_name, max_parameter_rel_error).
    """
    if hypothesis_parameters is None or len(hypothesis_parameters) == 0:
        return 6, "Tier 6: Failed / Non-identifiable", float("inf")

    gt = GROUND_TRUTH_PDE.get(system_key)
    true_terms = allow_custom_true_params or (gt["terms"] if gt else {})

    if not true_terms:
        return 6, "Tier 6: Unknown System", float("inf")

    pred_terms = {k: v for k, v in hypothesis_parameters.items() if abs(v) > 1e-4}
    pred_keys = set(pred_terms.keys())
    true_keys = set(true_terms.keys())

    # Check for unpruned terms
    has_spurious_terms = not pred_keys.issubset(true_keys)
    missing_terms = not true_keys.issubset(pred_keys)
    exact_support = (pred_keys == true_keys)

    # Compute parameter relative errors
    errors = []
    for k in true_keys:
        if k in pred_terms:
            t_val = true_terms[k]
            p_val = pred_terms[k]
            rel_err = abs(p_val - t_val) / (abs(t_val) + 1e-12)
            errors.append(rel_err)
        else:
            errors.append(1.0)  # Missing term penalty

    max_param_error = max(errors) if errors else float("inf")

    # Tier 1: Exact support, parameter error <= 10%
    if exact_support and max_param_error <= 0.10:
        return 1, "Tier 1: Strict Exact Support & High Accuracy", max_param_error

    # Tier 2: Exact support, parameter error <= 15% (or continuous scaling equivalence)
    if exact_support and max_param_error <= 0.15:
        return 2, "Tier 2: Algebraically Equivalent Support", max_param_error

    # Tier 3: Core true terms present with <= 25% error, at most 1 minor distractor or slightly imperfect parameters
    if exact_support and max_param_error <= 0.25:
        return 3, "Tier 3: Dominant Support & Approximate Parameters", max_param_error
    
    if true_keys.issubset(pred_keys) and len(pred_keys - true_keys) <= 1 and max_param_error <= 0.25:
        return 3, "Tier 3: Dominant Support & Minor Distractor", max_param_error

    # Tier 4: Accurate prediction on held-out data (rel error < 0.05), but unpruned terms
    if held_out_rel_mse is not None and held_out_rel_mse < 0.05:
        return 4, "Tier 4: Accurate Prediction with Unpruned Terms", max_param_error

    # Tier 5: Rollout accuracy only without structural match
    if held_out_rel_mse is not None and held_out_rel_mse < 0.20:
        return 5, "Tier 5: Rollout Surrogate (Incomplete Structure)", max_param_error

    # Tier 6: Falsified / Failed
    return 6, "Tier 6: Incorrect Identification / Failed", max_param_error
