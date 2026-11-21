"""
NOMOS High-Precision Numerical Solvers & Convergence Verification
Roles A04, B07, B08, B09
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Any
import numpy as np
from scipy.integrate import solve_ivp
from nomos.core.system import DynamicalSystem


@dataclass
class SimulationResult:
    """Outcome of numerical trajectory integration."""
    t: np.ndarray            # Shape: (M,)
    x: np.ndarray            # Shape: (M, n)
    x_dot_true: np.ndarray   # Shape: (M, n) exact true derivative at each state
    energy_drift: Optional[float]
    solver_name: str
    success: bool
    message: str


def simulate_system(
    system: DynamicalSystem,
    x0: np.ndarray,
    t_span: Tuple[float, float],
    t_eval: Optional[np.ndarray] = None,
    method: str = "DOP853",
    rtol: float = 1e-10,
    atol: float = 1e-10,
    max_step: float = 0.05,
) -> SimulationResult:
    """
    Simulate dynamical system using adaptive high-precision SciPy solver.
    Computes true analytical/RHS derivatives at each simulated point.
    """
    x0 = np.asarray(x0, dtype=np.float64)

    def fun(t, y):
        return system.rhs(t, y)

    sol = solve_ivp(
        fun,
        t_span=t_span,
        y0=x0,
        t_eval=t_eval,
        method=method,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )

    if not sol.success:
        return SimulationResult(
            t=sol.t if hasattr(sol, "t") else np.array([]),
            x=sol.y.T if hasattr(sol, "y") else np.array([[]]),
            x_dot_true=np.array([[]]),
            energy_drift=None,
            solver_name=method,
            success=False,
            message=sol.message,
        )

    t_arr = sol.t
    x_traj = sol.y.T  # Shape (M, n)

    # Compute true derivative exactly from ground-truth RHS
    x_dot_true = np.zeros_like(x_traj)
    for i in range(len(t_arr)):
        x_dot_true[i] = system.rhs(t_arr[i], x_traj[i])

    # Conserved quantity drift
    energy_drift = None
    if hasattr(system, "compute_energy_drift"):
        energy_drift = system.compute_energy_drift(x_traj)
    elif system.conserved_quantity(x0) is not None:
        energies = np.array([system.conserved_quantity(pt) for pt in x_traj])
        e0 = energies[0]
        energy_drift = float(np.max(np.abs(energies - e0)) / (abs(e0) + 1e-12))

    return SimulationResult(
        t=t_arr,
        x=x_traj,
        x_dot_true=x_dot_true,
        energy_drift=energy_drift,
        solver_name=method,
        success=True,
        message=sol.message,
    )


def solver_convergence_study(
    system: DynamicalSystem,
    x0: np.ndarray,
    t_span: Tuple[float, float],
    t_eval: np.ndarray,
    tolerances: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Execute solver tolerance convergence sweeps (B08).
    Evaluates relative error against reference DOP853 integration at 1e-13.
    """
    if tolerances is None:
        tolerances = [1e-4, 1e-6, 1e-8, 1e-10, 1e-12]

    # Reference solution at ultra-tight tolerance
    ref_res = simulate_system(
        system, x0, t_span, t_eval=t_eval, method="DOP853", rtol=1e-13, atol=1e-13
    )
    if not ref_res.success:
        raise RuntimeError("Reference integration failed")

    results = []
    for tol in tolerances:
        res = simulate_system(
            system, x0, t_span, t_eval=t_eval, method="RK45", rtol=tol, atol=tol
        )
        if res.success:
            err = np.max(np.abs(res.x - ref_res.x))
            rel_err = err / (np.max(np.abs(ref_res.x)) + 1e-12)
            results.append({
                "tolerance": tol,
                "max_absolute_error": float(err),
                "relative_error": float(rel_err),
                "energy_drift": res.energy_drift,
            })

    return {
        "system": system.metadata.name,
        "sweeps": results,
    }
