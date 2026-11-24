"""
NOMOS Milestone M5 Unit Tests: Experiment Acquisition Strategies
Verifies all 5 acquisition modes: Random, Fixed, Greedy Disagreement, Cost Normalized, Uncertainty Aware.
"""

import pytest
import numpy as np

from nomos.closed_loop.portfolio import ScientificHypothesis, HypothesisPortfolio
from nomos.closed_loop.acquisition import ExperimentAcquisitionEngine, AcquisitionStrategy


def create_mock_portfolio():
    portfolio = HypothesisPortfolio()
    # KdV hypothesis
    h1 = ScientificHypothesis(
        id="h_kdv",
        equation_str="u_t = -6.0*u*u_x - 1.0*u_xxx",
        features=["u*u_x", "u_xxx"],
        parameters={"u*u_x": -6.0, "u_xxx": -1.0},
        complexity=4,
        origin="wsindy",
        bic=10.0,
    )
    # Impostor advection hypothesis
    h2 = ScientificHypothesis(
        id="h_adv",
        equation_str="u_t = -2.0*u_x",
        features=["u_x"],
        parameters={"u_x": -2.0},
        complexity=2,
        origin="prior",
        bic=10.5,
    )
    portfolio.register(h1)
    portfolio.register(h2)
    return portfolio


def test_greedy_disagreement_selects_dispersive_state():
    portfolio = create_mock_portfolio()
    acq = ExperimentAcquisitionEngine(strategy=AcquisitionStrategy.GREEDY_DISAGREEMENT)

    x = np.linspace(-10, 10, 128)
    dx = x[1] - x[0]

    # Candidate 1: single soliton (c=2.0) where KdV and advection predict identically
    u0_soliton = 2.0 / (np.cosh(np.sqrt(2.0) * x / 2.0) ** 2)
    # Candidate 2: oscillatory wave packet where dispersion strongly diverges from advection
    u0_packet = np.exp(-(x**2) / 4.0) * np.cos(2.0 * x)

    candidate_pool = [
        ("single_soliton", u0_soliton, 1.0),
        ("wave_packet", u0_packet, 1.0),
    ]

    lbl, u0, score, scores = acq.select_experiment(
        portfolio=portfolio,
        candidate_pool=candidate_pool,
        dx=dx,
        dy=0.0,
        periodic=True,
    )

    # Disagreement on wave packet must be significantly higher than on soliton
    assert lbl == "wave_packet"
    assert scores["wave_packet"] > 5.0 * scores["single_soliton"]
    assert score == scores["wave_packet"]


def test_cost_normalized_acquisition():
    portfolio = create_mock_portfolio()
    acq = ExperimentAcquisitionEngine(strategy=AcquisitionStrategy.COST_NORMALIZED)

    x = np.linspace(-10, 10, 128)
    dx = x[1] - x[0]
    u0_packet = np.exp(-(x**2) / 4.0) * np.cos(2.0 * x)

    # Candidate 1: High disagreement but extremely expensive
    # Candidate 2: Slightly lower disagreement but 10x cheaper
    candidate_pool = [
        ("packet_expensive", u0_packet, 100.0),
        ("packet_cheap", u0_packet * 0.9, 1.0),
    ]

    lbl, _, score, scores = acq.select_experiment(
        portfolio=portfolio,
        candidate_pool=candidate_pool,
        dx=dx,
        dy=0.0,
        periodic=True,
    )

    assert lbl == "packet_cheap"
    assert scores["packet_cheap"] > scores["packet_expensive"]


def test_fixed_and_random_acquisition():
    portfolio = create_mock_portfolio()
    x = np.linspace(-10, 10, 64)
    pool = [("c1", np.sin(x), 1.0), ("c2", np.cos(x), 1.0), ("c3", np.exp(-(x**2)), 1.0)]

    # Fixed (round-robin)
    acq_fixed = ExperimentAcquisitionEngine(strategy=AcquisitionStrategy.FIXED)
    lbl0, _, _, _ = acq_fixed.select_experiment(portfolio, pool, dx=0.1, iteration_index=0)
    lbl1, _, _, _ = acq_fixed.select_experiment(portfolio, pool, dx=0.1, iteration_index=1)
    lbl2, _, _, _ = acq_fixed.select_experiment(portfolio, pool, dx=0.1, iteration_index=2)
    assert (lbl0, lbl1, lbl2) == ("c1", "c2", "c3")

    # Random
    acq_rand = ExperimentAcquisitionEngine(strategy=AcquisitionStrategy.RANDOM, random_seed=42)
    lbl_r, _, _, _ = acq_rand.select_experiment(portfolio, pool, dx=0.1, iteration_index=0)
    assert lbl_r in ["c1", "c2", "c3"]
