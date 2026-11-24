"""
Project NOMOS - Milestone M5.2
Forensic Investigation: Query-Efficiency Dynamics & Cahn-Hilliard 4th-Order Operator Pruning.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, wilcoxon

from nomos.pde.simulators.cahn_hilliard import CahnHilliard1DSimulator
from nomos.pde.weak_form import WeakFormPDEDiscovery
from nomos.pde.schema import Grid1D, TimeGrid


def audit_query_efficiency():
    df_raw = pd.read_csv("audit/m5/RAW_EPISODES.csv")
    
    # 1. Inspect all active episodes (strategy == 'greedy_disagreement')
    df_act = df_raw[df_raw["strategy"] == "greedy_disagreement"].copy()
    
    # Exact recoveries in active
    rec_act = df_act[df_act["is_exact_recovery"] == 1]
    nonrec_act = df_act[df_act["is_exact_recovery"] == 0]
    
    # Query count distributions
    rec_queries = rec_act["experiments_queried"].tolist()
    nonrec_queries = nonrec_act["experiments_queried"].tolist()
    
    all_act_queries = df_act["experiments_queried"].tolist()
    
    # Check stopping reasons/status
    act_status_counts = df_act["status"].value_counts().to_dict()
    
    # Passive Fixed query distribution
    df_fix = df_raw[df_raw["strategy"] == "fixed"].copy()
    rec_fix = df_fix[df_fix["is_exact_recovery"] == 1]
    nonrec_fix = df_fix[df_fix["is_exact_recovery"] == 0]
    fix_queries_rec = rec_fix["experiments_queried"].tolist()
    fix_queries_all = df_fix["experiments_queried"].tolist()

    # Passive Random query distribution
    df_rnd = df_raw[df_raw["strategy"] == "random"].copy()
    rec_rnd = df_rnd[df_rnd["is_exact_recovery"] == 1]
    rnd_queries_rec = rec_rnd["experiments_queried"].tolist()
    rnd_queries_all = df_rnd["experiments_queried"].tolist()

    # Paired comparisons conditioned on mutual success vs unconditional
    df_paired = pd.read_csv("audit/m5_1/CORRECTED_PAIRED_OUTCOMES.csv")
    mutual_success = df_paired[(df_paired["active_recovered"] == 1) & (df_paired["fixed_recovered"] == 1)]
    
    # Wilcoxon on mutual success (n=54)
    w_stat_cond, w_pval_cond = wilcoxon(
        mutual_success["active_queries"],
        mutual_success["fixed_queries"],
        alternative="less"
    )

    # Wilcoxon unconditional across all 100 episodes
    w_stat_uncond, w_pval_uncond = wilcoxon(
        df_paired["active_queries"],
        df_paired["fixed_queries"],
        alternative="two-sided"
    )

    forensic_summary = {
        "active_total_episodes": len(df_act),
        "active_recoveries": len(rec_act),
        "active_failures": len(nonrec_act),
        "active_recovery_query_mean": float(np.mean(rec_queries)),
        "active_recovery_query_std": float(np.std(rec_queries)),
        "active_failure_query_mean": float(np.mean(nonrec_queries)),
        "active_failure_query_std": float(np.std(nonrec_queries)),
        "fixed_recovery_query_mean": float(np.mean(fix_queries_rec)),
        "fixed_recovery_query_std": float(np.std(fix_queries_rec)),
        "fixed_all_query_mean": float(np.mean(fix_queries_all)),
        "random_recovery_query_mean": float(np.mean(rnd_queries_rec)),
        "mutual_success_count": len(mutual_success),
        "wilcoxon_conditional_pval": float(w_pval_cond),
        "wilcoxon_unconditional_pval": float(w_pval_uncond),
        "active_query_distribution_rec": {int(k): int(v) for k, v in rec_act["experiments_queried"].value_counts().items()},
        "active_query_distribution_nonrec": {int(k): int(v) for k, v in nonrec_act["experiments_queried"].value_counts().items()},
        "status_distribution_active": act_status_counts,
    }
    return forensic_summary


def audit_cahn_hilliard_recovery():
    """
    Examine the weak-form identification of 1D Cahn-Hilliard:
    True equation: u_t = -1.0 * u_xx + 1.0 * (u^3)_xx - 0.0025 * u_xxxx
    Examine why -0.0025 u_xxxx was pruned at lambda = 0.045, and test if lambda = 0.001 can recover it.
    """
    grid = Grid1D.create((0.0, 2.0 * np.pi), 64)
    time_grid = TimeGrid.create((0.0, 1.0), 21)
    sim = CahnHilliard1DSimulator(gamma=1.0, epsilon=0.05)
    
    u0 = np.cos(grid.x) + 0.1 * np.cos(2 * grid.x)
    field = sim.simulate(u0, grid, time_grid)
    
    # Fit with default threshold lambda = 0.045
    wf_default = WeakFormPDEDiscovery(threshold=0.045, poly_order=4)
    res_default = wf_default.fit(field)
    
    # Fit with sensitive threshold lambda = 0.001
    wf_sensitive = WeakFormPDEDiscovery(threshold=0.001, poly_order=4)
    res_sensitive = wf_sensitive.fit(field)

    return {
        "true_equation": "u_t = -1.0 * u_xx + 1.0 * (u^3)_xx - 0.0025 * u_xxxx",
        "default_threshold": 0.045,
        "default_equation": res_default.discovered_equation,
        "default_parameters": {k: float(v) for k, v in res_default.coefficients.items()},
        "sensitive_threshold": 0.001,
        "sensitive_equation": res_sensitive.discovered_equation,
        "sensitive_parameters": {k: float(v) for k, v in res_sensitive.coefficients.items()},
    }


def main():
    print("Running Query Efficiency & Cahn-Hilliard Forensics...")
    q_res = audit_query_efficiency()
    ch_res = audit_cahn_hilliard_recovery()
    
    out = {
        "query_efficiency_audit": q_res,
        "cahn_hilliard_audit": ch_res,
    }
    
    out_path = Path("audit/m5_2/FORENSIC_QUERY_AND_CH.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        
    print("Forensic analysis complete and saved to audit/m5_2/FORENSIC_QUERY_AND_CH.json.")
    print("Active Recovery Query Mean:", q_res["active_recovery_query_mean"], "Std:", q_res["active_recovery_query_std"])
    print("Active Failure Query Mean:", q_res["active_failure_query_mean"], "Std:", q_res["active_failure_query_std"])
    print("Default Cahn-Hilliard Recovered:", ch_res["default_equation"], ch_res["default_parameters"])
    print("Sensitive Cahn-Hilliard Recovered:", ch_res["sensitive_equation"], ch_res["sensitive_parameters"])


if __name__ == "__main__":
    main()
