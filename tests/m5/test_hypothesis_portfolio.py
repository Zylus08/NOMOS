"""
NOMOS Milestone M5 Unit Tests: Hypothesis Portfolio & Scientific Memory
Verifies immutability, revision history, evidence scoring, and falsification tracking.
"""

import pytest
import numpy as np

from nomos.closed_loop.portfolio import (
    ScientificHypothesis,
    HypothesisPortfolio,
    HypothesisStatus,
)


def test_portfolio_registration_and_revision():
    portfolio = HypothesisPortfolio()

    h1 = ScientificHypothesis(
        id="hyp_test_01",
        equation_str="u_t = -2.0*u_x",
        features=["u_x"],
        parameters={"u_x": -2.0},
        complexity=2,
        origin="wsindy",
        train_mse=0.01,
        val_mse=0.01,
        bic=12.5,
    )
    portfolio.register(h1)
    assert len(portfolio.get_all()) == 1
    assert portfolio.get("hyp_test_01").version == 1

    # Revise hypothesis with updated parameters
    h1_revised = ScientificHypothesis(
        id="hyp_test_01",
        equation_str="u_t = -2.1*u_x",
        features=["u_x"],
        parameters={"u_x": -2.1},
        complexity=2,
        origin="wsindy_refit",
        train_mse=0.008,
        val_mse=0.008,
        bic=11.2,
    )
    portfolio.register(h1_revised)

    # Immutability & lineage verification
    retrieved = portfolio.get("hyp_test_01")
    assert retrieved.version == 2
    assert len(retrieved.lineage_notes) == 1
    assert "Revised from version 1" in retrieved.lineage_notes[0]
    assert retrieved.parameters["u_x"] == -2.1


def test_portfolio_falsification_and_support():
    portfolio = HypothesisPortfolio()

    h1 = ScientificHypothesis(
        id="hyp_kdv",
        equation_str="u_t = -6.0*u*u_x - 1.0*u_xxx",
        features=["u*u_x", "u_xxx"],
        parameters={"u*u_x": -6.0, "u_xxx": -1.0},
        complexity=4,
        origin="wsindy",
    )
    h2 = ScientificHypothesis(
        id="hyp_advection",
        equation_str="u_t = -2.0*u_x",
        features=["u_x"],
        parameters={"u_x": -2.0},
        complexity=2,
        origin="competing_prior",
    )
    portfolio.register(h1)
    portfolio.register(h2)

    assert len(portfolio.get_active()) == 2

    # Support h1, falsify h2
    portfolio.record_support("hyp_kdv", "exp_01_soliton")
    portfolio.record_support("hyp_kdv", "exp_02_packet")
    portfolio.record_falsification("hyp_advection", "exp_02_packet", "Predictive error on wave packet exceeded margin")

    active = portfolio.get_active()
    assert len(active) == 1
    assert active[0].id == "hyp_kdv"
    assert active[0].status == HypothesisStatus.SUPPORTED
    assert len(active[0].supporting_experiments) == 2

    falsified_h2 = portfolio.get("hyp_advection")
    assert falsified_h2.status == HypothesisStatus.FALSIFIED
    assert "exp_02_packet" in falsified_h2.contradicting_experiments
    assert falsified_h2.rejection_reason is not None


def test_evidence_weights_softmax():
    portfolio = HypothesisPortfolio()

    h1 = ScientificHypothesis(id="h1", equation_str="eq1", features=["u"], parameters={"u": 1.0}, complexity=2, origin="m1", bic=10.0)
    h2 = ScientificHypothesis(id="h2", equation_str="eq2", features=["u"], parameters={"u": 2.0}, complexity=2, origin="m2", bic=20.0)
    portfolio.register(h1)
    portfolio.register(h2)

    portfolio.compute_evidence_weights()
    h1_obj = portfolio.get("h1")
    h2_obj = portfolio.get("h2")

    # Lower BIC should have much higher evidence weight
    assert h1_obj.evidence_score > 0.99
    assert h2_obj.evidence_score < 0.01
    assert np.isclose(h1_obj.evidence_score + h2_obj.evidence_score, 1.0)
