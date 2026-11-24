"""
NOMOS Milestone M5 CLI Investigation Interface
Autonomous closed-loop experimentation and hypothesis falsification controller CLI.
Usage:
    python -m nomos.cli_investigate --system kdv --strategy greedy_disagreement --budget 4 --seed 42 --output audit/m5/demo_trace.json
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import argparse
import json
from pathlib import Path
import numpy as np

from nomos.pde.schema import Grid1D, Grid2D
from nomos.closed_loop.oracle import SimulationOracle
from nomos.closed_loop.acquisition import AcquisitionStrategy
from nomos.closed_loop.controller import ClosedLoopController

# Simulators
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.pde.simulators.burgers import BurgersSimulator
from nomos.pde.simulators.gray_scott import GrayScottSimulator
from nomos.pde.simulators.fitzhugh_nagumo import FitzHughNagumoSimulator
from nomos.pde.simulators.navier_stokes_2d import NavierStokes2DSimulator

from experiments.m5.run_m5_benchmarks import (
    build_kdv_pool,
    build_burgers_pool,
    build_gray_scott_pool,
    build_fitzhugh_nagumo_pool,
    build_navier_stokes_pool,
)


def run_cli():
    parser = argparse.ArgumentParser(description="NOMOS Autonomous Closed-Loop Scientific Investigator")
    parser.add_argument("--system", type=str, default="kdv", choices=["kdv", "burgers", "gray_scott", "fitzhugh_nagumo", "navier_stokes"])
    parser.add_argument("--strategy", type=str, default="greedy_disagreement", choices=["greedy_disagreement", "cost_normalized", "uncertainty_aware", "random", "fixed"])
    parser.add_argument("--budget", type=int, default=4)
    parser.add_argument("--noise", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default="audit/m5/demo_trace.json")

    args = parser.parse_args()

    print(f"===========================================================")
    print(f"NOMOS M5 Autonomous Scientific Investigation")
    print(f"System: {args.system} | Strategy: {args.strategy} | Budget: {args.budget} | Noise: {args.noise}")
    print(f"===========================================================")

    strat_map = {
        "greedy_disagreement": AcquisitionStrategy.GREEDY_DISAGREEMENT,
        "cost_normalized": AcquisitionStrategy.COST_NORMALIZED,
        "uncertainty_aware": AcquisitionStrategy.UNCERTAINTY_AWARE,
        "random": AcquisitionStrategy.RANDOM,
        "fixed": AcquisitionStrategy.FIXED,
    }
    strategy = strat_map[args.strategy]

    if args.system == "kdv":
        grid = Grid1D.create((-10.0, 10.0), 128)
        sim = KdVSimulator(domain=(-10.0, 10.0))
        pool = build_kdv_pool(sim, grid)
        dim = 1
        target_chan = "u"
        cand_lib = ["u*u_x", "u_xxx", "u_x"]
    elif args.system == "burgers":
        grid = Grid1D.create((0.0, 2.0 * np.pi), 64)
        sim = BurgersSimulator(nu=0.05)
        pool = build_burgers_pool(sim, grid)
        dim = 1
        target_chan = "u"
        cand_lib = ["u*u_x", "u_xx"]
    elif args.system == "gray_scott":
        grid = Grid2D.create((0.0, 2.5), (0.0, 2.5), 32, 32)
        sim = GrayScottSimulator(D_u=0.16, D_v=0.08, F=0.035, k=0.060)
        pool = build_gray_scott_pool(sim, grid)
        dim = 2
        target_chan = "v"
        cand_lib = ["lap_v", "u*v^2", "v"]
    elif args.system == "fitzhugh_nagumo":
        grid = Grid2D.create((-10.0, 10.0), (-10.0, 10.0), 32, 32)
        sim = FitzHughNagumoSimulator(D_u=1.0, D_v=0.0, eps=0.05, a1=0.5, a0=0.0)
        pool = build_fitzhugh_nagumo_pool(sim, grid)
        dim = 2
        target_chan = "u"
        cand_lib = ["lap_u", "u", "u^3", "v"]
    elif args.system == "navier_stokes":
        grid = Grid2D.create((0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi), 32, 32)
        sim = NavierStokes2DSimulator(nu=0.02)
        pool = build_navier_stokes_pool(sim, grid)
        dim = 2
        target_chan = "omega"
        cand_lib = ["lap_omega", "advection_omega"]
    else:
        raise ValueError(f"Unknown system: {args.system}")

    oracle = SimulationOracle(sim, grid)
    controller = ClosedLoopController(
        oracle=oracle,
        grid=grid,
        candidate_experiment_pool=pool,
        strategy=strategy,
        max_budget=args.budget,
        noise_level=args.noise,
        random_seed=args.seed,
        dimension=dim,
        target_channel=target_chan,
        candidate_library=cand_lib,
    )

    episode = controller.run_investigation()

    print(f"\nInvestigation Complete!")
    print(f"Final Identifiability Status: {episode.status.value}")
    if episode.winning_hypothesis:
        print(f"Discovered Governing Law: {episode.winning_hypothesis.equation_str}")
        print(f"Parameter Values: {episode.winning_hypothesis.parameters}")
    print(f"Total Trajectory Queries: {episode.total_cost.trajectory_queries}")
    print(f"Total Compute Time: {episode.duration_seconds:.4f}s")
    print(f"Active Hypotheses Remaining: {len(controller.portfolio.get_active())}")

    # Build detailed decision trace for export
    trace_data = {
        "system": args.system,
        "strategy": args.strategy,
        "max_budget": args.budget,
        "noise_level": args.noise,
        "seed": args.seed,
        "final_status": episode.status.value,
        "winning_equation": episode.winning_hypothesis.equation_str if episode.winning_hypothesis else None,
        "winning_parameters": episode.winning_hypothesis.parameters if episode.winning_hypothesis else None,
        "total_cost": episode.total_cost.to_dict(),
        "duration_seconds": episode.duration_seconds,
        "trace": [
            {
                "iteration": rec.iteration,
                "stage": rec.stage,
                "selected_experiment": rec.selected_experiment,
                "acquisition_score": rec.acquisition_score,
                "active_hypotheses_count": rec.active_hypotheses_count,
                "top_hypothesis": rec.top_hypothesis,
                "identifiability_status": rec.identifiability_status,
                "cost": rec.cost,
                "falsified_hypotheses": rec.falsified_hypotheses,
                "supported_hypotheses": rec.supported_hypotheses,
                "elapsed_time_s": rec.elapsed_time_s,
                "metadata": rec.metadata,
            }
            for rec in episode.trace
        ],
        "portfolio": episode.portfolio_summary,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, indent=2)

    print(f"\nTrace successfully saved to {out_path.resolve()}")


if __name__ == "__main__":
    run_cli()
