"""
NOMOS M2 Unified Physical Benchmark Registry (10 Dynamical Systems)
Milestone M2 — Phase 7 Benchmark Suite Factory
Agents B11 & B12
"""

from typing import Dict, List, Optional, Tuple, Type
import numpy as np

from nomos.core.system import DynamicalSystem
from nomos.physics.harmonic_oscillator import HarmonicOscillator
from nomos.physics.damped_oscillator import DampedOscillator
from nomos.physics.pendulum import NonlinearPendulum
from nomos.physics.lotka_volterra import LotkaVolterra
from nomos.physics.lorenz63 import Lorenz63

# M2 Extended systems
from nomos.physics.duffing import DuffingOscillator
from nomos.physics.vanderpol import VanDerPolOscillator
from nomos.physics.damped_pendulum import DampedPendulum
from nomos.physics.rational_system import RationalKineticsSystem
from nomos.physics.roessler import RoesslerSystem


M2_BENCHMARK_REGISTRY: Dict[str, Type[DynamicalSystem]] = {
    # 5 M1 Benchmarks
    "harmonic_oscillator": HarmonicOscillator,
    "damped_oscillator": DampedOscillator,
    "nonlinear_pendulum": NonlinearPendulum,
    "lotka_volterra": LotkaVolterra,
    "lorenz63": Lorenz63,
    # 5 M2 Benchmarks
    "duffing_oscillator": DuffingOscillator,
    "vanderpol_oscillator": VanDerPolOscillator,
    "damped_pendulum": DampedPendulum,
    "rational_kinetics": RationalKineticsSystem,
    "roessler": RoesslerSystem,
}

M2_BENCHMARK_DEFAULT_ICS: Dict[str, List[np.ndarray]] = {
    "harmonic_oscillator": [np.array([1.0, 0.0]), np.array([1.5, 0.5])],
    "damped_oscillator": [np.array([1.5, 0.0]), np.array([2.0, -0.5])],
    "nonlinear_pendulum": [np.array([1.0, 0.0]), np.array([1.8, 0.2])],
    "lotka_volterra": [np.array([1.5, 1.0]), np.array([1.0, 1.5])],
    "lorenz63": [np.array([-8.0, 8.0, 27.0]), np.array([1.0, 1.0, 1.0])],
    "duffing_oscillator": [np.array([1.0, 0.0]), np.array([0.5, 1.0])],
    "vanderpol_oscillator": [np.array([2.0, 0.0]), np.array([0.5, 2.0])],
    "damped_pendulum": [np.array([1.5, 0.0]), np.array([2.0, -0.5])],
    "rational_kinetics": [np.array([1.2, 0.8]), np.array([2.0, 1.5])],
    "roessler": [np.array([1.0, 1.0, 0.0]), np.array([0.0, -2.0, 0.0])],
}

M2_SYSTEM_UNITS: Dict[str, Dict[str, Dict[str, int]]] = {
    "harmonic_oscillator": {"x": {"L": 1}, "v": {"L": 1, "T": -1}},
    "damped_oscillator": {"x": {"L": 1}, "v": {"L": 1, "T": -1}},
    "nonlinear_pendulum": {"theta": {}, "omega": {"T": -1}},
    "damped_pendulum": {"theta": {}, "omega": {"T": -1}},
    "duffing_oscillator": {"x": {"L": 1}, "v": {"L": 1, "T": -1}},
    "vanderpol_oscillator": {"x": {"L": 1}, "v": {"L": 1, "T": -1}},
}


def get_m2_system(name: str, **kwargs) -> DynamicalSystem:
    if name not in M2_BENCHMARK_REGISTRY:
        raise KeyError(f"Unknown M2 system: {name}. Available: {list(M2_BENCHMARK_REGISTRY.keys())}")
    return M2_BENCHMARK_REGISTRY[name](**kwargs)


def list_m2_benchmark_names() -> List[str]:
    return list(M2_BENCHMARK_REGISTRY.keys())
