"""
NOMOS Spatiotemporal Field Schema & Cryptographic Integrity
Phase 1: Spatiotemporal Architecture
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


class BoundaryConditionType(str, Enum):
    PERIODIC = "periodic"
    DIRICHLET = "dirichlet"
    NEUMANN = "neumann"
    OPEN = "open"


@dataclass
class Grid1D:
    """Uniform 1D spatial grid description."""
    x: np.ndarray  # Shape: (N,)
    num_points: int
    dx: float
    domain: Tuple[float, float]

    @classmethod
    def create(cls, domain: Tuple[float, float], num_points: int, periodic: bool = True) -> "Grid1D":
        if periodic:
            # On periodic grid, last point is omitted to avoid duplicate boundary point
            x = np.linspace(domain[0], domain[1], num_points, endpoint=False)
            dx = float((domain[1] - domain[0]) / num_points)
        else:
            x = np.linspace(domain[0], domain[1], num_points, endpoint=True)
            dx = float(x[1] - x[0]) if num_points > 1 else 0.0
        return cls(x=x, num_points=num_points, dx=dx, domain=domain)


@dataclass
class Grid2D:
    """Uniform 2D spatial grid description."""
    x: np.ndarray  # Shape: (Nx,)
    y: np.ndarray  # Shape: (Ny,)
    num_points_x: int
    num_points_y: int
    dx: float
    dy: float
    domain_x: Tuple[float, float]
    domain_y: Tuple[float, float]

    @classmethod
    def create(
        cls,
        domain_x: Tuple[float, float],
        domain_y: Tuple[float, float],
        num_points_x: int,
        num_points_y: int,
        periodic: bool = True,
    ) -> "Grid2D":
        if periodic:
            x = np.linspace(domain_x[0], domain_x[1], num_points_x, endpoint=False)
            y = np.linspace(domain_y[0], domain_y[1], num_points_y, endpoint=False)
            dx = float((domain_x[1] - domain_x[0]) / num_points_x)
            dy = float((domain_y[1] - domain_y[0]) / num_points_y)
        else:
            x = np.linspace(domain_x[0], domain_x[1], num_points_x, endpoint=True)
            y = np.linspace(domain_y[0], domain_y[1], num_points_y, endpoint=True)
            dx = float(x[1] - x[0]) if num_points_x > 1 else 0.0
            dy = float(y[1] - y[0]) if num_points_y > 1 else 0.0
        return cls(
            x=x,
            y=y,
            num_points_x=num_points_x,
            num_points_y=num_points_y,
            dx=dx,
            dy=dy,
            domain_x=domain_x,
            domain_y=domain_y,
        )

    @property
    def meshgrid(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return 2D coordinate meshgrids (X, Y) with indexing='ij'."""
        return np.meshgrid(self.x, self.y, indexing="ij")


@dataclass
class TimeGrid:
    """Temporal integration grid description."""
    t: np.ndarray  # Shape: (M,)
    num_steps: int
    dt: float
    t_span: Tuple[float, float]

    @classmethod
    def create(cls, t_span: Tuple[float, float], num_steps: int) -> "TimeGrid":
        t = np.linspace(t_span[0], t_span[1], num_steps)
        dt = float(t[1] - t[0]) if num_steps > 1 else 0.0
        return cls(t=t, num_steps=num_steps, dt=dt, t_span=t_span)


