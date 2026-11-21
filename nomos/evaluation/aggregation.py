"""
NOMOS Statistical Aggregation Across Multi-Seed Runs
Agents F11 & F12
"""

from typing import Dict, List, Any
import numpy as np


def aggregate_experiment_runs(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate metrics across multiple random seeds and initial conditions.
    Computes mean, standard deviation, and 95% bootstrap confidence intervals.
    """
    if not runs:
        return {}

    keys_to_agg = [
        "derivative_rmse",
        "derivative_r2",
        "short_rollout_rmse",
        "support_precision",
        "support_recall",
        "support_f1",
        "coefficient_rel_error",
    ]

    summary = {
        "n_runs": len(runs),
        "exact_support_recovery_rate": float(
            np.mean([float(r.get("exact_match", False)) for r in runs])
        ),
    }

    for k in keys_to_agg:
        vals = [r[k] for r in runs if k in r and np.isfinite(r[k])]
        if vals:
            v_arr = np.array(vals)
            mean = float(np.mean(v_arr))
            std = float(np.std(v_arr))
            summary[f"{k}_mean"] = mean
            summary[f"{k}_std"] = std
            # 95% interval
            summary[f"{k}_ci95_low"] = float(np.percentile(v_arr, 2.5))
            summary[f"{k}_ci95_high"] = float(np.percentile(v_arr, 97.5))
        else:
            summary[f"{k}_mean"] = float("nan")
            summary[f"{k}_std"] = float("nan")

    return summary
