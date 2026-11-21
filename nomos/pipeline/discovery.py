"""
NOMOS End-to-End Discovery Pipeline Engine
Agent D16 & J01
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import sympy as sp

from nomos.core.library import BaseFeatureLibrary
from nomos.core.symbolic import DiscoveredEquation, DiscoveredSystem
from nomos.data.schema import TrajectoryDataset
from nomos.data.isolation import IsolatedLearnerDataset
from nomos.differentiation import finite_difference, savitzky_golay_derivative, spline_derivative
from nomos.library import PolynomialLibrary, TrigonometricLibrary, CompositeLibrary, FeatureScaler
from nomos.sparse import STLSQ
from nomos.symbolic.sympy_converter import matrix_to_sympy_system
from nomos.symbolic.simplification import simplify_and_format_equation
from nomos.symbolic.complexity import compute_equation_complexity
from nomos.pipeline.config import DiscoveryConfig


@dataclass
class DiscoveryOutput:
    """Complete results from DiscoveryEngine fitting."""
    coef: np.ndarray                 # (P, n) learned sparse coefficient matrix
    feature_names: List[str]         # Candidate library column names
    variable_names: List[str]        # State variables
    library: BaseFeatureLibrary      # Fitted library instance
    discovered_system: DiscoveredSystem
    iterations: int
    converged: bool
    residual_norm: float
    X_stacked: np.ndarray
    X_dot_estimated: np.ndarray
    config: DiscoveryConfig


class DiscoveryEngine:
    """
    Unified NOMOS scientific discovery pipeline.
    Connects:
    1. Numerical differentiation on raw trajectories
    2. Candidate feature basis expansion Theta(X)
    3. Normalization and Sequentially Thresholded Least Squares (STLSQ)
    4. Active set refitting
    5. Conversion to analytical SymPy symbolic equations
    6. Simplification and complexity estimation
    """

    def __init__(self, config: Optional[DiscoveryConfig] = None):
        self.config = config or DiscoveryConfig()
        self.output_: Optional[DiscoveryOutput] = None

    def fit(self, dataset: Any) -> DiscoveryOutput:
        """
        Fit model on TrajectoryDataset or IsolatedLearnerDataset.
        Protects against data leakage.
        """
        # Ensure learner only accesses safe trajectory data
        if not isinstance(dataset, (TrajectoryDataset, IsolatedLearnerDataset)):
            raise TypeError("Dataset must be TrajectoryDataset or IsolatedLearnerDataset")

        trajectories = dataset.trajectories
        var_names = list(dataset.variable_names)
        n_vars = len(var_names)

        # 1. Differentiate each trajectory independently to prevent boundary discontinuities across runs
        x_stacked_list = []
        x_dot_list = []

        for traj in trajectories:
            t = traj.t
            x = traj.x

            if self.config.diff_method == "finite_difference":
                x_dot = finite_difference(t, x, order=self.config.diff_order)
            elif self.config.diff_method == "savitzky_golay":
                x_dot = savitzky_golay_derivative(
                    t, x,
                    window_length=self.config.savgol_window,
                    polyorder=self.config.savgol_poly
                )
            elif self.config.diff_method == "spline":
                x_dot = spline_derivative(t, x, s=self.config.spline_s)
            else:
                raise ValueError(f"Unknown diff_method: {self.config.diff_method}")

            x_stacked_list.append(x)
            x_dot_list.append(x_dot)

        X_all = np.concatenate(x_stacked_list, axis=0)
        X_dot_all = np.concatenate(x_dot_list, axis=0)

        # 2. Build feature library
        if self.config.library_type == "polynomial":
            library = PolynomialLibrary(
                degree=self.config.poly_degree,
                include_bias=self.config.include_bias
            )
        elif self.config.library_type == "trigonometric":
            library = TrigonometricLibrary(harmonics=self.config.trig_harmonics)
        elif self.config.library_type == "composite":
            poly_lib = PolynomialLibrary(degree=self.config.poly_degree, include_bias=self.config.include_bias)
            trig_lib = TrigonometricLibrary(harmonics=self.config.trig_harmonics)
            library = CompositeLibrary([poly_lib, trig_lib])
        else:
            raise ValueError(f"Unknown library_type: {self.config.library_type}")

        Theta = library.fit_transform(X_all, variable_names=var_names)
        feat_names = library.get_feature_names()

        # 3. Fit sparse optimizer (STLSQ)
        optimizer = STLSQ(
            threshold=self.config.threshold,
            alpha=self.config.alpha,
            max_iter=self.config.max_iter,
            normalize_columns=self.config.normalize_columns,
            refit_active_set=self.config.refit_active_set,
        )
        opt_res = optimizer.fit(Theta, X_dot_all)
        Xi = opt_res.coef

        # 4. Convert learned coefficients to SymPy analytical expressions
        raw_sympy = matrix_to_sympy_system(Xi, feat_names, var_names)

        # 5. Simplify and create DiscoveredEquations
        equations: Dict[str, DiscoveredEquation] = {}
        total_complexity = 0.0

        for col, vname in enumerate(var_names):
            raw_expr = raw_sympy[vname]
            simp_expr, latex_str, read_str = simplify_and_format_equation(raw_expr)
            comp_score = compute_equation_complexity(simp_expr)
            total_complexity += comp_score

            active_mask = opt_res.support[:, col]
            active_fnames = [feat_names[idx] for idx in np.where(active_mask)[0]]
            active_coeffs = {
                feat_names[idx]: float(Xi[idx, col])
                for idx in np.where(active_mask)[0]
            }

            eq = DiscoveredEquation(
                variable_name=vname,
                sympy_expr=simp_expr,
                latex_str=latex_str,
                raw_str=read_str,
                active_features=active_fnames,
                coefficients=active_coeffs,
                complexity_score=comp_score,
            )
            equations[vname] = eq

        discovered_sys = DiscoveredSystem(
            equations=equations,
            system_name=getattr(dataset, "system_name", "unknown_system"),
            state_names=var_names,
            total_complexity=total_complexity,
            metadata=opt_res.metadata,
        )

        self.output_ = DiscoveryOutput(
            coef=Xi,
            feature_names=feat_names,
            variable_names=var_names,
            library=library,
            discovered_system=discovered_sys,
            iterations=opt_res.iterations,
            converged=opt_res.converged,
            residual_norm=opt_res.residual_norm,
            X_stacked=X_all,
            X_dot_estimated=X_dot_all,
            config=self.config,
        )
        return self.output_
