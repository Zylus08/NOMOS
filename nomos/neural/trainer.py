"""
NOMOS Neural Dynamics Surrogate Trainer
Milestone M2 — Phase 4 Derivative Supervision
Agents D07 & D08
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from nomos.neural.surrogate import NeuralDynamicsSurrogate


class SurrogateTrainer:
    """
    Trains NeuralDynamicsSurrogate on estimated trajectory derivatives.
    Enforces deterministic seeding, train/val separation, and early stopping.
    """

    def __init__(
        self,
        hidden_dim: int = 64,
        num_layers: int = 3,
        lr: float = 1e-3,
        weight_decay: float = 1e-5,
        max_epochs: int = 80,
        batch_size: int = 64,
        patience: int = 12,
        seed: int = 42,
    ):
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lr = lr
        self.weight_decay = weight_decay
        self.max_epochs = max_epochs
        self.batch_size = batch_size
        self.patience = patience
        self.seed = seed

    def fit(
        self,
        X_train: np.ndarray,
        X_dot_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        X_dot_val: Optional[np.ndarray] = None,
    ) -> Tuple[NeuralDynamicsSurrogate, Dict[str, Any]]:
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)

        M, state_dim = X_train.shape

        # Train/val split if val not provided
        if X_val is None:
            val_size = max(1, int(0.2 * M))
            perm = np.random.permutation(M)
            tr_idx, val_idx = perm[val_size:], perm[:val_size]
            X_tr, y_tr = X_train[tr_idx], X_dot_train[tr_idx]
            X_v, y_v = X_train[val_idx], X_dot_train[val_idx]
        else:
            X_tr, y_tr = X_train, X_dot_train
            X_v, y_v = X_val, X_dot_val

        # Initialize surrogate
        surrogate = NeuralDynamicsSurrogate(
            state_dim=state_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
        )
        x_mean = np.mean(X_tr, axis=0)
        x_std = np.std(X_tr, axis=0)
        surrogate.set_normalization(x_mean, x_std)

        # Prepare PyTorch datasets
        ds_tr = TensorDataset(
            torch.from_numpy(X_tr.astype(np.float32)),
            torch.from_numpy(y_tr.astype(np.float32)),
        )
        loader_tr = DataLoader(ds_tr, batch_size=self.batch_size, shuffle=True)

        X_v_t = torch.from_numpy(X_v.astype(np.float32))
        y_v_t = torch.from_numpy(y_v.astype(np.float32))

        optimizer = torch.optim.Adam(
            surrogate.parameters(), lr=self.lr, weight_decay=self.weight_decay
        )
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="min", factor=0.5, patience=5
        )
        criterion = nn.MSELoss()

        best_val_loss = float("inf")
        best_state = None
        epochs_no_improve = 0
        loss_history = []

        for epoch in range(self.max_epochs):
            surrogate.train()
            train_loss_epoch = 0.0
            for bx, by in loader_tr:
                optimizer.zero_grad()
                pred = surrogate(bx)
                loss = criterion(pred, by)
                loss.backward()
                optimizer.step()
                train_loss_epoch += loss.item() * len(bx)

            train_loss_epoch /= len(X_tr)

            # Evaluate validation
            surrogate.eval()
            with torch.no_grad():
                val_pred = surrogate(X_v_t)
                val_loss = criterion(val_pred, y_v_t).item()

            scheduler.step(val_loss)
            loss_history.append((train_loss_epoch, val_loss))

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_state = {k: v.cpu().clone() for k, v in surrogate.state_dict().items()}
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= self.patience:
                    break

        if best_state is not None:
            surrogate.load_state_dict(best_state)

        # Final metrics
        pred_val_np = surrogate.predict_numpy(X_v)
        diff = pred_val_np - y_v
        rmse = float(np.sqrt(np.mean(diff ** 2)))
        ss_tot = np.sum((y_v - np.mean(y_v, axis=0)) ** 2)
        r2 = float(1.0 - np.sum(diff ** 2) / (ss_tot + 1e-12))

        metrics = {
            "val_loss": best_val_loss,
            "val_rmse": rmse,
            "val_r2": r2,
            "epochs_trained": len(loss_history),
        }
        return surrogate, metrics
