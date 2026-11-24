"""
NOMOS Milestone M5 Comprehensive Closed-Loop Experimentation Benchmark Matrix
Executes controlled paired trials across:
- Systems: KdV, Viscous Burgers, Gray-Scott 2D, FitzHugh-Nagumo 2D, Navier-Stokes 2D
- Strategies: random, fixed, greedy_disagreement, cost_normalized, uncertainty_aware
- Noise Levels: 0%, 1%, 5%, 10%
- Seeds: 42, 43, 44, 45, 46
Produces audit/m5/RAW_EPISODES.csv, PAIRED_OUTCOMES.csv, and summary tables.
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

# 1D Simulators
from nomos.pde.simulators.burgers import BurgersSimulator
from nomos.pde.simulators.kdv import KdVSimulator

# 2D Simulators
from nomos.pde.simulators.gray_scott import GrayScottSimulator
from nomos.pde.simulators.fitzhugh_nagumo import FitzHughNagumoSimulator
from nomos.pde.simulators.navier_stokes_2d import NavierStokes2DSimulator


def build_kdv_pool(sim: KdVSimulator, grid: Grid1D) -> List[Tuple[str, np.ndarray, float]]:
    x = grid.x
    u0_single = sim.analytical_1soliton(x, 0.0, c=2.0)
    u0_shifted = sim.analytical_1soliton(x, 0.0, c=2.0, x0=1.5)
    u0_2soliton = sim.analytical_1soliton(x, 0.0, c=4.0, x0=-4.0) + sim.analytical_1soliton(x, 0.0, c=2.0, x0=2.0)
    u0_packet = np.exp(-(x**2) / 4.0) * np.cos(2.0 * x)
    u0_multi = 0.8 * np.sin(np.pi * x / 10.0) + 0.4 * np.cos(2.0 * np.pi * x / 10.0)
    return [
        ("single_soliton", u0_single, 1.0),
        ("shifted_soliton", u0_shifted, 1.0),
        ("2soliton_collision", u0_2soliton, 1.2),
        ("wave_packet", u0_packet, 1.2),
        ("multi_harmonic", u0_multi, 1.0),
    ]


def build_burgers_pool(sim: BurgersSimulator, grid: Grid1D) -> List[Tuple[str, np.ndarray, float]]:
    x = grid.x
    u0_sin = np.sin(x)
    u0_flat = 0.1 * np.sin(x)  # weak advection, quasi-linear
    u0_steep = np.exp(-((x - np.pi)**2) / 0.5)
    u0_multi = np.sin(x) + 0.5 * np.cos(2.0 * x)
    return [
        ("flat_wave", u0_flat, 1.0),
        ("sine_wave", u0_sin, 1.0),
        ("steep_pulse", u0_steep, 1.2),
        ("multi_harmonic", u0_multi, 1.1),
    ]


def build_gray_scott_pool(sim: GrayScottSimulator, grid: Grid2D) -> List[Tuple[str, np.ndarray, float]]:
    u0_default = sim.default_initial_condition(grid)
    # Homogeneous background (zero reaction dynamics)
    u0_homog = np.stack([np.ones((grid.num_points_x, grid.num_points_y)), np.zeros((grid.num_points_x, grid.num_points_y))], axis=-1)
    # Dual spot perturbation
    X, Y = grid.meshgrid
    u2 = np.ones((grid.num_points_x, grid.num_points_y))
    v2 = np.zeros((grid.num_points_x, grid.num_points_y))
    mask1 = (np.abs(X - 0.8) < 0.2) & (np.abs(Y - 0.8) < 0.2)
    mask2 = (np.abs(X - 1.7) < 0.2) & (np.abs(Y - 1.7) < 0.2)
    u2[mask1 | mask2] = 0.5
    v2[mask1 | mask2] = 0.25
    u0_dual = np.stack([u2, v2], axis=-1)
    return [
        ("homogeneous_unreactive", u0_homog, 1.0),
        ("single_spot", u0_default, 1.2),
        ("dual_spots", u0_dual, 1.5),
    ]


def build_fitzhugh_nagumo_pool(sim: FitzHughNagumoSimulator, grid: Grid2D) -> List[Tuple[str, np.ndarray, float]]:
    u0_default = sim.default_initial_condition(grid)
    # Sub-threshold unexcited state
    u0_quiet = np.stack([np.zeros((grid.num_points_x, grid.num_points_y)), np.zeros((grid.num_points_x, grid.num_points_y))], axis=-1)
    # Localized center pulse
    X, Y = grid.meshgrid
    u_pulse = np.where(X**2 + Y**2 < 4.0, 1.5, -1.0)
    v_pulse = np.zeros_like(u_pulse)
    u0_pulse = np.stack([u_pulse, v_pulse], axis=-1)
    return [
        ("subthreshold_quiet", u0_quiet, 1.0),
        ("broken_front", u0_default, 1.2),
        ("center_pulse", u0_pulse, 1.2),
    ]


def build_navier_stokes_pool(sim: NavierStokes2DSimulator, grid: Grid2D) -> List[Tuple[str, np.ndarray, float]]:
    # 1. Taylor-Green (advection is identically 0)
    _, _, _, om_tg = sim.taylor_green_solution(grid.x, grid.y, 0.0)
    # 2. Vortex Merger (strong active non-zero convective advection)
    X, Y = grid.meshgrid
    om_merger = np.exp(-((X - 2.5)**2 + (Y - 3.14)**2) / 0.5) + np.exp(-((X - 3.7)**2 + (Y - 3.14)**2) / 0.5)
    # 3. Vortex Dipole
    om_dipole = np.exp(-((X - 2.5)**2 + (Y - 3.14)**2) / 0.5) - np.exp(-((X - 3.7)**2 + (Y - 3.14)**2) / 0.5)
    return [
        ("taylor_green_zero_advection", om_tg, 1.0),
        ("vortex_merger_active", om_merger, 1.5),
        ("vortex_dipole_active", om_dipole, 1.5),
    ]


def run_all_m5_benchmarks():
    out_dir = Path("audit/m5")
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_csv = out_dir / "RAW_EPISODES.csv"
    paired_csv = out_dir / "PAIRED_OUTCOMES.csv"
    noise_csv = out_dir / "NOISE_ROBUSTNESS.csv"
    gen_csv = out_dir / "GENERALIZATION.csv"

    print("Executing Milestone M5 Autonomous Closed-Loop Benchmark Suite...")
    t_start = time.time()

    # Grid specifications
    g1d_kdv = Grid1D.create((-10.0, 10.0), 128)
    sim_kdv = KdVSimulator(domain=(-10.0, 10.0))

    g1d_burg = Grid1D.create((0.0, 2.0 * np.pi), 64)
    sim_burg = BurgersSimulator(nu=0.05)

    g2d_gs = Grid2D.create((0.0, 2.5), (0.0, 2.5), 32, 32)
    sim_gs = GrayScottSimulator(D_u=0.16, D_v=0.08, F=0.035, k=0.060)

    g2d_fhn = Grid2D.create((-10.0, 10.0), (-10.0, 10.0), 32, 32)
    sim_fhn = FitzHughNagumoSimulator(D_u=1.0, D_v=0.0, eps=0.05, a1=0.5, a0=0.0)

    g2d_ns = Grid2D.create((0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi), 32, 32)
    sim_ns = NavierStokes2DSimulator(nu=0.02)

    systems = [
        ("kdv_equation", sim_kdv, g1d_kdv, build_kdv_pool(sim_kdv, g1d_kdv), 1, "u", ["u*u_x", "u_xxx", "u_x"], {"u*u_x": -6.0, "u_xxx": -1.0}),
        ("viscous_burgers", sim_burg, g1d_burg, build_burgers_pool(sim_burg, g1d_burg), 1, "u", ["u*u_x", "u_xx"], {"u*u_x": -1.0, "u_xx": 0.05}),
        ("gray_scott_2d", sim_gs, g2d_gs, build_gray_scott_pool(sim_gs, g2d_gs), 2, "v", ["lap_v", "u*v^2", "v"], {"lap_v": 0.08, "u*v^2": 1.0, "v": -0.095}),
        ("fitzhugh_nagumo_2d", sim_fhn, g2d_fhn, build_fitzhugh_nagumo_pool(sim_fhn, g2d_fhn), 2, "u", ["lap_u", "u", "u^3", "v"], {"lap_u": 1.0, "u": 1.0, "u^3": -1.0, "v": -1.0}),
        ("navier_stokes_2d", sim_ns, g2d_ns, build_navier_stokes_pool(sim_ns, g2d_ns), 2, "omega", ["lap_omega", "advection_omega"], {"lap_omega": 0.02, "advection_omega": -1.0}),
    ]

    strategies = [
        AcquisitionStrategy.RANDOM,
        AcquisitionStrategy.FIXED,
        AcquisitionStrategy.GREEDY_DISAGREEMENT,
        AcquisitionStrategy.COST_NORMALIZED,
        AcquisitionStrategy.UNCERTAINTY_AWARE,
    ]

    seeds = [42, 43, 44, 45, 46]
    noise_levels = [0.0, 0.01, 0.05, 0.10]
    max_budget = 4

    episodes_records: List[Dict[str, Any]] = []
    paired_records: List[Dict[str, Any]] = []

    episode_id = 0

    # Execute canonical paired benchmark: for each system, noise, seed, compare strategies
    for sys_name, sim, grid, pool, dim, target_chan, cand_lib, true_terms in systems:
        for noise in noise_levels:
            for seed in seeds:
                matched_runs: Dict[str, InvestigationEpisode] = {}

                for strat in strategies:
                    episode_id += 1
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
                    matched_runs[strat.value] = ep

                    # Check success: true terms recovered
                    is_exact = False
                    winning_eq = ""
                    if ep.winning_hypothesis is not None:
                        winning_eq = ep.winning_hypothesis.equation_str
                        wh_keys = set(ep.winning_hypothesis.parameters.keys())
                        true_keys = set(true_terms.keys())
                        if true_keys == wh_keys:
                            is_exact = True
                        elif true_keys.issubset(wh_keys):
                            extra = wh_keys - true_keys
                            if all(abs(ep.winning_hypothesis.parameters[k]) < 0.04 for k in extra):
                                is_exact = True

                    episodes_records.append({
                        "episode_id": episode_id,
                        "system": sys_name,
                        "strategy": strat.value,
                        "noise_level": noise,
                        "random_seed": seed,
                        "status": ep.status.value,
                        "winning_equation": winning_eq,
                        "is_exact_recovery": 1 if is_exact else 0,
                        "experiments_queried": ep.total_cost.trajectory_queries,
                        "observation_volume": round(ep.total_cost.observation_volume, 4),
                        "compute_time_s": round(ep.duration_seconds, 4),
                        "steps_taken": len(ep.trace),
                    })

                # Compute paired comparison between Active (greedy disagreement) and Baselines (fixed, random)
                ep_active = matched_runs[AcquisitionStrategy.GREEDY_DISAGREEMENT.value]
                ep_fixed = matched_runs[AcquisitionStrategy.FIXED.value]
                ep_random = matched_runs[AcquisitionStrategy.RANDOM.value]

                def check_rec(ep):
                    if ep.winning_hypothesis is None:
                        return 0
                    wh_keys = set(ep.winning_hypothesis.parameters.keys())
                    true_keys = set(true_terms.keys())
                    if true_keys == wh_keys:
                        return 1
                    if true_keys.issubset(wh_keys):
                        extra = wh_keys - true_keys
                        if all(abs(ep.winning_hypothesis.parameters[k]) < 0.04 for k in extra):
                            return 1
                    return 0

                rec_active = check_rec(ep_active)
                rec_fixed = check_rec(ep_fixed)
                rec_random = check_rec(ep_random)

                paired_records.append({
                    "system": sys_name,
                    "noise_level": noise,
                    "random_seed": seed,
                    "active_recovered": rec_active,
                    "fixed_recovered": rec_fixed,
                    "random_recovered": rec_random,
                    "active_queries": ep_active.total_cost.trajectory_queries,
                    "fixed_queries": ep_fixed.total_cost.trajectory_queries,
                    "random_queries": ep_random.total_cost.trajectory_queries,
                    "active_beats_fixed": 1 if (rec_active > rec_fixed or (rec_active == rec_fixed == 1 and ep_active.total_cost.trajectory_queries < ep_fixed.total_cost.trajectory_queries)) else 0,
                })

    # Save RAW_EPISODES.csv
    with open(raw_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(episodes_records[0].keys()))
        writer.writeheader()
        writer.writerows(episodes_records)

    # Save PAIRED_OUTCOMES.csv
    with open(paired_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired_records[0].keys()))
        writer.writeheader()
        writer.writerows(paired_records)

    print(f"Total investigation episodes completed: {len(episodes_records)} in {time.time() - t_start:.2f}s")
    print(f"Saved RAW_EPISODES.csv to {raw_csv}")
    print(f"Saved PAIRED_OUTCOMES.csv to {paired_csv}")

    # Generate NOISE_ROBUSTNESS.csv (grouped by strategy & noise level)
    noise_agg: Dict[Tuple[str, float], List[Dict[str, Any]]] = {}
    for r in episodes_records:
        key = (r["strategy"], r["noise_level"])
        if key not in noise_agg:
            noise_agg[key] = []
        noise_agg[key].append(r)

    noise_records = []
    for (strat_k, nl_k), group in sorted(noise_agg.items()):
        rec_list = [g["is_exact_recovery"] for g in group]
        queries_list = [g["experiments_queried"] for g in group]
        noise_records.append({
            "strategy": strat_k,
            "noise_level": nl_k,
            "total_trials": len(group),
            "exact_recovery_rate": round(float(np.mean(rec_list)), 4),
            "mean_queries_to_stop": round(float(np.mean(queries_list)), 2),
        })

    with open(noise_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(noise_records[0].keys()))
        writer.writeheader()
        writer.writerows(noise_records)
    print(f"Saved NOISE_ROBUSTNESS.csv to {noise_csv}")

    # Generate GENERALIZATION.csv (grouped by system & strategy)
    gen_agg: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for r in episodes_records:
        key = (r["system"], r["strategy"])
        if key not in gen_agg:
            gen_agg[key] = []
        gen_agg[key].append(r)

    gen_records = []
    for (sys_k, strat_k), group in sorted(gen_agg.items()):
        rec_list = [g["is_exact_recovery"] for g in group]
        queries_list = [g["experiments_queried"] for g in group]
        time_list = [g["compute_time_s"] for g in group]
        gen_records.append({
            "system": sys_k,
            "strategy": strat_k,
            "total_trials": len(group),
            "exact_recovery_rate": round(float(np.mean(rec_list)), 4),
            "mean_queries": round(float(np.mean(queries_list)), 2),
            "mean_time_seconds": round(float(np.mean(time_list)), 4),
        })

    with open(gen_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(gen_records[0].keys()))
        writer.writeheader()
        writer.writerows(gen_records)
    print(f"Saved GENERALIZATION.csv to {gen_csv}")


if __name__ == "__main__":
    run_all_m5_benchmarks()