@dataclass
class SpatiotemporalField:
    """
    Standard spatiotemporal field observation instance.
    Represents continuous or discretized scalar or multi-channel fields over 1D/2D space and time.
    """
    id: str
    pde_name: str
    x: np.ndarray                         # Shape: (Nx,) spatial coordinates
    t: np.ndarray                         # Shape: (M,) temporal coordinates
    u: np.ndarray                         # Observed field, Shape: (M, Nx), (M, Nx, C), (M, Nx, Ny), or (M, Nx, Ny, C)
    y: Optional[np.ndarray] = None        # Shape: (Ny,) spatial coordinates for 2D fields
    channel_names: List[str] = field(default_factory=lambda: ["u"])
    boundary_condition: BoundaryConditionType = BoundaryConditionType.PERIODIC
    spatial_dim: int = 1
    units: Dict[str, str] = field(default_factory=dict)
    
    # Ground-truth evaluator-only fields (STRIPPED from learners)
    u_clean: Optional[np.ndarray] = None  # Shape: identical to u
    u_t_true: Optional[np.ndarray] = None # Shape: identical to u, true temporal derivative
    true_parameters: Optional[Dict[str, float]] = None # Evaluator only
    
    observation_mask: Optional[np.ndarray] = None # Boolean mask
    noise_level: float = 0.0              # Relative measurement noise injected
    provenance: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.x = np.asarray(self.x, dtype=np.float64)
        self.t = np.asarray(self.t, dtype=np.float64)
        self.u = np.asarray(self.u, dtype=np.float64)
        if self.spatial_dim not in (1, 2):
            raise NotImplementedError(f"SpatiotemporalField supports spatial_dim 1 or 2, got {self.spatial_dim}")
        if self.spatial_dim == 2:
            if self.y is None:
                raise ValueError("SpatiotemporalField with spatial_dim=2 requires non-None 'y' array.")
            self.y = np.asarray(self.y, dtype=np.float64)

    @property
    def num_time_steps(self) -> int:
        return len(self.t)

    @property
    def num_spatial_points(self) -> int:
        if self.spatial_dim == 1:
            return len(self.x)
        return len(self.x) * len(self.y)

    @property
    def num_spatial_points_x(self) -> int:
        return len(self.x)

    @property
    def num_spatial_points_y(self) -> int:
        return len(self.y) if self.y is not None else 0

    @property
    def dx(self) -> float:
        return float(self.x[1] - self.x[0]) if len(self.x) > 1 else 0.0

    @property
    def dy(self) -> float:
        if self.y is not None and len(self.y) > 1:
            return float(self.y[1] - self.y[0])
        return 0.0

    @property
    def dt(self) -> float:
        return float(self.t[1] - self.t[0]) if len(self.t) > 1 else 0.0

    def get_channel(self, channel: Any) -> np.ndarray:
        """Extract a single channel as an array (M, Nx) or (M, Nx, Ny)."""
        if isinstance(channel, str):
            if channel not in self.channel_names:
                raise KeyError(f"Channel '{channel}' not found in {self.channel_names}")
            idx = self.channel_names.index(channel)
        else:
            idx = int(channel)

        if self.spatial_dim == 1:
            if self.u.ndim == 2:
                return self.u
            return self.u[..., idx]
        else:
            if self.u.ndim == 3:
                return self.u
            return self.u[..., idx]

    def compute_sha256(self) -> str:
        """Compute cryptographic hash of spatiotemporal grid and observations."""
        hasher = hashlib.sha256()
        hasher.update(self.pde_name.encode("utf-8"))
        hasher.update(self.x.tobytes())
        if self.y is not None:
            hasher.update(self.y.tobytes())
        hasher.update(self.t.tobytes())
        hasher.update(self.u.tobytes())
        return hasher.hexdigest()


@dataclass
class SpatiotemporalDataset:
    """
    Immutable collection of spatiotemporal PDE fields (e.g., across varying initial conditions).
    """
    pde_name: str
    channel_names: List[str]
    fields: List[SpatiotemporalField]
    dataset_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.dataset_hash:
            self.dataset_hash = self.compute_integrity_hash()

    def compute_integrity_hash(self) -> str:
        hasher = hashlib.sha256()
        hasher.update(self.pde_name.encode("utf-8"))
        for fld in self.fields:
            hasher.update(fld.compute_sha256().encode("utf-8"))
        return hasher.hexdigest()

    @property
    def num_fields(self) -> int:
        return len(self.fields)
