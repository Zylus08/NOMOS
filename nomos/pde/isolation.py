"""
NOMOS PDE Data Isolation Sandbox
Guarantees clean boundary between ground-truth simulation and learner observations.
"""

import copy
from typing import Dict, Any
from nomos.pde.schema import SpatiotemporalField, SpatiotemporalDataset


def create_learner_field_observation(field: SpatiotemporalField) -> SpatiotemporalField:
    """
    Create a sanitized field observation visible to discovery engines.
    Strictly purges:
    - PDE name / physical system identity (scrubbed to opaque blind identifier)
    - Clean noiseless fields (u_clean)
    - True analytical derivatives (u_t_true)
    - True underlying PDE parameters
    - Reference solver internals
    """
    blind_id = f"blind_system_{abs(hash(field.id)) % 1000000:06d}"
    obs = SpatiotemporalField(
        id=f"learner_obs_{field.id}",
        pde_name=blind_id,
        x=field.x.copy(),
        y=field.y.copy() if field.y is not None else None,
        t=field.t.copy(),
        u=field.u.copy(),
        channel_names=copy.deepcopy(field.channel_names),
        boundary_condition=field.boundary_condition,
        spatial_dim=field.spatial_dim,
        units=copy.deepcopy(field.units),
        u_clean=None,           # STRIPPED
        u_t_true=None,          # STRIPPED
        true_parameters=None,   # STRIPPED
        observation_mask=field.observation_mask.copy() if field.observation_mask is not None else None,
        noise_level=field.noise_level,
        provenance={
            "isolated": True,
            "source_id": field.id,
            "leakage_protected": True,
        },
    )
    return obs


def create_learner_dataset(dataset: SpatiotemporalDataset) -> SpatiotemporalDataset:
    """Create a sanitized dataset visible to learners."""
    isolated_fields = [create_learner_field_observation(f) for f in dataset.fields]
    blind_ds_name = f"blind_dataset_{abs(hash(dataset.dataset_hash)) % 1000000:06d}"
    return SpatiotemporalDataset(
        pde_name=blind_ds_name,
        channel_names=copy.deepcopy(dataset.channel_names),
        fields=isolated_fields,
        metadata={"isolated": True, "source_hash": dataset.dataset_hash},
    )
