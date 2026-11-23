"""
Project NOMOS — Milestone M4 2D Field Schema & Isolation Tests
Verifies 2D grid construction, multichannel shapes, hash integrity, and evaluator sandboxing.
"""

import pytest
import numpy as np

from nomos.pde.schema import Grid2D, TimeGrid, SpatiotemporalField, BoundaryConditionType
from nomos.pde.isolation import create_learner_field_observation


class Test2DSchemaAndIsolation:

    def test_grid2d_properties_and_meshgrid(self):
        """Verify Grid2D spacing, shapes, and meshgrid coordinates."""
        grid = Grid2D.create((0.0, 2.0 * np.pi), (-1.0, 1.0), 32, 16, periodic=True)
        assert grid.num_points_x == 32
        assert grid.num_points_y == 16
        assert abs(grid.dx - (2.0 * np.pi / 32)) < 1e-10
        assert abs(grid.dy - (2.0 / 16)) < 1e-10

        X, Y = grid.meshgrid
        assert X.shape == (32, 16)
        assert Y.shape == (32, 16)
        assert np.isclose(X[0, 0], 0.0)
        assert np.isclose(Y[0, 0], -1.0)

    def test_spatiotemporal_field_2d_multichannel(self):
        """Verify 2D multi-channel field shape invariants, dx/dy, and channel extraction."""
        x = np.linspace(0, 1, 10)
        y = np.linspace(0, 2, 20)
        t = np.linspace(0, 0.5, 5)
        # 2 channels: (M, Nx, Ny, 2)
        u_data = np.zeros((5, 10, 20, 2), dtype=np.float64)
        u_data[..., 0] = 1.0  # channel 'u'
        u_data[..., 1] = 2.0  # channel 'v'

        field = SpatiotemporalField(
            id="test_2d_field",
            pde_name="coupled_system",
            x=x,
            y=y,
            t=t,
            u=u_data,
            channel_names=["u", "v"],
            spatial_dim=2,
            u_clean=u_data.copy(),
            u_t_true=np.zeros_like(u_data),
            true_parameters={"alpha": 0.5},
        )

        assert field.num_time_steps == 5
        assert field.num_spatial_points == 200
        assert field.num_spatial_points_x == 10
        assert field.num_spatial_points_y == 20
        assert np.isclose(field.dx, 1.0 / 9.0)
        assert np.isclose(field.dy, 2.0 / 19.0)

        # Channel access
        u_chan = field.get_channel("u")
        v_chan = field.get_channel("v")
        assert u_chan.shape == (5, 10, 20)
        assert np.all(u_chan == 1.0)
        assert np.all(v_chan == 2.0)

        # Hash check
        h1 = field.compute_sha256()
        assert len(h1) == 64

    def test_evaluator_isolation_sandbox(self):
        """Verify strict learner observation purges u_clean, u_t_true, and true_parameters."""
        x = np.linspace(0, 1, 8)
        y = np.linspace(0, 1, 8)
        t = np.linspace(0, 1, 4)
        u_data = np.ones((4, 8, 8, 2))

        field = SpatiotemporalField(
            id="leakage_target",
            pde_name="reaction_diffusion",
            x=x,
            y=y,
            t=t,
            u=u_data,
            channel_names=["u", "v"],
            spatial_dim=2,
            u_clean=u_data.copy(),
            u_t_true=u_data.copy(),
            true_parameters={"D_u": 0.16, "D_v": 0.08},
        )

        obs = create_learner_field_observation(field)
        assert obs.u_clean is None
        assert obs.u_t_true is None
        assert obs.true_parameters is None
        assert obs.provenance["isolated"] is True
        assert obs.provenance["leakage_protected"] is True
