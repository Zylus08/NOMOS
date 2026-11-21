"""
NOMOS M1 Comprehensive Scientific Benchmark Matrix Runner
Division F & H — Multi-Seed Benchmark Reconciliation
Investigator: Saksham Mishra <mishrasaksham080705@gmail.com>
"""

import csv
import json
import os
from pathlib import Path
import time
from typing import Dict, List, Any
import numpy as np

from nomos.physics import get_benchmark_system, list_benchmark_names, simulate_system
from nomos.data import (
    Trajectory,
    TrajectoryDataset,
    sample_initial_conditions,
    split_trajectories_disjoint,
    inject_gaussian_noise,
    IsolatedLearnerDataset,
    check_dataset_leakage,
)
from nomos.pipeline import DiscoveryEngine, DiscoveryConfig
from nomos.library import PolynomialLibrary, CompositeLibrary, TrigonometricLibrary
from nomos.evaluation import (
    evaluate_rollout,
    evaluate_equation_support,
    evaluate_coefficient_error,
    evaluate_derivative_prediction,
    OLSBaseline,
    PySINDyAdapter,
)
from nomos.utils.manifest import ExperimentManifest

OUTPUT_DIR = Path("audit/m1")
MANIFESTS_DIR = Path("experiments/manifests")
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = OUTPUT_DIR / "GENERALIZATION_RESULTS.csv"

SYSTEMS = [
    "harmonic_oscillator",
    "damped_oscillator",
    "nonlinear_pendulum",
    "lotka_volterra",
    "lorenz63",
]
NOISE_LEVELS = [0.0, 0.01, 0.05, 0.10]
SEEDS = [42, 101, 777]

# System specific bounds for initial condition sampling
SYSTEM_IC_BOUNDS = {
    "harmonic_oscillator": [(-2.0, 2.0), (-2.0, 2.0)],
    "damped_oscillator": [(-2.5, 2.5), (-2.5, 2.5)],
    "nonlinear_pendulum": [(-2.0, 2.0), (-1.5, 1.5)],
    "lotka_volterra": [(0.5, 2.5), (0.5, 2.5)],
    "lorenz63": [(-15.0, 15.0), (-15.0, 15.0), (10.0, 35.0)],
}

SYSTEM_THRESHOLDS = {
    "harmonic_oscillator": 0.05,
    "damped_oscillator": 0.05,
    "nonlinear_pendulum": 0.05,
    "lotka_volterra": 0.05,
    "lorenz63": 0.10,
}


