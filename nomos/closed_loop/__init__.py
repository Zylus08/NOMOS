"""
NOMOS Closed-Loop Autonomous Scientific Experimentation Architecture
Milestone M5: Closed-Loop Physical Law Discovery & Falsifiable Experimentation
"""

from nomos.closed_loop.portfolio import ScientificHypothesis, HypothesisPortfolio
from nomos.closed_loop.oracle import SimulationOracle, ExperimentRequest, ExperimentResponse
from nomos.closed_loop.acquisition import ExperimentAcquisitionEngine, AcquisitionStrategy
from nomos.closed_loop.diagnostics import IdentifiabilityStatus, IdentifiabilityAuditor
from nomos.closed_loop.controller import ClosedLoopController, InvestigationEpisode

__all__ = [
    "ScientificHypothesis",
    "HypothesisPortfolio",
    "SimulationOracle",
    "ExperimentRequest",
    "ExperimentResponse",
    "ExperimentAcquisitionEngine",
    "AcquisitionStrategy",
    "IdentifiabilityStatus",
    "IdentifiabilityAuditor",
    "ClosedLoopController",
    "InvestigationEpisode",
]
