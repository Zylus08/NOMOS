"""
NOMOS Weak-Form PDE Discovery Engine (WSINDy)
Phase 5: Weak / Integral Form Spatiotemporal Identification
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from nomos.pde.schema import SpatiotemporalField
from nomos.pde.strong_form import PDEDiscoveryResult
from nomos.sparse.stlsq import STLSQ


class WeakFormPDEDiscovery:
    """
    Weak-Form Sparse PDE Identification (WSINDy).
    Projects PDE onto smooth, compactly supported space-time test functions:
        phi(x, t) = psi(x) * chi(t)
    Applies integration by parts to transfer spatial and temporal derivatives
    from the noisy observed field u onto the smooth test function phi:
        int (u_t * phi) dx dt = - int (u * phi_t) dx dt + [boundary]
        int (u_x * phi) dx dt = - int (u * phi_x) dx dt + [boundary]
        int (u_xx * phi) dx dt = int (u * phi_xx) dx dt + [boundary]
        int (u_xxx * phi) dx dt = - int (u * phi_xxx) dx dt + [boundary]
        int (u_xxxx * phi) dx dt = int (u * phi_xxxx) dx dt + [boundary]
        int (u * u_x * phi) dx dt = - 1/2 * int (u^2 * phi_x) dx dt + [boundary]
    Because test functions vanish on the boundary of their compact support,
    all boundary terms vanish identically!
    Extremely robust against high measurement noise without requiring derivative filtering.
    """

    def __init__(
        self,
        num_test_functions: int = 120,
        subdomain_scale_x: float = 0.25,
        subdomain_scale_t: float = 0.25,
        poly_order: int = 4,
        threshold: float = 0.05,
        alpha: float = 1e-4,
        random_seed: int = 42,
    ):
        self.num_test_functions = int(num_test_functions)
        self.subdomain_scale_x = float(subdomain_scale_x)
        self.subdomain_scale_t = float(subdomain_scale_t)
        self.poly_order = int(poly_order)
        self.threshold = float(threshold)
        self.alpha = float(alpha)
        self.random_seed = int(random_seed)

    def _compact_test_function_and_derivs(
        self,
        x: np.ndarray,
        t: np.ndarray,
        xc: float,
        tc: float,
        Rx: float,
        Rt: float,
    ) -> Dict[str, np.ndarray]:
        """
        Construct compactly supported polynomial test function:
            psi(x) = (1 - ((x-xc)/Rx)^2)^p   for |x-xc| < Rx, else 0
            chi(t) = (1 - ((t-tc)/Rt)^2)^p   for |t-tc| < Rt, else 0
            phi(x, t) = chi(t)[:, None] * psi(x)[None, :]
        Computes analytical spatial and temporal derivatives up to 4th order.
        """
        # Normalized coordinates
        xi_x = (x - xc) / Rx
        xi_t = (t - tc) / Rt

        mask_x = np.abs(xi_x) < 1.0
        mask_t = np.abs(xi_t) < 1.0

        p = self.poly_order
        # psi(x)
        psi = np.zeros_like(x)
        psi_x = np.zeros_like(x)
        psi_xx = np.zeros_like(x)
        psi_xxx = np.zeros_like(x)
        psi_xxxx = np.zeros_like(x)

        idx_x = np.where(mask_x)[0]
        if len(idx_x) > 0:
            s_x = 1.0 - xi_x[idx_x] ** 2
            # psi = s^p
            psi[idx_x] = s_x**p
            # d/dx s^p = p * s^{p-1} * (-2 xi / Rx)
            psi_x[idx_x] = p * (s_x ** (p - 1)) * (-2.0 * xi_x[idx_x] / Rx)
            # d2/dx2
            if p >= 2:
                psi_xx[idx_x] = (
                    p * (p - 1) * (s_x ** (p - 2)) * ((-2.0 * xi_x[idx_x] / Rx) ** 2)
                    + p * (s_x ** (p - 1)) * (-2.0 / (Rx**2))
                )
            if p >= 3:
                # 3rd derivative
                term1 = p * (p - 1) * (p - 2) * (s_x ** (p - 3)) * ((-2.0 * xi_x[idx_x] / Rx) ** 3)
                term2 = 3.0 * p * (p - 1) * (s_x ** (p - 2)) * (-2.0 / (Rx**2)) * (-2.0 * xi_x[idx_x] / Rx)
                psi_xxx[idx_x] = term1 + term2
            if p >= 4:
                # 4th derivative
                term1 = p * (p - 1) * (p - 2) * (p - 3) * (s_x ** (p - 4)) * ((-2.0 * xi_x[idx_x] / Rx) ** 4)
                term2 = 6.0 * p * (p - 1) * (p - 2) * (s_x ** (p - 3)) * ((-2.0 * xi_x[idx_x] / Rx) ** 2) * (-2.0 / (Rx**2))
                term3 = 3.0 * p * (p - 1) * (s_x ** (p - 2)) * ((-2.0 / (Rx**2)) ** 2)
                psi_xxxx[idx_x] = term1 + term2 + term3

        # chi(t)
        chi = np.zeros_like(t)
        chi_t = np.zeros_like(t)

        idx_t = np.where(mask_t)[0]
        if len(idx_t) > 0:
            s_t = 1.0 - xi_t[idx_t] ** 2
            chi[idx_t] = s_t**p
            chi_t[idx_t] = p * (s_t ** (p - 1)) * (-2.0 * xi_t[idx_t] / Rt)

        # 2D space-time tensors: shape (M, N)
        return {
            "phi": chi[:, None] * psi[None, :],
            "phi_t": chi_t[:, None] * psi[None, :],
            "phi_x": chi[:, None] * psi_x[None, :],
            "phi_xx": chi[:, None] * psi_xx[None, :],
            "phi_xxx": chi[:, None] * psi_xxx[None, :],
            "phi_xxxx": chi[:, None] * psi_xxxx[None, :],
        }

    def build_weak_form_system(
        self, field: SpatiotemporalField
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Build WSINDy linear system G * Xi = b using space-time quadrature.
        """
        U = field.u
        x = field.x
        t = field.t
        dx = field.dx
        dt = field.dt

        Lx = x[-1] - x[0]
        Lt = t[-1] - t[0]

        Rx = self.subdomain_scale_x * Lx
        Rt = self.subdomain_scale_t * Lt

        rng = np.random.RandomState(self.random_seed)

        # Candidate feature names
        feature_names = ["u", "u_x", "u_xx", "u_xxx", "u_xxxx", "u*u_x", "u^2", "u^3"]
        P = len(feature_names)
        K = self.num_test_functions

        G = np.zeros((K, P), dtype=np.float64)
        b = np.zeros(K, dtype=np.float64)

        # Sample test function centers strictly in interior so support stays within domain
        xc_pool = rng.uniform(x[0] + Rx, x[-1] - Rx, size=K)
        tc_pool = rng.uniform(t[0] + Rt, t[-1] - Rt, size=K)

        for k_idx in range(K):
            xc = xc_pool[k_idx]
            tc = tc_pool[k_idx]

            tf = self._compact_test_function_and_derivs(x, t, xc, tc, Rx, Rt)

            # Target b_k = <u_t, phi> = - <u, phi_t>
            b[k_idx] = -float(np.sum(U * tf["phi_t"]) * dx * dt)

            # Feature 0: <u, phi> = int u * phi dx dt
            G[k_idx, 0] = float(np.sum(U * tf["phi"]) * dx * dt)

            # Feature 1: <u_x, phi> = - <u, phi_x>
            G[k_idx, 1] = -float(np.sum(U * tf["phi_x"]) * dx * dt)

            # Feature 2: <u_xx, phi> = <u, phi_xx>
            G[k_idx, 2] = float(np.sum(U * tf["phi_xx"]) * dx * dt)

            # Feature 3: <u_xxx, phi> = - <u, phi_xxx>
            G[k_idx, 3] = -float(np.sum(U * tf["phi_xxx"]) * dx * dt)

            # Feature 4: <u_xxxx, phi> = <u, phi_xxxx>
            G[k_idx, 4] = float(np.sum(U * tf["phi_xxxx"]) * dx * dt)

            # Feature 5: <u * u_x, phi> = 1/2 <(u^2)_x, phi> = - 1/2 <u^2, phi_x>
            G[k_idx, 5] = -0.5 * float(np.sum((U**2) * tf["phi_x"]) * dx * dt)

            # Feature 6: <u^2, phi>
            G[k_idx, 6] = float(np.sum((U**2) * tf["phi"]) * dx * dt)

            # Feature 7: <u^3, phi>
            G[k_idx, 7] = float(np.sum((U**3) * tf["phi"]) * dx * dt)

        return G, b, feature_names

    def fit(self, field: SpatiotemporalField) -> PDEDiscoveryResult:
        import time

        t0 = time.time()
        G, b, feature_names = self.build_weak_form_system(field)

        # STLSQ on integral matrix
        opt = STLSQ(
            threshold=self.threshold,
            alpha=self.alpha,
            max_iter=50,
            normalize_columns=True,
            refit_active_set=True,
        )

        res = opt.fit(G, b.reshape(-1, 1))
        coefs = res.coef.flatten()
        duration = time.time() - t0

        active_terms = []
        coef_dict = {}
        for name, val in zip(feature_names, coefs):
            if abs(val) > 1e-4:
                coef_dict[name] = float(val)
                active_terms.append(f"{val:+.4f}*{name}")

        eq_str = "u_t = " + (" ".join(active_terms) if active_terms else "0.0")

        return PDEDiscoveryResult(
            pde_name=field.pde_name,
            discovered_equation=eq_str,
            feature_names=feature_names,
            coefficients=coef_dict,
            residual_norm=float(res.residual_norm),
            support_mask=[abs(c) > 1e-4 for c in coefs],
            num_evaluations=len(feature_names),
            execution_time_seconds=duration,
            discovery_mode="weak_form",
            metadata={
                "num_test_functions": self.num_test_functions,
                "poly_order": self.poly_order,
                "converged": res.converged,
                "iterations": res.iterations,
            },
        )