def run_single_experiment(
    sys_name: str,
    noise_level: float,
    seed: int,
) -> Dict[str, Any]:
    sys_obj = get_benchmark_system(sys_name)
    bounds = SYSTEM_IC_BOUNDS[sys_name]
    thresh = SYSTEM_THRESHOLDS[sys_name]

    manifest = ExperimentManifest.create(
        manifest_id=f"{sys_name}_noise{noise_level:.2f}_seed{seed}",
        benchmark_name=sys_name,
        noise_level=noise_level,
        seed=seed,
    )

    # 1. Sample 5 diverse initial conditions
    ics = sample_initial_conditions(bounds, n_samples=5, method="latin_hypercube", seed=seed)
    t_eval = np.linspace(0.0, 8.0, 801)

    trajectories = []
    for idx, x0 in enumerate(ics):
        sim = simulate_system(sys_obj, x0, (t_eval[0], t_eval[-1]), t_eval=t_eval)
        tr = Trajectory(
            id=f"{sys_name}_{idx}",
            t=sim.t,
            x=sim.x,
            x_clean=np.copy(sim.x),
            x_dot_true=sim.x_dot_true,
        )
        if noise_level > 0.0:
            tr = inject_gaussian_noise(tr, noise_ratio=noise_level, seed=seed + idx)
        trajectories.append(tr)

    dataset = TrajectoryDataset(
        system_name=sys_name,
        variable_names=list(sys_obj.variable_names),
        trajectories=trajectories,
        noise_level=noise_level,
    )

    # 2. Strict trajectory-disjoint train/val/test splitting
    train_ds, val_ds, test_ds = split_trajectories_disjoint(
        dataset, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, seed=seed
    )
    leakage_check = check_dataset_leakage(train_ds, val_ds, test_ds)
    assert not leakage_check["has_leakage"], f"Data leakage detected in {sys_name}!"

    # 3. Blind learner sandboxing
    learner_train = IsolatedLearnerDataset(train_ds)

    # 4. Configure and run NOMOS discovery engine
    diff_method = "savitzky_golay" if noise_level > 0.0 else "finite_difference"
    lib_type = "composite" if "pendulum" in sys_name else "polynomial"

    # Adapt threshold slightly for higher noise levels to suppress spurious noise terms
    eff_thresh = thresh if noise_level == 0.0 else max(thresh, noise_level * 1.5)

    cfg = DiscoveryConfig(
        diff_method=diff_method,
        diff_order=4,
        savgol_window=25 if noise_level >= 0.05 else 15,
        savgol_poly=3,
        library_type=lib_type,
        poly_degree=2,
        threshold=eff_thresh,
        alpha=1e-4 if noise_level > 0 else 1e-6,
    )
    engine = DiscoveryEngine(cfg)
    nomos_out = engine.fit(learner_train)

    # Ground truth matrix
    Xi_true = sys_obj.ground_truth_matrix(nomos_out.feature_names)

    # Evaluate NOMOS on test trajectory
    test_traj = test_ds.trajectories[0]
    nomos_rollout = evaluate_rollout(
        nomos_out.coef, nomos_out.library, test_traj.x_clean, test_traj.t
    )
    nomos_supp = evaluate_equation_support(nomos_out.coef != 0, Xi_true != 0)
    nomos_coef_err = evaluate_coefficient_error(nomos_out.coef, Xi_true)

    # Evaluate derivative prediction on test set
    test_theta = nomos_out.library.transform(test_traj.x)
    test_x_dot_pred = test_theta @ nomos_out.coef
    nomos_deriv = evaluate_derivative_prediction(test_x_dot_pred, test_traj.x_dot_true)

    # 5. Fit & evaluate OLS baseline
    train_x_all, train_x_dot_all = nomos_out.X_stacked, nomos_out.X_dot_estimated
    train_theta = nomos_out.library.transform(train_x_all)
    ols = OLSBaseline().fit(train_theta, train_x_dot_all)
    ols_coef_err = evaluate_coefficient_error(ols.coef_, Xi_true)
    ols_rollout = evaluate_rollout(ols.coef_, nomos_out.library, test_traj.x_clean, test_traj.t)
    ols_supp = evaluate_equation_support(np.abs(ols.coef_) > 1e-12, Xi_true != 0)

    # 6. Fit & evaluate PySINDy baseline (polynomial basis)
    pysindy_err = float("nan")
    pysindy_f1 = float("nan")
    pysindy_exact = False
    pysindy_rollout_rmse = float("nan")
    try:
        pysindy_adapter = PySINDyAdapter(threshold=eff_thresh, degree=2)
        pysindy_adapter.fit(
            train_x_all,
            t=np.linspace(0.0, 1.0, len(train_x_all)),
            x_dot=train_x_dot_all,
            feature_names=list(sys_obj.variable_names),
        )
        # If library degrees match polynomial
        if lib_type == "polynomial":
            ps_err_eval = evaluate_coefficient_error(pysindy_adapter.coef_, Xi_true)
            pysindy_err = ps_err_eval["relative_error"]
            ps_supp = evaluate_equation_support(pysindy_adapter.coef_ != 0, Xi_true != 0)
            pysindy_f1 = ps_supp["f1"]
            pysindy_exact = ps_supp["exact_match"]
            ps_rollout = evaluate_rollout(pysindy_adapter.coef_, nomos_out.library, test_traj.x_clean, test_traj.t)
            pysindy_rollout_rmse = ps_rollout.rmse
    except Exception as e:
        pass

    # Build discovered equations dict
    disc_eqs = {
        v: eq.raw_str for v, eq in nomos_out.discovered_system.equations.items()
    }
    true_eqs = sys_obj.ground_truth_symbolic()

    metrics = {
        "nomos_deriv_rmse": nomos_deriv["rmse"],
        "nomos_deriv_r2": nomos_deriv["r2"],
        "nomos_rollout_rmse": nomos_rollout.rmse if nomos_rollout.is_stable else 999.0,
        "nomos_rollout_rel_rmse": nomos_rollout.relative_rmse if nomos_rollout.is_stable else 999.0,
        "nomos_supp_precision": nomos_supp["precision"],
        "nomos_supp_recall": nomos_supp["recall"],
        "nomos_supp_f1": nomos_supp["f1"],
        "nomos_exact_match": nomos_supp["exact_match"],
        "nomos_coef_rel_err": nomos_coef_err["relative_error"],
        "nomos_active_coef_err": nomos_coef_err["active_relative_error"],
        "ols_coef_rel_err": ols_coef_err["relative_error"],
        "ols_rollout_rmse": ols_rollout.rmse if ols_rollout.is_stable else 999.0,
        "ols_supp_f1": ols_supp["f1"],
        "pysindy_coef_rel_err": pysindy_err,
        "pysindy_supp_f1": pysindy_f1,
        "pysindy_exact_match": pysindy_exact,
        "pysindy_rollout_rmse": pysindy_rollout_rmse,
    }

    manifest.finalize(metrics, disc_eqs, true_eqs)
    manifest.save(MANIFESTS_DIR / f"{manifest.manifest_id}.json")

    return {
        "system": sys_name,
        "noise_level": noise_level,
        "seed": seed,
        **metrics,
        "discovered_equations": str(disc_eqs),
    }


