"""
NOMOS Milestone M5.3: Zero-Leakage Blind Scientific Replication Benchmark Matrix
Category B: Blind Equation Identification with Distractor Libraries.
Executes matched paired trials across:
- Primary Systems: KdV, Viscous Burgers, Gray-Scott 2D, FitzHugh-Nagumo 2D, Navier-Stokes 2D
- Held-Out Systems: Brusselator 2D, Cahn-Hilliard 1D
- Strategies: greedy_disagreement (Active), cost_normalized (Active), random (Passive), fixed (Passive)
- Noise Levels: 0%, 1%, 5%, 10%
- Matched Seeds: 42, 43, 44, 45, 46
Generates audit/m5_3/BLIND_RAW_EPISODES.csv and BLIND_PAIRED_OUTCOMES.csv.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, os.getcwd())
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import time
import csv
from typing import Dict, List, Any, Tuple
import numpy as np

from nomos.pde.schema import Grid1D, Grid2D, TimeGrid, SpatiotemporalField
from nomos.closed_loop.oracle import SimulationOracle
from nomos.closed_loop.acquisition import AcquisitionStrategy
from nomos.closed_loop.controller import ClosedLoopController, InvestigationEpisode
from nomos.closed_loop.diagnostics import IdentifiabilityStatus
from experiments.m5_3.reconcile_metrics import evaluate_hypothesis_tier

# 1D Simulators
from nomos.pde.simulators.burgers import BurgersSimulator
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.pde.simulators.cahn_hilliard import CahnHilliard1DSimulator

# 2D Simulators
from nomos.pde.simulators.gray_scott import GrayScottSimulator
from nomos.pde.simulators.fitzhugh_nagumo import FitzHughNagumoSimulator
from nomos.pde.simulators.navier_stokes_2d import NavierStokes2DSimulator
from nomos.pde.simulators.brusselator import Brusselator2DSimulator

# Pools from m5 & m5_1
from experiments.m5.run_m5_benchmarks import (
    build_kdv_pool,
    build_burgers_pool,
    build_gray_scott_pool,
    build_fitzhugh_nagumo_pool,
    build_navier_stokes_pool,
)
from experiments.m5_1.run_held_out_benchmarks import (
    build_brusselator_pool,
    build_cahn_hilliard_pool,
)


def run_blind_replication_suite():
    out_dir = Path("audit/m5_3")
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_csv = out_dir / "BLIND_RAW_EPISODES.csv"
    paired_csv = out_dir / "BLIND_PAIRED_OUTCOMES.csv"

    print("Starting Milestone M5.3 Blind Replication Benchmark Suite...")
    t_start = time.time()

    # Grids & Simulators
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

    # Held-out simulators
    g2d_bruss = Grid2D.create((0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi), 24, 24)
    sim_bruss = Brusselator2DSimulator(D_u=0.1, D_v=0.05, A=1.0, B=3.0)

    g1d_ch = Grid1D.create((-10.0, 10.0), 128)
    sim_ch = CahnHilliard1DSimulator(gamma=1.0, epsilon=0.05)

    # Primary Benchmark Systems with OVERCOMPLETE Candidate Libraries containing distractors
    primary_systems = [
        ("kdv", sim_kdv, g1d_kdv, build_kdv_pool(sim_kdv, g1d_kdv), 1, "u", ["u*u_x", "u_xxx", "u_x", "u_xx", "u_xxxx"]),
        ("burgers", sim_burg, g1d_burg, build_burgers_pool(sim_burg, g1d_burg), 1, "u", ["u*u_x", "u_xx", "u_xxx", "u_x", "u_xxxx"]),
        ("gray_scott", sim_gs, g2d_gs, build_gray_scott_pool(sim_gs, g2d_gs), 2, "v", ["lap_v", "u*v^2", "v", "u", "1"]),
        ("fitzhugh", sim_fhn, g2d_fhn, build_fitzhugh_nagumo_pool(sim_fhn, g2d_fhn), 2, "u", ["lap_u", "u", "u^3", "v", "1", "lap_v"]),
        ("navier_stokes", sim_ns, g2d_ns, build_navier_stokes_pool(sim_ns, g2d_ns), 2, "omega", ["lap_omega", "advection_omega", "1", "omega"]),
    ]

    # Held-Out Benchmark Systems
    held_out_systems = [
        ("brusselator", sim_bruss, g2d_bruss, build_brusselator_pool(sim_bruss, g2d_bruss), 2, "u", ["lap_u", "1", "u", "u^2*v", "v", "lap_v"]),
        ("cahn_hilliard", sim_ch, g1d_ch, build_cahn_hilliard_pool(sim_ch, g1d_ch), 1, "u", ["u_xx", "(u^3)_xx", "u_xxxx", "u_x", "u*u_x"]),
    ]

    strategies = [
        AcquisitionStrategy.GREEDY_DISAGREEMENT,
        AcquisitionStrategy.COST_NORMALIZED,
        AcquisitionStrategy.RANDOM,
        AcquisitionStrategy.FIXED,
    ]

    seeds = [42, 43, 44, 45, 46]
    noise_levels = [0.0, 0.01, 0.05, 0.10]
    max_budget = 4

    episodes_records: List[Dict[str, Any]] = []
    paired_records: List[Dict[str, Any]] = []
    episode_id = 0

    print("Running Primary Systems Benchmark Matrix (5 systems x 4 noise x 5 seeds x 4 strategies = 400 episodes)...")

    for sys_key, sim, grid, pool, dim, target_chan, cand_lib in primary_systems:
        print(f"  -> System: {sys_key}")
        for noise in noise_levels:
            for seed in seeds:
                matched_runs: Dict[str, Tuple[InvestigationEpisode, int, float]] = {}

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
                    
                    # Evaluate Recovery Tier
                    params = ep.winning_hypothesis.parameters if ep.winning_hypothesis else None
                    tier, tier_name, max_err = evaluate_hypothesis_tier(sys_key, params)
                    is_tier1 = 1 if tier == 1 else 0

                    matched_runs[strat.value] = (ep, tier, max_err)

                    winning_eq = ep.winning_hypothesis.equation_str if ep.winning_hypothesis else "NONE"

                    episodes_records.append({
                        "episode_id": episode_id,
                        "benchmark_type": "PRIMARY",
                        "system": sys_key,
                        "strategy": strat.value,
                        "noise_level": noise,
                        "random_seed": seed,
                        "status": ep.status.value,
                        "winning_equation": winning_eq,
                        "tier": tier,
                        "tier_name": tier_name,
                        "is_tier1_strict": is_tier1,
                        "max_parameter_rel_error": round(max_err, 6) if max_err < 100.0 else -1.0,
                        "experiments_queried": ep.total_cost.trajectory_queries,
                        "observation_volume": round(ep.total_cost.observation_volume, 4),
                        "compute_time_s": round(ep.duration_seconds, 4),
                        "steps_taken": len(ep.trace),
                    })

                # Paired outcome comparison (Greedy Disagreement vs Random)
                ep_greedy, tier_greedy, _ = matched_runs[AcquisitionStrategy.GREEDY_DISAGREEMENT.value]
                ep_random, tier_random, _ = matched_runs[AcquisitionStrategy.RANDOM.value]
                ep_fixed, tier_fixed, _ = matched_runs[AcquisitionStrategy.FIXED.value]
                ep_cost, tier_cost, _ = matched_runs[AcquisitionStrategy.COST_NORMALIZED.value]

                g_win = 1 if tier_greedy == 1 else 0
                r_win = 1 if tier_random == 1 else 0
                f_win = 1 if tier_fixed == 1 else 0
                c_win = 1 if tier_cost == 1 else 0

                paired_records.append({
                    "system": sys_key,
                    "noise_level": noise,
                    "random_seed": seed,
                    "greedy_tier": tier_greedy,
                    "random_tier": tier_random,
                    "fixed_tier": tier_fixed,
                    "cost_tier": tier_cost,
                    "greedy_tier1": g_win,
                    "random_tier1": r_win,
                    "fixed_tier1": f_win,
                    "cost_tier1": c_win,
                    "greedy_queries": ep_greedy.total_cost.trajectory_queries,
                    "random_queries": ep_random.total_cost.trajectory_queries,
                    "fixed_queries": ep_fixed.total_cost.trajectory_queries,
                    "cost_queries": ep_cost.total_cost.trajectory_queries,
                    "contingency_cell_greedy_vs_random": f"{g_win}{r_win}",
                    "contingency_cell_greedy_vs_fixed": f"{g_win}{f_win}",
                })

    print("Running Held-Out Replication Systems (2 systems x 4 noise x 5 seeds x 2 strategies = 80 episodes)...")
    for sys_key, sim, grid, pool, dim, target_chan, cand_lib in held_out_systems:
        print(f"  -> Held-Out System: {sys_key}")
        for noise in noise_levels:
            for seed in seeds:
                for strat in [AcquisitionStrategy.GREEDY_DISAGREEMENT, AcquisitionStrategy.RANDOM]:
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
                    params = ep.winning_hypothesis.parameters if ep.winning_hypothesis else None
                    tier, tier_name, max_err = evaluate_hypothesis_tier(sys_key, params)
                    is_tier1 = 1 if tier == 1 else 0
                    winning_eq = ep.winning_hypothesis.equation_str if ep.winning_hypothesis else "NONE"

                    episodes_records.append({
                        "episode_id": episode_id,
                        "benchmark_type": "HELD_OUT",
                        "system": sys_key,
                        "strategy": strat.value,
                        "noise_level": noise,
                        "random_seed": seed,
                        "status": ep.status.value,
                        "winning_equation": winning_eq,
                        "tier": tier,
                        "tier_name": tier_name,
                        "is_tier1_strict": is_tier1,
                        "max_parameter_rel_error": round(max_err, 6) if max_err < 100.0 else -1.0,
                        "experiments_queried": ep.total_cost.trajectory_queries,
                        "observation_volume": round(ep.total_cost.observation_volume, 4),
                        "compute_time_s": round(ep.duration_seconds, 4),
                        "steps_taken": len(ep.trace),
                    })

    # Save CSV files
    print(f"Writing {len(episodes_records)} episode records to {raw_csv}...")
    with open(raw_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(episodes_records[0].keys()))
        writer.writeheader()
        writer.writerows(episodes_records)

    print(f"Writing {len(paired_records)} matched paired records to {paired_csv}...")
    with open(paired_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired_records[0].keys()))
        writer.writeheader()
        writer.writerows(paired_records)

    elapsed = time.time() - t_start
    print(f"Milestone M5.3 Benchmark Suite Completed in {elapsed:.2f} seconds ({len(episodes_records)} total episodes).")


if __name__ == "__main__":
    run_blind_replication_suite()
