"""
NOMOS Baselines Verification Tests (OLS & PySINDy Adapter)
Agents F09 & F10
"""

import numpy as np
import pytest
from nomos.physics import get_benchmark_system, simulate_system
from nomos.library import PolynomialLibrary
from nomos.differentiation import finite_difference
from nomos.evaluation.baselines import OLSBaseline, PySINDyAdapter


def test_ols_baseline():
    sys = get_benchmark_system("harmonic_oscillator")
    t = np.linspace(0.0, 5.0, 501)
    sim = simulate_system(sys, np.array([1.0, 0.0]), (0.0, 5.0), t_eval=t)
    x_dot = finite_difference(t, sim.x, order=4)

    lib = PolynomialLibrary(degree=2, include_bias=True)
    Theta = lib.fit_transform(sim.x, list(sys.variable_names))

    ols = OLSBaseline().fit(Theta, x_dot)
    assert ols.coef_ is not None
    # OLS is dense: all coefficients are generally nonzero
    assert np.all(np.abs(ols.coef_) > 1e-15)


def test_pysindy_adapter_parity():
    sys = get_benchmark_system("harmonic_oscillator")
    t = np.linspace(0.0, 5.0, 501)
    sim = simulate_system(sys, np.array([1.0, 0.0]), (0.0, 5.0), t_eval=t)

    adapter = PySINDyAdapter(threshold=0.1, degree=2)
    adapter.fit(sim.x, sim.t, feature_names=list(sys.variable_names))

    assert adapter.coef_ is not None
    # Verify PySINDy also recovers sparse harmonic oscillator
    # Check that nonzeros are on x and v
    feat_names = ["1", "x", "v", "x^2", "x v", "v^2"]
    v_idx = feat_names.index("v")
    x_idx = feat_names.index("x")

    assert abs(adapter.coef_[v_idx, 0] - 1.0) < 0.05
    assert abs(adapter.coef_[x_idx, 1] - (-1.0)) < 0.05
