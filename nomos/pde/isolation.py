"""
NOMOS PDE Data Isolation Sandbox
Guarantees clean boundary between ground-truth simulation and learner observations.
Enforces deterministic SHA-256 opaque anonymization and explicit allowlist filtering.
"""

import copy
import hashlib
from typing import Dict, Any, Set, List, Optional
import numpy as np
from nomos.pde.schema import SpatiotemporalField, SpatiotemporalDataset

# Explicit allowlist of attributes permitted across the isolation sandbox boundary
ALLOWED_OBSERVATION_ATTRIBUTES: Set[str] = {
    "id",
    "pde_name",
    "x",
    "y",
    "t",
    "u",
    "channel_names",
    "boundary_condition",
    "spatial_dim",
    "units",
    "observation_mask",
    "noise_level",
    "provenance",
}

# Explicit prohibited ground-truth evaluator attributes
DISALLOWED_EVALUATOR_ATTRIBUTES: Set[str] = {
    "u_clean",
    "u_t_true",
    "true_parameters",
    "_simulator",
    "simulator",
    "analytical_solution",
    "exact_coefficients",
    "governing_equation",
    "source_pde_name",
}


def compute_opaque_observation_digest(field: SpatiotemporalField) -> str:
    """
    Compute a deterministic SHA-256 digest over observable data byte streams.
    Independent of Python process lifetime, memory addresses, or PYTHONHASHSEED.
    Hashes only observable physical tensors: spatial_dim, channels, x, y, t, u.
    """
    hasher = hashlib.sha256()
    hasher.update(str(int(field.spatial_dim)).encode("ascii"))
    for ch in sorted(field.channel_names):
        hasher.update(ch.encode("utf-8"))
    hasher.update(np.ascontiguousarray(field.x, dtype=np.float64).tobytes())
    if field.y is not None:
        hasher.update(np.ascontiguousarray(field.y, dtype=np.float64).tobytes())
    hasher.update(np.ascontiguousarray(field.t, dtype=np.float64).tobytes())
    hasher.update(np.ascontiguousarray(field.u, dtype=np.float64).tobytes())
    return hasher.hexdigest()


def create_learner_field_observation(field: SpatiotemporalField) -> SpatiotemporalField:
    """
    Create a sanitized field observation visible to discovery engines.
    Enforces an explicit attribute allowlist and scrubs system names to deterministic
    SHA-256 opaque identifiers.
    
    Strictly purges:
    - PDE name / physical system identity (scrubbed to SHA-256 opaque identifier)
    - Clean noiseless fields (u_clean -> None)
    - True analytical derivatives (u_t_true -> None)
    - True underlying PDE parameters (true_parameters -> None)
    - Reference solver internals or attached simulator handles
    """
    opaque_hash = compute_opaque_observation_digest(field)
    blind_id = f"blind_system_{opaque_hash[:12]}"
    
    # Allowlist attribute extraction: only copy allowlisted attributes
    obs = SpatiotemporalField(
        id=f"learner_obs_{opaque_hash[:8]}",
        pde_name=blind_id,
        x=np.asarray(field.x, dtype=np.float64).copy(),
        y=np.asarray(field.y, dtype=np.float64).copy() if field.y is not None else None,
        t=np.asarray(field.t, dtype=np.float64).copy(),
        u=np.asarray(field.u, dtype=np.float64).copy(),
        channel_names=list(copy.deepcopy(field.channel_names)),
        boundary_condition=field.boundary_condition,
        spatial_dim=int(field.spatial_dim),
        units=dict(copy.deepcopy(field.units)),
        u_clean=None,           # STRIPPED
        u_t_true=None,          # STRIPPED
        true_parameters=None,   # STRIPPED
        observation_mask=np.asarray(field.observation_mask).copy() if field.observation_mask is not None else None,
        noise_level=float(field.noise_level),
        provenance={
            "isolated": True,
            "sha256_digest": opaque_hash,
            "leakage_protected": True,
            "allowlist_enforced": True,
        },
    )

    # Sanitize any unexpected dynamically set attributes
    for disallowed in DISALLOWED_EVALUATOR_ATTRIBUTES:
        if hasattr(obs, disallowed) and getattr(obs, disallowed) is not None:
            setattr(obs, disallowed, None)

    return obs


def serialize_learner_observation(field: SpatiotemporalField) -> Dict[str, Any]:
    """
    Serialize learner observation using an explicit allowlist schema.
    Blocks any accidental or malicious leakage of ground-truth attributes.
    """
    return {
        "id": field.id,
        "pde_name": field.pde_name,
        "x": field.x.tolist(),
        "y": field.y.tolist() if field.y is not None else None,
        "t": field.t.tolist(),
        "u": field.u.tolist(),
        "channel_names": list(field.channel_names),
        "boundary_condition": str(field.boundary_condition.value if hasattr(field.boundary_condition, "value") else field.boundary_condition),
        "spatial_dim": field.spatial_dim,
        "units": field.units,
        "observation_mask": field.observation_mask.tolist() if field.observation_mask is not None else None,
        "noise_level": field.noise_level,
        "provenance": field.provenance,
    }


def create_learner_dataset(dataset: SpatiotemporalDataset) -> SpatiotemporalDataset:
    """Create a sanitized dataset visible to learners using SHA-256 hashing."""
    isolated_fields = [create_learner_field_observation(f) for f in dataset.fields]
    h = hashlib.sha256()
    for f in isolated_fields:
        h.update(f.pde_name.encode("ascii"))
    blind_ds_name = f"blind_dataset_{h.hexdigest()[:12]}"
    return SpatiotemporalDataset(
        pde_name=blind_ds_name,
        channel_names=copy.deepcopy(dataset.channel_names),
        fields=isolated_fields,
        metadata={"isolated": True, "sha256_dataset_hash": h.hexdigest()[:16]},
    )
