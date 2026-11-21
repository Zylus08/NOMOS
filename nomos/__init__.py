"""
NOMOS: Neural & Symbolic Discovery of Physical Laws
M1 Scientific Discovery Foundation
"""

__version__ = "0.1.0"
__author__ = "Saksham Mishra <mishrasaksham080705@gmail.com>"

from nomos.core.system import DynamicalSystem, SystemMetadata
from nomos.core.library import BaseFeatureLibrary
from nomos.core.optimizer import BaseSparseOptimizer, OptimizerResult
from nomos.core.symbolic import DiscoveredEquation, DiscoveredSystem
from nomos.core.evaluator import EvaluationReport
from nomos.pipeline.discovery import DiscoveryEngine, DiscoveryConfig
from nomos.physics.benchmarks import get_benchmark_system, list_benchmark_names

__all__ = [
    "DynamicalSystem",
    "SystemMetadata",
    "BaseFeatureLibrary",
    "BaseSparseOptimizer",
    "OptimizerResult",
    "DiscoveredEquation",
    "DiscoveredSystem",
    "EvaluationReport",
    "DiscoveryEngine",
    "DiscoveryConfig",
    "get_benchmark_system",
    "list_benchmark_names",
]
