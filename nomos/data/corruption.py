"""
NOMOS Observation Corruption & Realistic Sampling
Agents C05, C06, C07
"""

from typing import List, Optional, Tuple
import numpy as np
from nomos.data.schema import Trajectory, TrajectoryDataset


def inject_gaussian_noise(
    trajectory: Trajectory,
    noise_ratio: float,
    seed: Optional[int] = None,
) -> Trajectory:
    """
    Inject proportional Gaussian noise:
    x_noisy = x + epsilon, where epsilon ~ N(0, (noise_ratio * std(x))^2)
    Preserves x_clean and x_dot_true for independent evaluation.
    """
    if noise_ratio <= 0.0:
        return trajectory

    rng = np.random.default_rng(seed)
    clean_x = trajectory.x if trajectory.x_clean is None else trajectory.x_clean
    std_per_dim = np.std(clean_x, axis=0, keepdims=True)
    std_per_dim[std_per_dim < 1e-12] = 1.0

    noise = rng.normal(0.0, noise_ratio * std_per_dim, size=clean_x.shape)
    corrupted_x = clean_x + noise

    return Trajectory(
        id=f"{trajectory.id}_noise_{noise_ratio:.3f}",
        t=np.copy(trajectory.t),
        x=corrupted_x,
        x_clean=np.copy(clean_x),
        x_dot_true=trajectory.x_dot_true,
        metadata={**trajectory.metadata, "noise_ratio": float(noise_ratio), "noise_seed": seed},
    )


def sample_irregular_time(
    trajectory: Trajectory,
    jitter_fraction: float = 0.2,
    seed: Optional[int] = None,
) -> Trajectory:
    """
    Simulate non-uniform temporal jitter:
    t_new[k] = t[k] + Uniform(-jitter * dt, jitter * dt), maintaining strict monotonicity.
    Agent C06.
    """
    rng = np.random.default_rng(seed)
    t = trajectory.t
    dt_avg = np.mean(np.diff(t))
    jitter = rng.uniform(-jitter_fraction * dt_avg, jitter_fraction * dt_avg, size=len(t))
    jitter[0] = 0.0  # Preserve t0
    t_jittered = np.sort(t + jitter)

    # Ensure strictly increasing
    for i in range(1, len(t_jittered)):
        if t_jittered[i] <= t_jittered[i - 1]:
            t_jittered[i] = t_jittered[i - 1] + 1e-5

    return Trajectory(
        id=f"{trajectory.id}_jitter_{jitter_fraction:.2f}",
        t=t_jittered,
        x=np.copy(trajectory.x),
        x_clean=trajectory.x_clean,
        x_dot_true=trajectory.x_dot_true,
        metadata={**trajectory.metadata, "jitter_fraction": float(jitter_fraction)},
    )


def apply_missing_observations(
    trajectory: Trajectory,
    drop_rate: float = 0.1,
    seed: Optional[int] = None,
) -> Trajectory:
    """
    Simulate random observation dropout (missing samples).
    Agent C07.
    """
    rng = np.random.default_rng(seed)
    M = len(trajectory.t)
    keep_mask = rng.uniform(0.0, 1.0, size=M) >= drop_rate
    keep_mask[0] = True  # Always preserve first point
    keep_mask[-1] = True  # Always preserve last point

    return Trajectory(
        id=f"{trajectory.id}_drop_{drop_rate:.2f}",
        t=trajectory.t[keep_mask],
        x=trajectory.x[keep_mask],
        x_clean=trajectory.x_clean[keep_mask] if trajectory.x_clean is not None else None,
        x_dot_true=trajectory.x_dot_true[keep_mask] if trajectory.x_dot_true is not None else None,
        metadata={**trajectory.metadata, "drop_rate": float(drop_rate)},
    )
