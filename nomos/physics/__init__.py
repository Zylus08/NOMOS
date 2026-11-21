"""
NOMOS Physics Package Module
"""

from nomos.physics.base import BasePhysicalSystem
from nomos.physics.solvers import simulate_system, solver_convergence_study, SimulationResult
from nomos.physics.harmonic_oscillator import HarmonicOscillator
from nomos.physics.damped_oscillator import DampedOscillator
from nomos.physics.pendulum import NonlinearPendulum
from nomos.physics.lotka_volterra import LotkaVolterra
from nomos.physics.lorenz63 import Lorenz63
from nomos.physics.benchmarks import get_benchmark_system, list_benchmark_names, BENCHMARK_DEFAULT_ICS

__all__ = [
    "BasePhysicalSystem",
    "simulate_system",
    "solver_convergence_study",
    "SimulationResult",
    "HarmonicOscillator",
    "DampedOscillator",
    "NonlinearPendulum",
    "LotkaVolterra",
    "Lorenz63",
    "get_benchmark_system",
    "list_benchmark_names",
    "BENCHMARK_DEFAULT_ICS",
]
