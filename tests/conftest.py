"""
NOMOS Test Fixtures & Configurations
Agent G01
"""

import pytest
import numpy as np
from nomos.physics import get_benchmark_system, list_benchmark_names
from nomos.data import Trajectory, TrajectoryDataset, sample_initial_conditions


@pytest.fixture
def harmonic_system():
    return get_benchmark_system("harmonic_oscillator", omega0=1.0)


@pytest.fixture
def damped_system():
    return get_benchmark_system("damped_oscillator", omega0=1.0, zeta=0.1)


@pytest.fixture
def pendulum_system():
    return get_benchmark_system("nonlinear_pendulum", g=9.81, L=1.0)


@pytest.fixture
def lotka_system():
    return get_benchmark_system("lotka_volterra", alpha=1.5, beta=1.0, gamma=3.0, delta=1.0)


@pytest.fixture
def lorenz_system():
    return get_benchmark_system("lorenz63", sigma=10.0, rho=28.0, beta=8.0 / 3.0)
