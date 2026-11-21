"""
NOMOS Support Precision, Recall, and Sparsity Evaluation
Agent F04
"""

from typing import Dict, Tuple, Any
import numpy as np


def evaluate_equation_support(
    discovered_support: np.ndarray,
    ground_truth_support: np.ndarray,
) -> Dict[str, Any]:
    """
    Compute Precision, Recall, F1, and Exact Match on the binary sparsity pattern.
    Inputs: boolean matrices of shape (P, n).
    """
    disc = np.asarray(discovered_support, dtype=bool)
    true = np.asarray(ground_truth_support, dtype=bool)

    if disc.shape != true.shape:
        raise ValueError(f"Support shape mismatch: {disc.shape} vs {true.shape}")

    tp = int(np.sum(disc & true))
    fp = int(np.sum(disc & (~true)))
    fn = int(np.sum((~disc) & true))
    tn = int(np.sum((~disc) & (~true)))

    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else (1.0 if fn == 0 else 0.0)
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 1.0
    f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    exact_match = bool(np.array_equal(disc, true))

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match": exact_match,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }
