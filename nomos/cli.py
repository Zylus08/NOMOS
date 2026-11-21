"""
NOMOS Command Line Interface
Agent H02
"""

import argparse
import sys
import numpy as np
from nomos.physics import get_benchmark_system, list_benchmark_names, simulate_system
from nomos.data import Trajectory, TrajectoryDataset, IsolatedLearnerDataset
from nomos.pipeline import DiscoveryEngine, DiscoveryConfig


def main():
    parser = argparse.ArgumentParser(description="NOMOS: Neural & Symbolic Discovery of Physical Laws")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # Benchmarks list
    subparsers.add_parser("list-benchmarks", help="List available physical benchmarks")

    # Discover command
    disc_parser = subparsers.add_parser("discover", help="Run equation discovery on benchmark system")
    disc_parser.add_argument("--system", type=str, default="harmonic_oscillator", choices=list_benchmark_names())
    disc_parser.add_argument("--noise", type=float, default=0.0, help="Proportional observation noise")
    disc_parser.add_argument("--degree", type=int, default=2, help="Polynomial library degree")
    disc_parser.add_argument("--threshold", type=float, default=0.1, help="STLSQ sparsity threshold")

    args = parser.parse_args()

    if args.command == "list-benchmarks":
        print("Available NOMOS benchmarks:")
        for name in list_benchmark_names():
            sys_obj = get_benchmark_system(name)
            print(f" - {name} (dimension: {sys_obj.dimension}, conservative: {sys_obj.metadata.is_conservative})")
        return

    elif args.command == "discover":
        print(f"Executing NOMOS discovery on {args.system} with noise={args.noise}...")
        sys_obj = get_benchmark_system(args.system)
        t = np.linspace(0.0, 10.0, 1001)
        x0 = np.ones(sys_obj.dimension)
        sim = simulate_system(sys_obj, x0, (0.0, 10.0), t_eval=t)

        traj = Trajectory(id="cli_traj_0", t=sim.t, x=sim.x)
        ds = TrajectoryDataset(system_name=args.system, variable_names=list(sys_obj.variable_names), trajectories=[traj])
        isolated_ds = IsolatedLearnerDataset(ds)

        cfg = DiscoveryConfig(
            poly_degree=args.degree,
            threshold=args.threshold,
            library_type="composite" if "pendulum" in args.system else "polynomial",
        )
        engine = DiscoveryEngine(cfg)
        out = engine.fit(isolated_ds)

        print("\n=== Discovered Governing Equations ===")
        for vname, eq in out.discovered_system.equations.items():
            print(f"d{vname}/dt = {eq.raw_str}  [complexity: {eq.complexity_score:.1f}]")
        print("\nGround Truth Equations:")
        for vname, eq_str in sys_obj.ground_truth_symbolic().items():
            print(f"d{vname}/dt = {eq_str}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
