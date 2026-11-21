"""
NOMOS Coefficient Error Metrics
Agent F05
"""

from typing import Dict, Any
import numpy as np


def evaluate_coefficient_error(
    discovered_xi: np.ndarray,
    ground_truth_xi: np.ndarray,
) -> Dict[str, Any]:
    """
    Compute relative parameter error, Frobenius norm distance, and per-column errors.
    Inputs: (P, n) arrays.
    """
    disc = np.asarray(discovered_xi, dtype=np.float64)
    true = np.asarray(ground_truth_xi, dtype=np.float64)

    if disc.shape != true.shape:
        raise ValueError(f"Coefficient shape mismatch: {disc.shape} vs {true.shape}")

    diff = disc - true
    frobenius_error = float(np.linalg.norm(diff, ord="fro"))
    true_frobenius = float(np.linalg.norm(true, ord="fro"))
    rel_error = float(frobenius_error / (true_frobenius + 1e-12))

    # Active-set only relative error (on ground-truth nonzero elements)
    true_mask = (np.abs(true) > 1e-12)
    if np.any(true_mask):
        active_diff = diff[true_mask]
        active_rel = float(np.linalg.norm(active_diff) / (np.linalg.norm(true[true_mask]) + 1e-12))
    else:
        active_rel = rel_error

    return {
        "frobenius_error": frobenius_error,
        "relative_error": rel_error,
        "active_relative_error": active_rel,
    }
