"""
NOMOS M2 Neural Surrogate & Guidance Tests
Milestone M2 — Phase 13 Testing & Review
Agents D07, D08, D09, D10, G01, G04, G05
"""

import numpy as np
import pytest
import torch

from nomos.neural.surrogate import NeuralDynamicsSurrogate
from nomos.neural.trainer import SurrogateTrainer
from nomos.neural.guidance import NeuralGuidanceEngine


def test_neural_surrogate_training_and_jacobian():
    # Fit simple linear system: dx/dt = v, dv/dt = -x
    t = np.linspace(0.0, 4.0, 200)
    x = np.sin(t)[:, np.newaxis]
    v = np.cos(t)[:, np.newaxis]
    X = np.column_stack([x, v])
    X_dot = np.column_stack([v, -x])

    trainer = SurrogateTrainer(
        hidden_dim=32,
        num_layers=2,
        lr=0.01,
        max_epochs=40,
        seed=42,
    )
    surrogate, metrics = trainer.fit(X, X_dot)

    assert metrics["val_r2"] > 0.95, f"Neural surrogate fit poor: R2={metrics['val_r2']}"

    # Verify Jacobian
    # True Jacobian of f([x, v]) = [v, -x] is [[0, 1], [-1, 0]]
    sample_pt = np.array([[0.5, 0.5]])
    jac = surrogate.compute_jacobian(sample_pt)  # (1, 2, 2)
    J = jac[0]

    # Check that d(f_x)/dv is positive and d(f_v)/dx is negative
    assert J[0, 1] > 0.5, f"Expected d(f_x)/dv ~ 1.0, got {J[0, 1]}"
    assert J[1, 0] < -0.5, f"Expected d(f_v)/dx ~ -1.0, got {J[1, 0]}"


def test_neural_guidance_nonlinearity_detection():
    # Periodic nonlinear restoring force: f(x) = -sin(x)
    X = np.linspace(-np.pi, np.pi, 200)[:, np.newaxis]
    X_dot = -np.sin(X)

    trainer = SurrogateTrainer(
        hidden_dim=32,
        num_layers=2,
        lr=0.02,
        batch_size=16,
        max_epochs=100,
        patience=25,
        seed=42,
    )
    surrogate, _ = trainer.fit(X, X_dot)

    engine = NeuralGuidanceEngine(surrogate, variable_names=["theta"])
    guidance = engine.extract_guidance(X, target_dim=0)

    # Should detect strong nonlinearity and recommend sin/cos
    assert guidance.is_strongly_nonlinear, "Failed to detect periodic nonlinearity"
    assert "sin" in guidance.recommended_primitives
