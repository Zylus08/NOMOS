"""
Project NOMOS - Milestone M5.2
Mechanism Ablations, BIC Calibration, and Held-Out Generalization Audit.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd


def audit_bic_calibration():
    """
    Quantify nominal vs effective sample size and BIC scaling.
    N_nominal = N_x * N_t (or N_x * N_y * N_t).
    N_eff = (L_x * T) / (4 * xi_x * tau_t).
    """
    # Typical KdV simulation:
    # L_x = 20.0, T = 2.0, N_x = 128, N_t = 100 -> N_nominal = 12800.
    # xi_x (soliton width) ~ 1.5, tau_t (persistence) ~ 0.5
    # N_eff = (20.0 * 2.0) / (4 * 1.5 * 0.5) = 40.0 / 3.0 = 13.3!
    # Ratio = 12800 / 13.3 = 960x pseudoreplication!
    
    # 2D Reaction-Diffusion (Gray-Scott):
    # L_x = 2.5, L_y = 2.5, T = 1.0, N_x = 32, N_y = 32, N_t = 30 -> N_nominal = 30720.
    # xi_x ~ 0.25, xi_y ~ 0.25, tau_t ~ 0.1
    # N_eff ~ 125.0
    # Ratio = 30720 / 125 = 245x pseudoreplication!

    systems_bic = {
        "kdv_1d": {
            "N_nominal": 128 * 100,
            "xi_x": 1.5,
            "tau_t": 0.5,
            "N_eff": round((20.0 * 2.0) / (4 * 1.5 * 0.5), 1),
            "inflation_factor": round((128 * 100) / ((20.0 * 2.0) / (4 * 1.5 * 0.5)), 1),
            "delta_bic_noise_nominal": round(12800 * np.log(1 + 0.005), 2),
            "delta_bic_noise_eff": round(13.3 * np.log(1 + 0.005), 2),
        },
        "gray_scott_2d": {
            "N_nominal": 32 * 32 * 30,
            "xi_x": 0.25,
            "tau_t": 0.1,
            "N_eff": round((2.5 * 2.5 * 1.0) / (8 * 0.25 * 0.25 * 0.1), 1),
            "inflation_factor": round((32 * 32 * 30) / ((2.5 * 2.5 * 1.0) / (8 * 0.25 * 0.25 * 0.1)), 1),
            "delta_bic_noise_nominal": round(30720 * np.log(1 + 0.005), 2),
            "delta_bic_noise_eff": round(125.0 * np.log(1 + 0.005), 2),
        },
    }
    return systems_bic


def audit_held_out_generalization():
    """
    Examine the held-out benchmark results from audit/m5_1/HELD_OUT_BENCHMARKS.csv
    and audit/m5_1/STRONG_BASELINES.csv.
    """
    df_held = pd.read_csv("audit/m5_1/HELD_OUT_BENCHMARKS.csv")
    df_strong = pd.read_csv("audit/m5_1/STRONG_BASELINES.csv")
    
    # Brusselator performance by strategy
    bruss_df = df_held[df_held["system"] == "brusselator_2d"]
    bruss_strat = bruss_df.groupby("strategy").agg({
        "exact_recovery": ["count", "mean", "sum"],
        "queries": "mean",
        "param_error": "mean",
    }).to_dict()

    # Cahn-Hilliard performance by strategy
    ch_df = df_held[df_held["system"] == "cahn_hilliard"]
    ch_strat = ch_df.groupby("strategy").agg({
        "exact_recovery": ["count", "mean", "sum"],
        "queries": "mean",
        "param_error": "mean",
    }).to_dict()

    return {
        "brusselator_by_strategy": {
            strat: {
                "n_episodes": int(len(sub)),
                "recovery_rate": float(sub["exact_recovery"].mean()),
                "mean_queries": float(sub["queries"].mean()),
                "mean_param_error": float(sub["param_error"].mean()),
            }
            for strat, sub in bruss_df.groupby("strategy")
        },
        "cahn_hilliard_by_strategy": {
            strat: {
                "n_episodes": int(len(sub)),
                "recovery_rate": float(sub["exact_recovery"].mean()),
                "mean_queries": float(sub["queries"].mean()),
                "mean_param_error": float(sub["param_error"].mean()),
            }
            for strat, sub in ch_df.groupby("strategy")
        },
    }


def audit_mechanism_ablations():
    """
    Compare the primary strategies in M5/M5.1:
    1. Full NOMOS: Greedy Disagreement with Hypothesis Portfolio + Calibrated BIC.
    2. Ablation 1 (No Portfolio / Single Hypothesis): Greedily optimizes residual without competing vector field.
    3. Ablation 2 (No Active Divergence / Portfolio + Random IC): Random sampling from candidate pool.
    4. Ablation 3 (No Active Divergence / Fixed Schedule): Deterministic sequential acquisition.
    5. Ablation 4 (Uncertainty-Aware / Epistemic Variance): Selects max prediction variance.
    """
    df_raw = pd.read_csv("audit/m5/RAW_EPISODES.csv")
    
    strat_summary = {}
    for strat, sub in df_raw.groupby("strategy"):
        strat_summary[strat] = {
            "episodes": len(sub),
            "exact_recovery_rate": float(sub["is_exact_recovery"].mean()),
            "mean_queries": float(sub["experiments_queried"].mean()),
            "std_queries": float(sub["experiments_queried"].std()),
            "false_stops": int(((sub["is_exact_recovery"] == 0) & (sub["status"] == "CONVERGED_UNIQUE_LAW")).sum()),
            "exhausted_stops": int((sub["status"] == "BUDGET_EXHAUSTED").sum()),
            "ambiguous_stops": int((sub["status"] == "MULTIPLE_PLAUSIBLE_LAWS").sum()),
        }

    return strat_summary


def main():
    print("Running Mechanism Ablations, BIC, and Held-Out Audits...")
    bic_data = audit_bic_calibration()
    held_data = audit_held_out_generalization()
    abl_data = audit_mechanism_ablations()
    
    combined = {
        "bic_calibration": bic_data,
        "held_out_generalization": held_data,
        "mechanism_ablations": abl_data,
    }
    
    out_file = Path("audit/m5_2/ABLATIONS_AND_BIC.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)
        
    print("Ablation & Calibration Audit complete and saved to audit/m5_2/ABLATIONS_AND_BIC.json.")


if __name__ == "__main__":
    main()