def main():
    print(f"Starting Project NOMOS M1 Benchmark Suite across {len(SYSTEMS)} systems, {len(NOISE_LEVELS)} noise levels, {len(SEEDS)} seeds (total {len(SYSTEMS)*len(NOISE_LEVELS)*len(SEEDS)} runs)...")
    start_time = time.time()

    all_results = []
    fieldnames = [
        "system",
        "noise_level",
        "seed",
        "nomos_deriv_rmse",
        "nomos_deriv_r2",
        "nomos_rollout_rmse",
        "nomos_rollout_rel_rmse",
        "nomos_supp_precision",
        "nomos_supp_recall",
        "nomos_supp_f1",
        "nomos_exact_match",
        "nomos_coef_rel_err",
        "nomos_active_coef_err",
        "ols_coef_rel_err",
        "ols_rollout_rmse",
        "ols_supp_f1",
        "pysindy_coef_rel_err",
        "pysindy_supp_f1",
        "pysindy_exact_match",
        "pysindy_rollout_rmse",
        "discovered_equations",
    ]

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for s_idx, sys_name in enumerate(SYSTEMS):
            for n_idx, noise in enumerate(NOISE_LEVELS):
                for seed in SEEDS:
                    print(f"[{time.strftime('%H:%M:%S')}] Running {sys_name:20s} | noise={noise:4.2f} | seed={seed}...", end="", flush=True)
                    res = run_single_experiment(sys_name, noise, seed)
                    writer.writerow(res)
                    f.flush()
                    all_results.append(res)
                    print(f" Done! Support F1={res['nomos_supp_f1']:.2f}, Exact={res['nomos_exact_match']}, CoefErr={res['nomos_active_coef_err']:.4f}")

    total_time = time.time() - start_time
    print(f"\nAll {len(all_results)} runs completed successfully in {total_time:.2f} seconds.")
    print(f"Results written to {CSV_PATH}")


if __name__ == "__main__":
    main()
