"""
NOMOS Physics & Numerical Solvers Verification Tests
Agents G01, G03, B07, B08, B09
"""

import numpy as np
import pytest
from nomos.physics import (
    get_benchmark_system,
    list_benchmark_names,
    simulate_system,
    solver_convergence_study,
)


def test_benchmark_registry_completeness():
    names = list_benchmark_names()
    expected = {"harmonic_oscillator", "damped_oscillator", "nonlinear_pendulum", "lotka_volterra", "lorenz63"}
    assert set(names) == expected


def test_harmonic_oscillator_analytical_equivalence(harmonic_system):
    t = np.linspace(0.0, 5.0, 501)
    x0 = np.array([1.5, -0.5])
    sim = simulate_system(harmonic_system, x0, (0.0, 5.0), t_eval=t, rtol=1e-11, atol=1e-11)
    assert sim.success
    analytical = harmonic_system.analytical_solution(t, x0)
    err = np.max(np.abs(sim.x - analytical))
    assert err < 1e-8, f"Harmonic oscillator solver error {err} exceeds analytical tolerance"


def test_damped_oscillator_analytical_equivalence(damped_system):
    t = np.linspace(0.0, 5.0, 501)
    x0 = np.array([2.0, 0.0])
    sim = simulate_system(damped_system, x0, (0.0, 5.0), t_eval=t, rtol=1e-11, atol=1e-11)
    assert sim.success
    analytical = damped_system.analytical_solution(t, x0)
    err = np.max(np.abs(sim.x - analytical))
    assert err < 1e-8, f"Damped oscillator solver error {err} exceeds analytical tolerance"


def test_harmonic_energy_conservation(harmonic_system):
    t = np.linspace(0.0, 10.0, 1001)
    x0 = np.array([1.0, 1.0])
    sim = simulate_system(harmonic_system, x0, (0.0, 10.0), t_eval=t, rtol=1e-10, atol=1e-10)
    assert sim.energy_drift is not None
    assert sim.energy_drift < 1e-10, f"Energy drift {sim.energy_drift} exceeds symplectic threshold"


def test_lotka_volterra_first_integral(lotka_system):
    t = np.linspace(0.0, 8.0, 801)
    x0 = np.array([1.5, 1.0])
    sim = simulate_system(lotka_system, x0, (0.0, 8.0), t_eval=t, rtol=1e-10, atol=1e-10)
    assert sim.energy_drift is not None
    assert sim.energy_drift < 1e-8, f"Lotka-Volterra invariant drift {sim.energy_drift} exceeds bound"


def test_solver_tolerance_convergence(harmonic_system):
    t = np.linspace(0.0, 2.0, 201)
    x0 = np.array([1.0, 0.0])
    res = solver_convergence_study(harmonic_system, x0, (0.0, 2.0), t_eval=t, tolerances=[1e-4, 1e-6, 1e-8, 1e-10])
    sweeps = res["sweeps"]
    errors = [s["max_absolute_error"] for s in sweeps]
    # Check monotonic convergence with decreasing tolerance until numerical precision floor (~1e-9)
    for i in range(len(errors) - 1):
        assert errors[i] >= errors[i + 1] or errors[i + 1] < 1e-9
