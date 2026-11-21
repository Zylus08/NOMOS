"""
NOMOS Physical Benchmark Suite Factory & Independent Integration
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


BENCHMARK_REGISTRY: Dict[str, Type[DynamicalSystem]] = {
    "harmonic_oscillator": HarmonicOscillator,
    "damped_oscillator": DampedOscillator,
    "nonlinear_pendulum": NonlinearPendulum,
    "lotka_volterra": LotkaVolterra,
    "lorenz63": Lorenz63,
}

BENCHMARK_DEFAULT_ICS: Dict[str, List[np.ndarray]] = {
    "harmonic_oscillator": [
        np.array([1.0, 0.0]),
        np.array([2.0, 0.5]),
        np.array([0.5, 1.5]),
        np.array([-1.2, 0.8]),
    ],
    "damped_oscillator": [
        np.array([1.5, 0.0]),
        np.array([2.0, 1.0]),
        np.array([-1.0, 2.0]),
        np.array([0.5, -1.5]),
    ],
    "nonlinear_pendulum": [
        np.array([0.5, 0.0]),
        np.array([1.2, 0.0]),
        np.array([2.0, 0.2]),
        np.array([-1.5, 0.5]),
    ],
    "lotka_volterra": [
        np.array([1.0, 1.0]),
        np.array([1.5, 0.8]),
        np.array([2.0, 1.2]),
        np.array([0.8, 1.5]),
    ],
    "lorenz63": [
        np.array([-8.0, 8.0, 27.0]),
        np.array([1.0, 1.0, 1.0]),
        np.array([5.0, 5.0, 20.0]),
        np.array([-5.0, -5.0, 25.0]),
    ],
}


def get_benchmark_system(name: str, **kwargs) -> DynamicalSystem:
    """Factory to retrieve configured benchmark dynamical system."""
    if name not in BENCHMARK_REGISTRY:
        raise KeyError(f"Unknown benchmark system '{name}'. Available: {list(BENCHMARK_REGISTRY.keys())}")
    return BENCHMARK_REGISTRY[name](**kwargs)


def list_benchmark_names() -> List[str]:
    return list(BENCHMARK_REGISTRY.keys())
