"""
NOMOS Information-Gain Experiment Selection & Acquisition Strategies
Phase 3 & Phase 7: Multi-Strategy Experiment Design with Cost Normalization
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Callable
import numpy as np

from nomos.closed_loop.portfolio import ScientificHypothesis, HypothesisPortfolio
from nomos.pde.operators import compute_derivative


class AcquisitionStrategy(str, Enum):
    RANDOM = "random"
    FIXED = "fixed"
    GREEDY_DISAGREEMENT = "greedy_disagreement"
    COST_NORMALIZED = "cost_normalized"
    UNCERTAINTY_AWARE = "uncertainty_aware"
    MODEL_DISCRIMINATION = "model_discrimination"
    HANDCRAFTED_SCHEDULE = "handcrafted_schedule"


class ExperimentAcquisitionEngine:
    """
    Autonomous Experiment Design Engine.
    Evaluates candidate experimental initial conditions against active hypotheses
    using functional vector-field divergence, Bayesian ensemble entropy, or cost-normalized gain.
    """

    def __init__(self, strategy: AcquisitionStrategy = AcquisitionStrategy.GREEDY_DISAGREEMENT, random_seed: int = 42):
        self.strategy = strategy
        self.random_seed = int(random_seed)

    def evaluate_model_vector_field(
        self,
        hypothesis: ScientificHypothesis,
        u: np.ndarray,
        dx: float,
        dy: float = 0.0,
        periodic: bool = True,
    ) -> np.ndarray:
        """
        Evaluate predicted time derivative u_t = f(u; theta) for a given hypothesis.
        """
        is_2d = (u.ndim >= 2 and dy > 0.0)

        # Handle multichannel 2D state (e.g. (Nx, Ny, 2))
        u_chan = u[..., 0] if (u.ndim == 3 and is_2d) else u
        v_chan = u[..., 1] if (u.ndim == 3 and is_2d) else None

        f_pred = np.zeros(u_chan.shape, dtype=np.float64)

        for term, coef in hypothesis.parameters.items():
            if abs(coef) < 1e-6:
                continue

            if term == "1":
                f_pred = f_pred + coef * 1.0
            elif term in ("u", "v", "omega"):
                arr = v_chan if (term == "v" and v_chan is not None) else u_chan
                f_pred = f_pred + coef * arr
            elif term == "u_x" or term == "d_u_x":
                axis = 1 if is_2d else -1
                du_x = compute_derivative(u_chan, dx=dx, order=1, method="spectral" if periodic else "fd", periodic=periodic, axis=axis)
                f_pred = f_pred + coef * du_x
            elif term == "u_xx" or term == "d_u_xx":
                axis = 1 if is_2d else -1
                du_xx = compute_derivative(u_chan, dx=dx, order=2, method="spectral" if periodic else "fd", periodic=periodic, axis=axis)
                f_pred = f_pred + coef * du_xx
            elif term == "u_xxx":
                axis = 1 if is_2d else -1
                du_xxx = compute_derivative(u_chan, dx=dx, order=3, method="spectral" if periodic else "fd", periodic=periodic, axis=axis)
                f_pred = f_pred + coef * du_xxx
            elif term == "u_xxxx":
                axis = 1 if is_2d else -1
                du_xxxx = compute_derivative(u_chan, dx=dx, order=4, method="spectral" if periodic else "fd", periodic=periodic, axis=axis)
                f_pred = f_pred + coef * du_xxxx
            elif term == "u*u_x":
                axis = 1 if is_2d else -1
                du_x = compute_derivative(u_chan, dx=dx, order=1, method="spectral" if periodic else "fd", periodic=periodic, axis=axis)
                f_pred = f_pred + coef * (u_chan * du_x)
            elif term == "u^2":
                f_pred = f_pred + coef * (u_chan**2)
            elif term == "u^3":
                f_pred = f_pred + coef * (u_chan**3)
            elif term in ("(u^3)_xx", "d2_u3_dx2", "lap_u3"):
                axis = 1 if is_2d else -1
                du3_xx = compute_derivative(u_chan**3, dx=dx, order=2, method="spectral" if periodic else "fd", periodic=periodic, axis=axis)
                f_pred = f_pred + coef * du3_xx
            elif term == "u*v^2":
                if v_chan is not None:
                    f_pred = f_pred + coef * (u_chan * (v_chan**2))
            elif term in ("u^2*v", "u^2_v"):
                if v_chan is not None:
                    f_pred = f_pred + coef * ((u_chan**2) * v_chan)
            elif term in ("lap_u", "lap_v", "lap_omega"):
                arr = v_chan if (term == "lap_v" and v_chan is not None) else u_chan
                if is_2d:
                    dxx = compute_derivative(arr, dx=dx, order=2, method="spectral" if periodic else "fd", periodic=periodic, axis=0)
                    dyy = compute_derivative(arr, dx=dy, order=2, method="spectral" if periodic else "fd", periodic=periodic, axis=1)
                    f_pred = f_pred + coef * (dxx + dyy)
                else:
                    dxx = compute_derivative(arr, dx=dx, order=2, method="spectral" if periodic else "fd", periodic=periodic, axis=-1)
                    f_pred = f_pred + coef * dxx
            elif term == "advection_omega" and is_2d:
                # 2D Navier-Stokes vorticity convective advection
                # u_adv * omega_x + v_adv * omega_y
                om = u_chan
                Nx, Ny = om.shape[:2]
                Lx = Nx * dx
                Ly = Ny * dy
                kx = (2.0 * np.pi / Lx) * np.fft.fftfreq(Nx, 1.0 / Nx)
                ky = (2.0 * np.pi / Ly) * np.fft.fftfreq(Ny, 1.0 / Ny)
                KX, KY = np.meshgrid(kx, ky, indexing="ij")
                K2 = KX**2 + KY**2
                inv_K2 = np.zeros_like(K2)
                inv_K2[K2 > 1e-12] = 1.0 / K2[K2 > 1e-12]
                om_hat = np.fft.fftn(om)
                psi_hat = om_hat * inv_K2
                u_vel = np.real(np.fft.ifftn(1j * KY * psi_hat))
                v_vel = np.real(np.fft.ifftn(-1j * KX * psi_hat))
                om_x = np.real(np.fft.ifftn(1j * KX * om_hat))
                om_y = np.real(np.fft.ifftn(1j * KY * om_hat))
                advec = u_vel * om_x + v_vel * om_y
                f_pred = f_pred + coef * advec
            else:
                pass

        return f_pred

    def compute_pairwise_disagreement(
        self,
        h1: ScientificHypothesis,
        h2: ScientificHypothesis,
        u0: np.ndarray,
        dx: float,
        dy: float = 0.0,
        periodic: bool = True,
    ) -> float:
        """
        Compute integrated vector-field divergence:
        D(u0; h1, h2) = || f_h1(u0) - f_h2(u0) ||_2^2
        """
        f1 = self.evaluate_model_vector_field(h1, u0, dx, dy, periodic)
        f2 = self.evaluate_model_vector_field(h2, u0, dx, dy, periodic)
        return float(np.mean((f1 - f2) ** 2))

    def compute_ensemble_variance(
        self,
        hypotheses: List[ScientificHypothesis],
        u0: np.ndarray,
        dx: float,
        dy: float = 0.0,
        periodic: bool = True,
    ) -> float:
        """
        Compute evidence-weighted predictive variance across hypothesis ensemble:
        Var(u0) = sum_k w_k || f_k(u0) - bar{f}(u0) ||_2^2
        """
        if not hypotheses:
            return 0.0

        weights = np.array([h.evidence_score for h in hypotheses])
        if np.sum(weights) < 1e-12:
            weights = np.ones(len(hypotheses)) / len(hypotheses)
        else:
            weights = weights / np.sum(weights)

        fields = [self.evaluate_model_vector_field(h, u0, dx, dy, periodic) for h in hypotheses]
        mean_field = np.zeros_like(fields[0])
        for w, f in zip(weights, fields):
            mean_field += w * f

        total_var = 0.0
        for w, f in zip(weights, fields):
            total_var += w * float(np.mean((f - mean_field) ** 2))

        return total_var

    def select_experiment(
        self,
        portfolio: HypothesisPortfolio,
        candidate_pool: List[Tuple[str, np.ndarray, float]],  # (label, u0, expected_cost)
        dx: float,
        dy: float = 0.0,
        periodic: bool = True,
        iteration_index: int = 0,
    ) -> Tuple[str, np.ndarray, float, Dict[str, float]]:
        """
        Select optimal experimental initial condition using configured strategy.
        Returns: (chosen_label, chosen_u0, acquisition_score, score_ledger).
        """
        active = portfolio.get_active()
        rng = np.random.RandomState(self.random_seed + iteration_index)

        # Fallback if no active hypotheses
        if not active or len(active) == 1:
            # Pick next candidate or random
            idx = iteration_index % len(candidate_pool)
            label, u0, _ = candidate_pool[idx]
            return label, u0, 1.0, {label: 1.0}

        top1 = active[0]
        top2 = active[1] if len(active) > 1 else active[0]

        scores: Dict[str, float] = {}

        if self.strategy == AcquisitionStrategy.RANDOM:
            # Uniform random choice
            chosen_idx = rng.randint(0, len(candidate_pool))
            for i, (lbl, u0, _) in enumerate(candidate_pool):
                scores[lbl] = 1.0 if i == chosen_idx else 0.0
            lbl, u0, _ = candidate_pool[chosen_idx]
            return lbl, u0, 1.0, scores

        elif self.strategy == AcquisitionStrategy.FIXED:
            # Deterministic schedule (round-robin / sequential)
            chosen_idx = iteration_index % len(candidate_pool)
            for i, (lbl, u0, _) in enumerate(candidate_pool):
                scores[lbl] = 1.0 if i == chosen_idx else 0.0
            lbl, u0, _ = candidate_pool[chosen_idx]
            return lbl, u0, 1.0, scores

        elif self.strategy == AcquisitionStrategy.GREEDY_DISAGREEMENT:
            # Maximize divergence between top two competing laws
            best_score = -1.0
            best_tuple = candidate_pool[0]
            for lbl, u0, _ in candidate_pool:
                d = self.compute_pairwise_disagreement(top1, top2, u0, dx, dy, periodic)
                scores[lbl] = d
                if d > best_score:
                    best_score = d
                    best_tuple = (lbl, u0, _)
            return best_tuple[0], best_tuple[1], best_score, scores

        elif self.strategy == AcquisitionStrategy.COST_NORMALIZED:
            # Maximize disagreement per unit experimental cost
            best_score = -1.0
            best_tuple = candidate_pool[0]
            for lbl, u0, cost in candidate_pool:
                d = self.compute_pairwise_disagreement(top1, top2, u0, dx, dy, periodic)
                cost_val = max(cost, 1e-4)
                score_norm = d / cost_val
                scores[lbl] = score_norm
                if score_norm > best_score:
                    best_score = score_norm
                    best_tuple = (lbl, u0, cost)
            return best_tuple[0], best_tuple[1], best_score, scores

        elif self.strategy == AcquisitionStrategy.UNCERTAINTY_AWARE:
            # Maximize predictive variance across all active hypotheses
            best_score = -1.0
            best_tuple = candidate_pool[0]
            portfolio.compute_evidence_weights()
            for lbl, u0, _ in candidate_pool:
                var = self.compute_ensemble_variance(active, u0, dx, dy, periodic)
                scores[lbl] = var
                if var > best_score:
                    best_score = var
                    best_tuple = (lbl, u0, _)
            return best_tuple[0], best_tuple[1], best_score, scores

        elif self.strategy == AcquisitionStrategy.MODEL_DISCRIMINATION:
            # Multi-hypothesis Bayesian B-optimal design: weighted pairwise divergence
            best_score = -1.0
            best_tuple = candidate_pool[0]
            portfolio.compute_evidence_weights()
            weights = np.array([h.evidence_score for h in active])
            if np.sum(weights) < 1e-12:
                weights = np.ones(len(active)) / len(active)
            else:
                weights = weights / np.sum(weights)

            for lbl, u0, _ in candidate_pool:
                fields = [self.evaluate_model_vector_field(h, u0, dx, dy, periodic) for h in active]
                disc_score = 0.0
                for i in range(len(active)):
                    for j in range(i + 1, len(active)):
                        div = float(np.mean((fields[i] - fields[j]) ** 2))
                        disc_score += weights[i] * weights[j] * div
                scores[lbl] = disc_score
                if disc_score > best_score:
                    best_score = disc_score
                    best_tuple = (lbl, u0, _)
            return best_tuple[0], best_tuple[1], best_score, scores

        elif self.strategy == AcquisitionStrategy.HANDCRAFTED_SCHEDULE:
            # Domain-expert heuristic: rank candidates by spatial complexity / gradient energy
            def gradient_energy(arr: np.ndarray) -> float:
                u_c = arr[..., 0] if arr.ndim >= 2 else arr
                gx = compute_derivative(u_c, dx=dx, order=1, method="spectral" if periodic else "fd", periodic=periodic, axis=-1)
                return float(np.mean(gx**2) + np.var(u_c))

            ranked_pool = sorted(candidate_pool, key=lambda t: gradient_energy(t[1]), reverse=True)
            chosen_idx = iteration_index % len(ranked_pool)
            chosen_lbl, chosen_u0, _ = ranked_pool[chosen_idx]
            for lbl, u0, _ in candidate_pool:
                scores[lbl] = gradient_energy(u0)
            return chosen_lbl, chosen_u0, scores[chosen_lbl], scores

        else:
            raise ValueError(f"Unsupported acquisition strategy: {self.strategy}")
