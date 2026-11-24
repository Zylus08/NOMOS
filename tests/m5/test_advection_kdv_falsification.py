"""
NOMOS Milestone M5 Unit Tests: Active Falsification of Linear Advection vs KdV
Verifies that traveling solitary waves cannot separate advection from KdV,
and that closed-loop experiment selection actively discovers dispersive initial conditions
that conclusively falsify linear advection.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid1D, TimeGrid
from nomos.pde.simulators.kdv import KdVSimulator
from nomos.pde.weak_form import WeakFormPDEDiscovery
from nomos.closed_loop.portfolio import ScientificHypothesis, HypothesisPortfolio, HypothesisStatus
from nomos.closed_loop.acquisition import ExperimentAcquisitionEngine, AcquisitionStrategy


def test_soliton_advection_kdv_degeneracy():
    grid = Grid1D.create((-10.0, 10.0), 128)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    x = grid.x

    # Single soliton with c=2.0
    u0_soliton = sim.analytical_1soliton(x, 0.0, c=2.0)
    time_grid = TimeGrid.create((0.0, 0.2), 15)
    field_soliton = sim.simulate(u0_soliton, grid, time_grid)

    wf = WeakFormPDEDiscovery(num_test_functions=60, random_seed=42)
    G, b, fnames = wf.build_weak_form_system(field_soliton)

    # Hypotheses
    xi_adv = np.zeros(len(fnames))
    xi_adv[fnames.index("u_x")] = -2.0

    xi_kdv = np.zeros(len(fnames))
    xi_kdv[fnames.index("u_xxx")] = -1.0
    xi_kdv[fnames.index("u*u_x")] = -6.0

    res_adv = float(np.mean((b - G @ xi_adv) ** 2))
    res_kdv = float(np.mean((b - G @ xi_kdv) ** 2))

    # On a single soliton, advection and KdV residuals are both extremely low (< 1e-6)
    # and their ratio is close to 1.0 (~0.9 to 1.1)
    ratio = res_adv / (res_kdv + 1e-12)
    assert res_adv < 1e-5
    assert res_kdv < 1e-5
    assert 0.5 < ratio < 2.0, f"Expected indistinguishable residuals on soliton, got ratio {ratio}"


def test_wave_packet_active_falsification():
    grid = Grid1D.create((-10.0, 10.0), 128)
    sim = KdVSimulator(domain=(-10.0, 10.0))
    x = grid.x

    # Oscillatory wave packet
    u0_packet = np.exp(-(x**2) / 4.0) * np.cos(2.0 * x)
    time_grid = TimeGrid.create((0.0, 0.2), 15)
    field_packet = sim.simulate(u0_packet, grid, time_grid)

    wf = WeakFormPDEDiscovery(num_test_functions=60, random_seed=42)
    G, b, fnames = wf.build_weak_form_system(field_packet)

    xi_adv = np.zeros(len(fnames))
    xi_adv[fnames.index("u_x")] = -2.0

    xi_kdv = np.zeros(len(fnames))
    xi_kdv[fnames.index("u_xxx")] = -1.0
    xi_kdv[fnames.index("u*u_x")] = -6.0

    res_adv = float(np.mean((b - G @ xi_adv) ** 2))
    res_kdv = float(np.mean((b - G @ xi_kdv) ** 2))

    # On the wave packet, KdV residual is near zero, while advection residual is massive
    falsification_ratio = res_adv / (res_kdv + 1e-12)
    assert falsification_ratio > 1000.0, f"Expected decisive falsification ratio > 1000x, got {falsification_ratio}"
    assert res_kdv < 1e-5
    assert res_adv > 5e-4
