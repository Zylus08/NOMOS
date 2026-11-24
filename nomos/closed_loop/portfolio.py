"""
NOMOS Persistent Scientific Hypothesis Portfolio & Memory Engine
Phase 2: Structured Candidate-Law Repository and Investigation Lineage
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time
from typing import Dict, List, Optional, Any, Tuple
import numpy as np


class HypothesisStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPPORTED = "SUPPORTED"
    FALSIFIED = "FALSIFIED"
    SUSPENDED = "SUSPENDED"
    REVISE_REQUIRED = "REVISE_REQUIRED"


@dataclass
class ScientificHypothesis:
    """
    Structured, persistent physical governing law candidate.
    Tracks mathematical form, continuous parameters, empirical evidence,
    and historical falsification lineage.
    """
    id: str
    equation_str: str                       # e.g., "u_t = -6.0000*u*u_x - 1.0000*u_xxx"
    features: List[str]                     # e.g., ["u*u_x", "u_xxx"]
    parameters: Dict[str, float]            # e.g., {"u*u_x": -6.0, "u_xxx": -1.0}
    complexity: int                         # Structural complexity (AST nodes or term count)
    origin: str                             # "wsindy", "beam_search", "sindy", "prior"
    
    # Statistical Evidence Metrics
    train_mse: float = float("inf")
    val_mse: float = float("inf")
    bic: float = float("inf")
    evidence_score: float = 0.0             # Normalized likelihood or Bayesian posterior weight
    parameter_uncertainties: Dict[str, float] = field(default_factory=dict)
    
    # Stability & Domain Validity
    stability_diagnostic: Dict[str, Any] = field(default_factory=dict)
    physical_domain_assumptions: Dict[str, Any] = field(default_factory=dict)
    
    # Scientific Memory & Experimental History
    supporting_experiments: List[str] = field(default_factory=list)      # Episode / trial IDs
    contradicting_experiments: List[str] = field(default_factory=list)   # Episode / trial IDs
    rejection_reason: Optional[str] = None
    status: HypothesisStatus = HypothesisStatus.ACTIVE
    version: int = 1
    created_at: float = field(default_factory=time.time)
    lineage_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "equation_str": self.equation_str,
            "features": self.features,
            "parameters": self.parameters,
            "complexity": self.complexity,
            "origin": self.origin,
            "train_mse": round(self.train_mse, 6),
            "val_mse": round(self.val_mse, 6),
            "bic": round(self.bic, 4),
            "evidence_score": round(self.evidence_score, 4),
            "parameter_uncertainties": {k: round(v, 6) for k, v in self.parameter_uncertainties.items()},
            "status": self.status.value,
            "rejection_reason": self.rejection_reason,
            "supporting_count": len(self.supporting_experiments),
            "contradicting_count": len(self.contradicting_experiments),
            "version": self.version,
        }


class HypothesisPortfolio:
    """
    Persistent scientific memory repository.
    Enforces that hypotheses are never silently overwritten.
    Maintains full decision lineage across closed-loop iterations.
    """

    def __init__(self):
        self._hypotheses: Dict[str, ScientificHypothesis] = {}
        self._history: List[Dict[str, Any]] = []

    def register(self, hypothesis: ScientificHypothesis) -> str:
        """Register or revise a hypothesis in scientific memory."""
        hid = hypothesis.id
        if hid in self._hypotheses:
            # Create a revised version rather than overwriting
            existing = self._hypotheses[hid]
            hypothesis.version = existing.version + 1
            hypothesis.lineage_notes.append(f"Revised from version {existing.version} at {time.time()}")
            # Preserve supporting and contradicting history
            hypothesis.supporting_experiments = list(set(existing.supporting_experiments + hypothesis.supporting_experiments))
            hypothesis.contradicting_experiments = list(set(existing.contradicting_experiments + hypothesis.contradicting_experiments))

        self._hypotheses[hid] = hypothesis
        self._history.append({
            "action": "REGISTER_OR_REVISE",
            "id": hid,
            "version": hypothesis.version,
            "equation": hypothesis.equation_str,
            "status": hypothesis.status.value,
            "timestamp": time.time(),
        })
        return hid

    def get(self, hid: str) -> Optional[ScientificHypothesis]:
        return self._hypotheses.get(hid)

    def get_active(self) -> List[ScientificHypothesis]:
        """Return all non-falsified hypotheses sorted by evidence score."""
        active = [h for h in self._hypotheses.values() if h.status in (HypothesisStatus.ACTIVE, HypothesisStatus.SUPPORTED)]
        active.sort(key=lambda h: (h.val_mse, h.complexity))
        return active

    def get_all(self) -> List[ScientificHypothesis]:
        return list(self._hypotheses.values())

    def record_falsification(self, hid: str, experiment_id: str, reason: str):
        """Mark hypothesis as falsified without deleting it from memory."""
        if hid in self._hypotheses:
            h = self._hypotheses[hid]
            h.status = HypothesisStatus.FALSIFIED
            h.rejection_reason = reason
            if experiment_id not in h.contradicting_experiments:
                h.contradicting_experiments.append(experiment_id)
            self._history.append({
                "action": "FALSIFY",
                "id": hid,
                "experiment_id": experiment_id,
                "reason": reason,
                "timestamp": time.time(),
            })

    def record_support(self, hid: str, experiment_id: str):
        """Record an experiment confirming candidate model predictions."""
        if hid in self._hypotheses:
            h = self._hypotheses[hid]
            if experiment_id not in h.supporting_experiments:
                h.supporting_experiments.append(experiment_id)
            if h.status == HypothesisStatus.ACTIVE:
                h.status = HypothesisStatus.SUPPORTED

    def export_summary(self) -> List[Dict[str, Any]]:
        return [h.to_dict() for h in self.get_all()]

    def compute_evidence_weights(self):
        """
        Compute relative evidence distribution (normalized softmax of -BIC)
        across active hypotheses to quantify model uncertainty.
        """
        active = self.get_active()
        if not active:
            return

        bics = np.array([h.bic for h in active])
        # Shift for numerical stability
        min_bic = np.min(bics)
        delta_bic = bics - min_bic
        weights = np.exp(-0.5 * delta_bic)
        total_w = np.sum(weights) + 1e-12
        probs = weights / total_w

        for h, p in zip(active, probs):
            h.evidence_score = float(p)
