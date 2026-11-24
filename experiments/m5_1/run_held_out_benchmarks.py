"""
NOMOS Milestone M5.1:
Held-out Physical Systems Benchmark & Strong Baseline Comparison Matrix.
Evaluates:
- Systems: Brusselator 2D, Cahn–Hilliard 1D
- Strategies:
    * Active: greedy_disagreement, cost_normalized
    * Passive: fixed, random
    * Strong Baselines: uncertainty_aware, model_discrimination, handcrafted_schedule
- Noise levels: 0.0, 0.01, 0.05, 0.10
- Seeds: 42, 43, 44, 45, 46
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import time
import csv
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np

from nomos.pde.schema import Grid1D, Grid2D, TimeGrid, SpatiotemporalField
from nomos.closed_loop.oracle import SimulationOracle
from nomos.closed_loop.acquisition import AcquisitionStrategy
from nomos.closed_loop.controller import ClosedLoopController, InvestigationEpisode
from nomos.closed_loop.diagnostics import IdentifiabilityStatus

# Held-Out Simulators
from nomos.pde.simulators.brusselator import Brusselator2DSimulator
from nomos.pde.simulators.cahn_hilliard import CahnHilliard1DSimulator


def build_brusselator_pool(sim: Brusselator2DSimulator, grid: Grid2D) -> List[Tuple[str, np.ndarray, float]]:
    X, Y = grid.meshgrid
    # 1. Homogeneous steady state: u = A = 1.0, v = B/A = 3.0 (reaction terms balance to zero)
    u_ss = np.full((grid.num_points_x, grid.num_points_y), sim.A, dtype=np.float64)
    v_ss = np.full((grid.num_points_x, grid.num_points_y), sim.B / sim.A, dtype=np.float64)
    u0_steady = np.stack([u_ss, v_ss], axis=-1)

    # 2. Localized spot perturbation
    u0_spot = sim.default_initial_condition(grid)

    # 3. Multi-mode Turing wave packet
    pert = 0.4 * np.sin(2.0 * X) * np.cos(2.0 * Y) + 0.2 * np.cos(3.0 * X) * np.sin(3.0 * Y)
    u0_turing = np.stack([u_ss + pert, v_ss - pert], axis=-1)

    return [
        ("homogeneous_quiescent", u0_steady, 1.0),
        ("localized_spot", u0_spot, 1.2),
        ("turing_wave_packet", u0_turing, 1.5),
    ]


def build_cahn_hilliard_pool(sim: CahnHilliard1DSimulator, grid: Grid1D) -> List[Tuple[str, np.ndarray, float]]:
    x = grid.x
    # 1. Flat quiescent near-homogeneous state (minimal gradient activity)
    u0_flat = 0.02 * np.sin(x)

    # 2. Spinodal multi-mode perturbation (drives phase separation)
    u0_spinodal = 0.15 * np.cos(2.0 * x) + 0.10 * np.sin(5.0 * x)

    # 3. Sharp domain interface (interfacial tension and curvature flow)
    x_mid = 0.5 * (x[0] + x[-1])
    u0_interface = np.tanh((x - x_mid) / 0.25)

    return [
        ("flat_quiescent", u0_flat, 1.0),
        ("spinodal_modes", u0_spinodal, 1.2),
        ("steep_interface", u0_interface, 1.5),
    ]


def run_held_out_benchmarks():
    out_dir = Path("audit/m5_1")
    out_dir.mkdir(parents=True, exist_ok=True)
    bench_csv = out_dir / "HELD_OUT_BENCHMARKS.csv"
    strong_csv = out_dir / "STRONG_BASELINES.csv"

    print("Running NOMOS M5.1 Held-Out System & Strong Baseline Benchmark Suite...")
    t_start = time.time()

    # Grids
    g2d_bruss = Grid2D.create((0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi), 24, 24)
    sim_bruss = Brusselator2DSimulator(D_u=0.1, D_v=0.05, A=1.0, B=3.0)

    g1d_ch = Grid1D.create((0.0, 2.0 * np.pi), 64)
    sim_ch = CahnHilliard1DSimulator(gamma=1.0, epsilon=0.05)

    # System configurations
    # Brusselator u channel: u_t = 0.1*lap_u - 4.0*u + 1.0*u^2*v + 1.0*1
    systems = [
        (
            "brusselator_2d",
            sim_bruss,
            g2d_bruss,
            build_brusselator_pool(sim_bruss, g2d_bruss),
            2,
            "u",
            ["lap_u", "u", "u^2*v", "1"],
            {"lap_u": 0.1, "u": -4.0, "u^2*v": 1.0, "1": 1.0},
        ),
        (
            "cahn_hilliard",
            sim_ch,
            g1d_ch,
            build_cahn_hilliard_pool(sim_ch, g1d_ch),
            1,
            "u",
            ["u_xx", "(u^3)_xx", "u_xxxx"],
            {"u_xx": -1.0, "(u^3)_xx": 1.0, "u_xxxx": -0.0025},
        ),
    ]

    strategies = [
        AcquisitionStrategy.GREEDY_DISAGREEMENT,
        AcquisitionStrategy.COST_NORMALIZED,
        AcquisitionStrategy.FIXED,
        AcquisitionStrategy.RANDOM,
        AcquisitionStrategy.UNCERTAINTY_AWARE,
        AcquisitionStrategy.MODEL_DISCRIMINATION,
        AcquisitionStrategy.HANDCRAFTED_SCHEDULE,
    ]

    seeds = [42, 43, 44, 45, 46]
    noise_levels = [0.0, 0.01, 0.05, 0.10]
    max_budget = 4

    all_records: List[Dict[str, Any]] = []

    for sys_name, sim, grid, pool, dim, target_chan, cand_lib, true_terms in systems:
        print(f"Benchmarking held-out system: {sys_name}...", flush=True)
        for noise in noise_levels:
            for seed in seeds:
                for strat in strategies:
                    oracle = SimulationOracle(sim, grid)
                    controller = ClosedLoopController(
                        oracle=oracle,
                        grid=grid,
                        candidate_experiment_pool=pool,
                        strategy=strat,
                        max_budget=max_budget,
                        noise_level=noise,
                        random_seed=seed,
                        dimension=dim,
                        target_channel=target_chan,
                        candidate_library=cand_lib,
                    )
                    ep = controller.run_investigation()

                    # Exact recovery check
                    is_exact = False
                    param_error = 1.0
                    winning_eq = ""
                    if ep.winning_hypothesis is not None:
                        winning_eq = ep.winning_hypothesis.equation_str
                        wh_keys = set(ep.winning_hypothesis.parameters.keys())
                        true_keys = set(true_terms.keys())
                        if wh_keys == true_keys and len(wh_keys) > 0:
                            errs = [
                                abs(ep.winning_hypothesis.parameters[k] - true_terms[k]) / (abs(true_terms[k]) + 1e-6)
                                for k in true_keys
                            ]
                            param_error = float(np.mean(errs))
                            if param_error < 0.25:
                                is_exact = True

                    rec = {
                        "system": sys_name,
                        "strategy": strat.value,
                        "noise_level": noise,
                        "seed": seed,
                        "status": ep.status.value,
                        "queries": ep.total_cost.trajectory_queries,
                        "exact_recovery": is_exact,
                        "param_error": round(param_error, 5),
                        "duration_s": round(ep.duration_seconds, 3),
                        "winning_equation": winning_eq,
                    }
                    all_records.append(rec)

    # Write out HELD_OUT_BENCHMARKS.csv
    with open(bench_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_records[0].keys()))
        writer.writeheader()
        writer.writerows(all_records)

    # Write out STRONG_BASELINES summary
    # Aggregated recovery rate by strategy and system
    strat_summary = {}
    for r in all_records:
        key = (r["system"], r["strategy"])
        if key not in strat_summary:
            strat_summary[key] = {"total": 0, "recovered": 0, "queries": 0.0, "time_s": 0.0}
        strat_summary[key]["total"] += 1
        if r["exact_recovery"]:
            strat_summary[key]["recovered"] += 1
        strat_summary[key]["queries"] += r["queries"]
        strat_summary[key]["time_s"] += r["duration_s"]

    strong_records = []
    for (sys_name, strat), v in sorted(strat_summary.items()):
        rec_rate = v["recovered"] / v["total"]
        avg_q = v["queries"] / v["total"]
        avg_t = v["time_s"] / v["total"]
        strong_records.append({
            "system": sys_name,
            "strategy": strat,
            "total_runs": v["total"],
            "exact_recoveries": v["recovered"],
            "recovery_rate": round(rec_rate, 4),
            "mean_queries": round(avg_q, 3),
            "mean_duration_s": round(avg_t, 3),
        })

    with open(strong_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(strong_records[0].keys()))
        writer.writeheader()
        writer.writerows(strong_records)

    total_time = round(time.time() - t_start, 2)
    print(f"Held-out & strong baseline benchmarks completed in {total_time}s across {len(all_records)} episodes.")
    return all_records, strong_records


if __name__ == "__main__":
    run_held_out_benchmarks()
