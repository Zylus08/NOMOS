"""
NOMOS Unified PDE Benchmark Registry & Initial Conditions
Phase 2: Numerical PDE Simulators
"""

from typing import Dict, List, Optional, Tuple, Type, Callable
import numpy as np

from nomos.pde.simulators.base import BasePDESimulator
from nomos.pde.simulators.heat import HeatEquationSimulator
from nomos.pde.simulators.advection import LinearAdvectionSimulator
from nomos.pde.simulators.burgers import BurgersSimulator
from nomos.pde.simulators.wave import WaveEquationSimulator
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.pde.simulators.kuramoto_sivashinsky import KuramotoSivashinskySimulator
from nomos.pde.simulators.cahn_hilliard import CahnHilliard1DSimulator


PDE_BENCHMARK_REGISTRY: Dict[str, Type[BasePDESimulator]] = {
    "heat_equation": HeatEquationSimulator,
    "linear_advection": LinearAdvectionSimulator,
    "viscous_burgers": BurgersSimulator,
    "wave_equation": WaveEquationSimulator,
    "kdv_equation": KdVSimulator,
    "kuramoto_sivashinsky": KuramotoSivashinskySimulator,
    "cahn_hilliard": CahnHilliard1DSimulator,
}


def get_pde_simulator(name: str, **kwargs) -> BasePDESimulator:
    """Factory to retrieve configured PDE simulator."""
    if name not in PDE_BENCHMARK_REGISTRY:
        raise KeyError(f"Unknown PDE '{name}'. Available: {list(PDE_BENCHMARK_REGISTRY.keys())}")
    return PDE_BENCHMARK_REGISTRY[name](**kwargs)


def list_pde_names() -> List[str]:
    return list(PDE_BENCHMARK_REGISTRY.keys())


def generate_benchmark_initial_condition(pde_name: str, x: np.ndarray, ic_type: str = "default") -> np.ndarray:
    """Generate physically appropriate initial condition on spatial grid x."""
    L = x[-1] - x[0] + (x[1] - x[0])

    if pde_name in ["heat_equation", "linear_advection"]:
        if ic_type == "default":
            return np.sin(x)
        elif ic_type == "composite":
            return np.sin(x) + 0.5 * np.cos(2.0 * x)
        elif ic_type == "gaussian":
            x_mid = 0.5 * (x[0] + x[-1])
            return np.exp(-4.0 * ((x - x_mid) ** 2))
        else:
            return np.sin(x)

    elif pde_name == "viscous_burgers":
        if ic_type == "default":
            # Sinusoidal steepening into viscous shock
            return np.sin(x)
        elif ic_type == "step":
            return -np.sin(x)
        else:
            return np.sin(x)

    elif pde_name == "wave_equation":
        if ic_type == "default":
            return np.sin(x)
        elif ic_type == "pulse":
            x_mid = 0.5 * (x[0] + x[-1])
            return np.exp(-10.0 * ((x - x_mid) ** 2))
        else:
            return np.sin(x)

    elif pde_name == "kdv_equation":
        # 1-soliton profile
        c = 2.0
        xi = 0.5 * np.sqrt(c) * (x - 0.0)
        return 0.5 * c * (1.0 / np.cosh(xi)) ** 2

    elif pde_name == "kuramoto_sivashinsky":
        # Multi-mode small amplitude perturbation initiating chaos
        return np.cos(x / 16.0) * (1.0 + np.sin(x / 16.0))

    elif pde_name == "cahn_hilliard":
        if ic_type == "spinodal":
            # Small random/harmonic perturbation around mixed state u=0
            return 0.1 * np.cos(2.0 * x) + 0.05 * np.sin(5.0 * x)
        elif ic_type == "interface":
            # Smooth domain wall interface tanh(x / eps)
            x_mid = 0.5 * (x[0] + x[-1])
            return np.tanh((x - x_mid) / 0.2)
        else:
            return 0.2 * np.cos(3.0 * x)

    return np.sin(x)
