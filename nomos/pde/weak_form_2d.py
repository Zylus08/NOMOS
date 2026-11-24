"""
NOMOS 2D Multichannel Weak-Form PDE Discovery Engine (WSINDy-2D)
Phase 5: Weak / Integral Form Spatiotemporal Identification in 2D
Supports coupled systems (Gray–Scott, FitzHugh–Nagumo) and fluid dynamics (Navier–Stokes 2D).
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from nomos.pde.schema import SpatiotemporalField
from nomos.pde.strong_form import PDEDiscoveryResult
from nomos.sparse.stlsq import STLSQ


class WeakForm2DPDEDiscovery:
    """
    2D Multichannel Weak-Form Sparse PDE Identification (WSINDy-2D).
    Projects PDE onto 3D space-time test functions:
        phi(x, y, t) = psi(x) * theta(y) * chi(t)
    Applies multi-dimensional integration by parts to transfer spatial and temporal
    derivatives from noisy measured fields onto smooth analytical test functions:
        int (w_t * phi) dV      = - int (w * phi_t) dV
        int (w_x * phi) dV      = - int (w * phi_x) dV
        int (w_y * phi) dV      = - int (w * phi_y) dV
        int (laplacian(w)*phi) dV = int (w * (phi_xx + phi_yy)) dV
        int ((u*w_x + v*w_y)*phi) dV = - int (w * (u*phi_x + v*phi_y)) dV  (for div(u, v) = 0)
    Boundary terms vanish identically due to compact support!
    """

    def __init__(
        self,
        num_test_functions: int = 100,
        subdomain_scale_x: float = 0.25,
        subdomain_scale_y: float = 0.25,
        subdomain_scale_t: float = 0.30,
        poly_order: int = 4,
        threshold: float = 0.05,
        alpha: float = 1e-4,
        random_seed: int = 42,
    ):
        self.num_test_functions = int(num_test_functions)
        self.subdomain_scale_x = float(subdomain_scale_x)
        self.subdomain_scale_y = float(subdomain_scale_y)
        self.subdomain_scale_t = float(subdomain_scale_t)
        self.poly_order = int(poly_order)
        self.threshold = float(threshold)
        self.alpha = float(alpha)
        self.random_seed = int(random_seed)

    def _1d_compact_poly(
        self, coord: np.ndarray, center: float, radius: float
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute 1D compact polynomial test function and its 1st and 2nd derivatives.
        psi(z) = (1 - xi^2)^p for |xi| < 1, where xi = (z - center)/radius.
        """
        xi = (coord - center) / radius
        mask = np.abs(xi) < 1.0
        p = self.poly_order

        val = np.zeros_like(coord)
        d1 = np.zeros_like(coord)
        d2 = np.zeros_like(coord)

        idx = np.where(mask)[0]
        if len(idx) > 0:
            s = 1.0 - xi[idx] ** 2
            val[idx] = s**p
            d1[idx] = p * (s ** (p - 1)) * (-2.0 * xi[idx] / radius)
            if p >= 2:
                d2[idx] = (
                    p * (p - 1) * (s ** (p - 2)) * ((-2.0 * xi[idx] / radius) ** 2)
                    + p * (s ** (p - 1)) * (-2.0 / (radius**2))
                )

        return val, d1, d2, mask

    def build_test_functions(
        self, x: np.ndarray, y: np.ndarray, t: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Generate randomly placed 3D space-time compact test functions.
        """
        Lx = x[-1] - x[0]
        Ly = y[-1] - y[0]
        Lt = t[-1] - t[0]

        Rx = self.subdomain_scale_x * Lx
        Ry = self.subdomain_scale_y * Ly
        Rt = self.subdomain_scale_t * Lt

        # Ensure centers allow full compact support within domain boundaries
        x_min, x_max = x[0] + Rx, x[-1] - Rx
        y_min, y_max = y[0] + Ry, y[-1] - Ry
        t_min, t_max = t[0] + Rt, t[-1] - Rt

        if x_max <= x_min:
            x_min, x_max = x[0] + 0.1 * Lx, x[-1] - 0.1 * Lx
            Rx = 0.2 * Lx
        if y_max <= y_min:
            y_min, y_max = y[0] + 0.1 * Ly, y[-1] - 0.1 * Ly
            Ry = 0.2 * Ly
        if t_max <= t_min:
            t_min, t_max = t[0] + 0.1 * Lt, t[-1] - 0.1 * Lt
            Rt = 0.2 * Lt

        rng = np.random.RandomState(self.random_seed)
        xc_list = rng.uniform(x_min, x_max, self.num_test_functions)
        yc_list = rng.uniform(y_min, y_max, self.num_test_functions)
        tc_list = rng.uniform(t_min, t_max, self.num_test_functions)

        test_functions = []
        for k in range(self.num_test_functions):
            xc, yc, tc = xc_list[k], yc_list[k], tc_list[k]

            psi_x, psi_x_d1, psi_x_d2, mask_x = self._1d_compact_poly(x, xc, Rx)
            theta_y, theta_y_d1, theta_y_d2, mask_y = self._1d_compact_poly(y, yc, Ry)
            chi_t, chi_t_d1, _, mask_t = self._1d_compact_poly(t, tc, Rt)

            idx_x = np.where(mask_x)[0]
            idx_y = np.where(mask_y)[0]
            idx_t = np.where(mask_t)[0]

            if len(idx_x) == 0 or len(idx_y) == 0 or len(idx_t) == 0:
                continue

            # Subdomain slices for high performance quadrature
            # 3D tensor on subdomain: (Nt_sub, Nx_sub, Ny_sub)
            chi_sub = chi_t[idx_t, None, None]
            chi_t_sub = chi_t_d1[idx_t, None, None]

            psi_sub = psi_x[None, idx_x, None]
            psi_x_sub = psi_x_d1[None, idx_x, None]
            psi_xx_sub = psi_x_d2[None, idx_x, None]

            theta_sub = theta_y[None, None, idx_y]
            theta_y_sub = theta_y_d1[None, None, idx_y]
            theta_yy_sub = theta_y_d2[None, None, idx_y]

            phi = chi_sub * psi_sub * theta_sub
            phi_t = chi_t_sub * psi_sub * theta_sub
            phi_x = chi_sub * psi_x_sub * theta_sub
            phi_y = chi_sub * psi_sub * theta_y_sub
            phi_xx = chi_sub * psi_xx_sub * theta_sub
            phi_yy = chi_sub * psi_sub * theta_yy_sub
            phi_lap = phi_xx + phi_yy

            test_functions.append({
                "idx_t": idx_t,
                "idx_x": idx_x,
                "idx_y": idx_y,
                "phi": phi,
                "phi_t": phi_t,
                "phi_x": phi_x,
                "phi_y": phi_y,
                "phi_lap": phi_lap,
            })

        return test_functions

    def build_weak_form_system(
        self,
        field: SpatiotemporalField,
        target_channel: str,
        candidate_library: List[str],
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Assemble 2D spatiotemporal weak-form linear system G @ xi = b.
        Returns: (G, b) of shape (K, P) and (K,).
        """
        x = field.x
        y = field.y
        t = field.t
        dx = field.dx
        dy = field.dy
        dt = field.dt

        if field.spatial_dim != 2 or y is None:
            raise ValueError("build_weak_form_system requires 2D SpatiotemporalField with non-None y.")

        test_functions = self.build_test_functions(x, y, t)
        K = len(test_functions)
        if K < 10:
            raise ValueError(f"Too few valid test functions constructed ({K}). Check grid dimensions.")

        dV = dx * dy * dt
        b = np.zeros(K, dtype=np.float64)
        P = len(candidate_library)
        G = np.zeros((K, P), dtype=np.float64)

        # Pre-extract channel arrays
        channel_data: Dict[str, np.ndarray] = {}
        for cname in field.channel_names:
            channel_data[cname] = field.get_channel(cname)

        w_target = channel_data[target_channel]

        # Assemble weak-form system
        for k, tf in enumerate(test_functions):
            it = tf["idx_t"]
            ix = tf["idx_x"]
            iy = tf["idx_y"]

            # Subdomain view: shape (len(it), len(ix), len(iy))
            sub_w_target = w_target[np.ix_(it, ix, iy)]

            # Target b_k = - int (w * phi_t) dV
            b[k] = -float(np.sum(sub_w_target * tf["phi_t"]) * dV)

            # Evaluate each candidate operator in weak form
            for p, cand in enumerate(candidate_library):
                val_k = 0.0
                if cand == "1":
                    val_k = float(np.sum(tf["phi"]) * dV)
                elif cand in field.channel_names:
                    f_sub = channel_data[cand][np.ix_(it, ix, iy)]
                    val_k = float(np.sum(f_sub * tf["phi"]) * dV)
                elif cand.startswith("lap_"):
                    vname = cand[4:]
                    f_sub = channel_data[vname][np.ix_(it, ix, iy)]
                    val_k = float(np.sum(f_sub * tf["phi_lap"]) * dV)
                elif cand.startswith("d_") and cand.endswith("_x"):
                    vname = cand[2:-2]
                    f_sub = channel_data[vname][np.ix_(it, ix, iy)]
                    val_k = -float(np.sum(f_sub * tf["phi_x"]) * dV)
                elif cand.startswith("d_") and cand.endswith("_y"):
                    vname = cand[2:-2]
                    f_sub = channel_data[vname][np.ix_(it, ix, iy)]
                    val_k = -float(np.sum(f_sub * tf["phi_y"]) * dV)
                elif cand == "u*v^2":
                    u_sub = channel_data["u"][np.ix_(it, ix, iy)]
                    v_sub = channel_data["v"][np.ix_(it, ix, iy)]
                    val_k = float(np.sum(u_sub * (v_sub**2) * tf["phi"]) * dV)
                elif cand == "u^3":
                    u_sub = channel_data["u"][np.ix_(it, ix, iy)]
                    val_k = float(np.sum((u_sub**3) * tf["phi"]) * dV)
                elif cand == "advection_omega":
                    om_sub = channel_data["omega"][np.ix_(it, ix, iy)]
                    u_sub = channel_data["u"][np.ix_(it, ix, iy)]
                    v_sub = channel_data["v"][np.ix_(it, ix, iy)]
                    advec_integrand = om_sub * (u_sub * tf["phi_x"] + v_sub * tf["phi_y"])
                    val_k = -float(np.sum(advec_integrand) * dV)
                else:
                    val_k = 0.0

                G[k, p] = val_k

        return G, b

    def fit_channel(
        self,
        field: SpatiotemporalField,
        target_channel: str,
        candidate_library: List[str],
    ) -> PDEDiscoveryResult:
        """
        Discover governing PDE for a specific channel using WSINDy-2D.
        """
        import time

        t0 = time.time()
        G, b = self.build_weak_form_system(field, target_channel, candidate_library)
        K = len(b)

        # Solve sparse regression via STLSQ directly on (G, b)
        b_col = b.reshape(-1, 1)
        stlsq = STLSQ(threshold=self.threshold, alpha=self.alpha, max_iter=25, normalize_columns=True)
        opt_res = stlsq.fit(G, b_col)
        raw_coefs = np.squeeze(opt_res.coef)
        if raw_coefs.ndim == 0:
            raw_coefs = np.array([float(raw_coefs)])

        # Format results
        coef_dict = {}
        for p, cand in enumerate(candidate_library):
            if abs(raw_coefs[p]) > 1e-6:
                coef_dict[cand] = float(raw_coefs[p])

        eq_parts = [f"{coef_dict[c]:+.4f}*{c}" for c in coef_dict]
        eq_str = f"{target_channel}_t = " + (" ".join(eq_parts) if eq_parts else "0.0")

        # Residual
        b_norm = float(np.linalg.norm(b)) + 1e-12
        pred = G @ raw_coefs
        res_norm = float(np.linalg.norm(b - pred) / b_norm)
        duration = time.time() - t0

        return PDEDiscoveryResult(
            pde_name=f"{field.pde_name}_{target_channel}",
            discovered_equation=eq_str,
            feature_names=list(coef_dict.keys()),
            coefficients=coef_dict,
            residual_norm=res_norm,
            support_mask=[True] * len(coef_dict),
            num_evaluations=K,
            execution_time_seconds=duration,
            discovery_mode="wsindy_2d",
            metadata={
                "target_channel": target_channel,
                "num_test_functions": K,
                "subdomain_scale": (self.subdomain_scale_x, self.subdomain_scale_y, self.subdomain_scale_t),
            },
        )
