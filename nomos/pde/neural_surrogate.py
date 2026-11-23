"""
NOMOS 1D Spatiotemporal Convolutional Dynamics Surrogate
Phase 7: Neural-Guided PDE Discovery
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from nomos.pde.schema import SpatiotemporalField
from nomos.pde.operators import finite_difference_1d


class Conv1DPDESurrogate(nn.Module):
    """
    1D Convolutional Neural Network surrogate for local spatiotemporal dynamics:
        u_t(x, t) = F_theta(u(x - stencil : x + stencil, t))
    Uses periodic circular padding to respect spatial domain boundaries.
    """

    def __init__(self, in_channels: int = 1, hidden_dim: int = 32, kernel_size: int = 5):
        super().__init__()
        pad = kernel_size // 2
        self.net = nn.Sequential(
            nn.Conv1d(in_channels, hidden_dim, kernel_size=kernel_size, padding=pad, padding_mode="circular"),
            nn.Tanh(),
            nn.Conv1d(hidden_dim, hidden_dim, kernel_size=kernel_size, padding=pad, padding_mode="circular"),
            nn.Tanh(),
            nn.Conv1d(hidden_dim, 1, kernel_size=kernel_size, padding=pad, padding_mode="circular"),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input shape: (Batch, 1, N)
        return self.net(x)


class NeuralPDESurrogateTrainer:
    """
    Trains Conv1DPDESurrogate on observed spatiotemporal field and extracts
    differential operator sensitivity priors.
    """

    def __init__(
        self,
        epochs: int = 50,
        lr: float = 1e-3,
        hidden_dim: int = 32,
        kernel_size: int = 5,
        random_seed: int = 42,
    ):
        self.epochs = int(epochs)
        self.lr = float(lr)
        self.hidden_dim = int(hidden_dim)
        self.kernel_size = int(kernel_size)
        self.random_seed = int(random_seed)
        self.model: Optional[Conv1DPDESurrogate] = None
        self.training_time_seconds: float = 0.0

    def fit(self, field: SpatiotemporalField) -> Dict[str, Any]:
        """
        Train neural surrogate to predict u_t from spatial snapshots u.
        Target u_t is approximated from data using finite difference.
        """
        import time

        t0 = time.time()
        torch.manual_seed(self.random_seed)
        np.random.seed(self.random_seed)

        U = field.u  # Shape: (M, N)
        dt = field.dt
        dx = field.dx
        M, N = U.shape

        # Approximate u_t target from observations
        U_t_target = finite_difference_1d(U, dx=dt, order=1, accuracy=2, axis=0, periodic=False)

        # Prepare PyTorch tensors (Batch = M, Channels = 1, Spatial = N)
        X_tensor = torch.tensor(U[:, None, :], dtype=torch.float32)
        Y_tensor = torch.tensor(U_t_target[:, None, :], dtype=torch.float32)

        self.model = Conv1DPDESurrogate(
            in_channels=1, hidden_dim=self.hidden_dim, kernel_size=self.kernel_size
        )

        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        criterion = nn.MSELoss()

        self.model.train()
        loss_history = []
        for epoch in range(self.epochs):
            optimizer.zero_grad()
            pred = self.model(X_tensor)
            loss = criterion(pred, Y_tensor)
            loss.backward()
            optimizer.step()
            loss_history.append(float(loss.item()))

        self.training_time_seconds = time.time() - t0

        return {
            "final_loss": loss_history[-1],
            "training_time": self.training_time_seconds,
            "epochs": self.epochs,
        }

    def compute_operator_sensitivities(
        self, field: SpatiotemporalField, candidate_features: List[str]
    ) -> Dict[str, float]:
        """
        Compute sensitivity priors w_k for candidate differential features by correlating
        neural surrogate predictions with candidate differential fields.
        """
        if self.model is None:
            raise RuntimeError("Surrogate model must be trained before computing sensitivities.")

        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.tensor(field.u[:, None, :], dtype=torch.float32)
            u_t_pred = self.model(X_tensor).squeeze(1).cpu().numpy()  # Shape: (M, N)

        # Correlate predicted u_t with candidate differential operators
        from nomos.pde.operators import compute_pde_derivatives_matrix

        derivs = compute_pde_derivatives_matrix(
            field.u, dx=field.dx, dt=field.dt, periodic=True, method="fd"
        )

        sensitivities = {}
        pred_flat = u_t_pred.flatten()
        pred_norm = np.linalg.norm(pred_flat) + 1e-8

        for feat in candidate_features:
            if feat in derivs:
                feat_flat = derivs[feat].flatten()
                feat_norm = np.linalg.norm(feat_flat) + 1e-8
                # Absolute cosine similarity as sensitivity prior
                cos_sim = abs(float(np.dot(pred_flat, feat_flat) / (pred_norm * feat_norm)))
                sensitivities[feat] = max(cos_sim, 0.05)
            else:
                sensitivities[feat] = 0.10

        # Normalize weights
        total = sum(sensitivities.values())
        return {k: v / total for k, v in sensitivities.items()}
