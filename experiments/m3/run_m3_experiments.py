"""
NOMOS Milestone M3 Comprehensive PDE Benchmark Suite
Executes controlled grid across 6 PDEs, 4 Methods, 3 Seeds, and 4 Noise Levels.
Produces audit/m3/RAW_EXPERIMENTS.csv and empirical validation metrics.
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import time
import csv
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

from nomos.pde.schema import Grid1D, TimeGrid, SpatiotemporalField
from nomos.pde.isolation import create_learner_field_observation
from nomos.pde.simulators.benchmarks import get_pde_simulator, generate_benchmark_initial_condition
from nomos.pde.strong_form import StrongFormPDEDiscovery
from nomos.pde.weak_form import WeakFormPDEDiscovery
from nomos.pde.symbolic_search import DifferentialBeamSearch


def run_benchmark_grid():
    out_dir = Path("audit/m3")
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "RAW_EXPERIMENTS.csv"

    pde_configs = [
        # 1. Heat Equation
        {
            "name": "heat_equation",
            "kwargs": {"alpha": 0.1},
            "domain": (0.0, 2.0 * np.pi),
            "N": 64,
            "M": 50,
            "t_span": (0.0, 1.0),
            "true_terms": {"u_xx": 0.1},
        },
        # 2. Linear Advection
        {
            "name": "linear_advection",
            "kwargs": {"c": 1.0},
            "domain": (0.0, 2.0 * np.pi),
            "N": 64,
            "M": 50,
            "t_span": (0.0, 1.0),
            "true_terms": {"u_x": -1.0},
        },
        # 3. Viscous Burgers'
        {
            "name": "viscous_burgers",
            "kwargs": {"nu": 0.05},
            "domain": (0.0, 2.0 * np.pi),
            "N": 64,
            "M": 50,
            "t_span": (0.0, 1.0),
            "true_terms": {"u*u_x": -1.0, "u_xx": 0.05},
        },
        # 4. KdV Equation (Dispersive Soliton)
        {
            "name": "kdv_equation",
            "kwargs": {"domain": (-10.0, 10.0)},
            "domain": (-10.0, 10.0),
            "N": 64,
            "M": 50,
            "t_span": (0.0, 0.5),
            "true_terms": {"u*u_x": -6.0, "u_xxx": -1.0},
        },
        # 5. Kuramoto-Sivashinsky (Chaotic PDE)
        {
            "name": "kuramoto_sivashinsky",
            "kwargs": {"domain": (0.0, 32.0 * np.pi)},
            "domain": (0.0, 32.0 * np.pi),
            "N": 64,
            "M": 50,
            "t_span": (0.0, 1.0),
            "true_terms": {"u*u_x": -1.0, "u_xx": -1.0, "u_xxxx": -1.0},
        },
    ]

    methods = [
        "StrongSINDy",
        "WeakSINDy",
        "PureBeam",
        "NeuralBeam",
    ]

    noise_levels = [0.0, 0.01, 0.05, 0.10]
    seeds = [42, 43, 44]

    fieldnames = [
        "run_id",
        "pde_name",
        "method",
        "noise_level",
        "random_seed",
        "discovered_equation",
        "is_exact_support",
        "mean_coefficient_error",
        "wall_clock_time_s",
        "surrogate_time_s",
        "num_evaluations",
        "residual_norm",
    ]

    results: List[Dict[str, Any]] = []
    run_idx = 0
    total_runs = len(pde_configs) * len(methods) * len(noise_levels) * len(seeds)

    print(f"Starting NOMOS M3 Controlled PDE Benchmark Grid ({total_runs} total runs)...")
    start_total_time = time.time()

    for pcfg in pde_configs:
        pde_name = pcfg["name"]
        sim = get_pde_simulator(pde_name, **pcfg["kwargs"])
        grid = Grid1D.create(pcfg["domain"], pcfg["N"], periodic=True)
        t_grid = TimeGrid.create(pcfg["t_span"], pcfg["M"])
        u0 = generate_benchmark_initial_condition(pde_name, grid.x, ic_type="default")

        for noise in noise_levels:
            for seed in seeds:
                # Generate simulation field
                raw_field = sim.simulate(u0, grid, t_grid, noise_level=noise, random_seed=seed)
                # Ensure ground-truth separation: create learner observation
                field_obs = create_learner_field_observation(raw_field)

                for method in methods:
                    run_idx += 1
                    t_start = time.time()

                    disc_res = None
                    surr_time = 0.0

                    if method == "StrongSINDy":
                        engine = StrongFormPDEDiscovery(
                            threshold=0.04,
                            diff_method="fd",
                            filter_window=7 if noise > 0.01 else None,
                        )
                        disc_res = engine.fit(field_obs)

                    elif method == "WeakSINDy":
                        engine = WeakFormPDEDiscovery(
                            num_test_functions=80,
                            threshold=0.04,
                            random_seed=seed,
                        )
                        disc_res = engine.fit(field_obs)

                    elif method == "PureBeam":
                        engine = DifferentialBeamSearch(
                            use_neural_guidance=False,
                            random_seed=seed,
                        )
                        disc_res = engine.fit(field_obs)

                    elif method == "NeuralBeam":
                        engine = DifferentialBeamSearch(
                            use_neural_guidance=True,
                            surrogate_epochs=30,
                            random_seed=seed,
                        )
                        disc_res = engine.fit(field_obs)
                        surr_time = disc_res.metadata.get("surrogate_training_time", 0.0)

                    wall_time = time.time() - t_start

                    # Check exact support recovery
                    true_terms = pcfg["true_terms"]
                    disc_terms = disc_res.coefficients

                    # Check if keys match
                    # Normalize key matching (e.g. u*u_x vs u_x*u)
                    exact_support = set(disc_terms.keys()) == set(true_terms.keys())

                    coeff_errors = []
                    for k, true_val in true_terms.items():
                        if k in disc_terms:
                            rel_err = abs(disc_terms[k] - true_val) / (abs(true_val) + 1e-8)
                            coeff_errors.append(rel_err)
                        else:
                            coeff_errors.append(1.0)
                    mean_coeff_err = float(np.mean(coeff_errors)) if coeff_errors else 1.0

                    row = {
                        "run_id": run_idx,
                        "pde_name": pde_name,
                        "method": method,
                        "noise_level": noise,
                        "random_seed": seed,
                        "discovered_equation": disc_res.discovered_equation,
                        "is_exact_support": exact_support,
                        "mean_coefficient_error": round(mean_coeff_err, 4),
                        "wall_clock_time_s": round(wall_time, 4),
                        "surrogate_time_s": round(surr_time, 4),
                        "num_evaluations": disc_res.num_evaluations,
                        "residual_norm": round(disc_res.residual_norm, 6),
                    }
                    results.append(row)

                    if run_idx % 20 == 0 or run_idx == total_runs:
                        status_str = "EXACT" if exact_support else "DIFF"
                        print(
                            f"[{run_idx:03d}/{total_runs}] {pde_name:<20} | {method:<12} | "
                            f"n={int(noise*100):02d}% | s={seed} | {status_str:<6} | "
                            f"err={mean_coeff_err:.3f} | time={wall_time:.2f}s"
                        )

    # Write CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    total_duration = time.time() - start_total_time
    print(f"\nAll {total_runs} PDE runs completed in {total_duration:.1f}s ({total_duration/60:.2f} min).")
    print(f"Results saved to: {csv_path}")


if __name__ == "__main__":
    run_benchmark_grid()
