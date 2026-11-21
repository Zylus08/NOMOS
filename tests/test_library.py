"""
NOMOS Differentiation & Feature Library Tests
Agents G05, G07, D08, D09, D11, D12, D13
"""

import numpy as np
import pytest
from nomos.differentiation import (
    finite_difference,
    savitzky_golay_derivative,
    spline_derivative,
    evaluate_derivative_error,
)
from nomos.library import PolynomialLibrary, TrigonometricLibrary, CompositeLibrary, FeatureScaler


def test_finite_difference_accuracy():
    # Test on f(t) = sin(t), exact derivative is cos(t)
    t = np.linspace(0.0, 2.0 * np.pi, 501)
    x = np.sin(t)
    x_dot_true = np.cos(t)

    # 4th order FD
    x_dot_est = finite_difference(t, x, order=4)
    # Exclude boundary points for pure interior check
    err = np.max(np.abs(x_dot_est[5:-5] - x_dot_true[5:-5]))
    assert err < 1e-4, f"Finite difference error {err} too high"


def test_savitzky_golay_noise_filtering():
    rng = np.random.default_rng(42)
    t = np.linspace(0.0, 5.0, 501)
    x_clean = np.sin(2.0 * t)
    x_dot_true = 2.0 * np.cos(2.0 * t)

    noise = rng.normal(0, 0.02, size=len(t))
    x_noisy = x_clean + noise

    # Raw FD on noisy data amplifies error
    fd_noisy = finite_difference(t, x_noisy, order=2)
    # Savitzky-Golay filters out high frequencies
    sg_noisy = savitzky_golay_derivative(t, x_noisy, window_length=21, polyorder=3)

    fd_rmse = np.sqrt(np.mean((fd_noisy[10:-10] - x_dot_true[10:-10]) ** 2))
    sg_rmse = np.sqrt(np.mean((sg_noisy[10:-10] - x_dot_true[10:-10]) ** 2))

    assert sg_rmse < fd_rmse, f"Savitzky-Golay ({sg_rmse}) should outperform raw FD ({fd_rmse}) on noisy signals"


def test_polynomial_library_features():
    X = np.array([[1.0, 2.0], [3.0, 4.0]])
    poly = PolynomialLibrary(degree=2, include_bias=True)
    Theta = poly.fit_transform(X, variable_names=["x", "y"])
    names = poly.get_feature_names()

    # Features for 2 vars up to deg 2: 1, x, y, x^2, x*y, y^2 (6 terms)
    assert len(names) == 6
    assert names == ["1", "x", "y", "x^2", "x*y", "y^2"]
    # Check row 0: [1, 1, 2, 1, 2, 4]
    np.testing.assert_allclose(Theta[0], [1.0, 1.0, 2.0, 1.0, 2.0, 4.0])


def test_trigonometric_library_features():
    X = np.array([[0.0, np.pi / 2.0]])
    trig = TrigonometricLibrary(harmonics=[1])
    Theta = trig.fit_transform(X, variable_names=["a", "b"])
    names = trig.get_feature_names()

    # sin(a), cos(a), sin(b), cos(b)
    assert len(names) == 4
    np.testing.assert_allclose(Theta[0], [0.0, 1.0, 1.0, 0.0], atol=1e-7)


def test_feature_scaler_unscaling_exactness():
    rng = np.random.default_rng(42)
    Theta = rng.uniform(1.0, 10.0, size=(50, 4))
    Theta[:, 0] *= 1000.0  # severely unscaled column

    scaler = FeatureScaler(mode="l2")
    Theta_scaled = scaler.fit_transform(Theta)

    # Check scaled column norms are 1.0
    col_norms = np.linalg.norm(Theta_scaled, axis=0)
    np.testing.assert_allclose(col_norms, 1.0)

    # Check unscaling
    Xi_scaled = np.array([[1.0], [2.0], [3.0], [4.0]])
    Xi_unscaled = scaler.unscale_coefficients(Xi_scaled)

    # Verify Theta @ Xi_unscaled == Theta_scaled @ Xi_scaled
    pred_orig = Theta @ Xi_unscaled
    pred_scaled = Theta_scaled @ Xi_scaled
    np.testing.assert_allclose(pred_orig, pred_scaled, atol=1e-10)
