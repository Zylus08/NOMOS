"""
NOMOS PyTorch Neural Dynamics Surrogate Model
Milestone M2 — Phase 4 Neural Surrogate
Agents D07 & D08
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from typing import Dict, List, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn


class NeuralDynamicsSurrogate(nn.Module):
    """
    Continuous neural surrogate approximating:
        dx/dt = f_theta(x, u)
    Uses smooth SiLU / Tanh activations ensuring continuous Jacobian existence.
    Features built-in state standardization buffers.
    """

    def __init__(
        self,
        state_dim: int,
        control_dim: int = 0,
        hidden_dim: int = 64,
        num_layers: int = 3,
        activation: str = "silu",
    ):
        super().__init__()
        self.state_dim = state_dim
        self.control_dim = control_dim
        input_dim = state_dim + control_dim

        # Normalization buffers
        self.register_buffer("x_mean", torch.zeros(input_dim))
        self.register_buffer("x_std", torch.ones(input_dim))

        act_fn = nn.SiLU() if activation.lower() == "silu" else nn.Tanh()

        layers = []
        layers.append(nn.Linear(input_dim, hidden_dim))
        layers.append(act_fn)
        for _ in range(num_layers - 2):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(act_fn)
        layers.append(nn.Linear(hidden_dim, state_dim))

        self.net = nn.Sequential(*layers)

    def set_normalization(self, x_mean: np.ndarray, x_std: np.ndarray):
        x_std_safe = np.where(x_std < 1e-8, 1.0, x_std)
        self.x_mean.copy_(torch.from_numpy(x_mean).float())
        self.x_std.copy_(torch.from_numpy(x_std_safe).float())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Standardize input
        x_norm = (x - self.x_mean) / self.x_std
        return self.net(x_norm)

    def predict_numpy(self, x_np: np.ndarray) -> np.ndarray:
        self.eval()
        with torch.no_grad():
            x_t = torch.from_numpy(np.asarray(x_np, dtype=np.float32))
            pred = self.forward(x_t)
            return pred.cpu().numpy().astype(np.float64)

    def compute_jacobian(self, x_np: np.ndarray) -> np.ndarray:
        """
        Compute full Jacobian matrix J_ij = d(f_i)/d(x_j) for each state row.
        Returns array of shape (M, state_dim, input_dim).
        """
        self.eval()
        x_t = torch.from_numpy(np.asarray(x_np, dtype=np.float32)).requires_grad_(True)
        M = x_t.shape[0]

        jacobians = []
        for i in range(M):
            single_x = x_t[i : i + 1]
            # PyTorch functional jacobian
            jac = torch.autograd.functional.jacobian(self.forward, single_x)
            # jac shape: (1, state_dim, 1, input_dim) -> squeeze to (state_dim, input_dim)
            jac_mat = jac.squeeze(0).squeeze(1).detach().cpu().numpy()
            jacobians.append(jac_mat)

        return np.array(jacobians, dtype=np.float64)
