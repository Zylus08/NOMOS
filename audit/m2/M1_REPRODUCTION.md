# M2 PHASE 0 — M1 EXPERIMENTAL REPRODUCTION AUDIT
**Orchestrator:** Chief Scientific Orchestrator  
**Investigator:** Saksham Mishra <mishrasaksham080705@gmail.com>  
**Status:** FULL REPRODUCTION VERIFIED

---

## 1. Automated Test Suite Reproduction

Command executed:
```bash
python -m pytest -v tests
```
**Outcome:**
```text
============================= 33 passed in 7.37s ==============================
```

All 33 unit, integration, and adversarial tests passed without failure or regressions:
- `tests/test_physics.py`: 6 tests passed (Registry completeness, Analytical solutions, Symplectic invariant drifts, Tolerance sweeps).
- `tests/test_data.py`: 5 tests passed (Disjoint splitting, Sandbox metadata stripping, Gaussian noise injection, Quality audit).
- `tests/test_library.py`: 5 tests passed (4th-order FD, Savitzky-Golay filtering, Polynomial basis, Trigonometric basis, Feature scaler unscaling).
- `tests/test_sparse.py`: 3 tests passed (STLSQ sparse recovery, Rank-deficient collinear handling, Overly high threshold).
- `tests/test_symbolic.py`: 5 tests passed (Matrix to SymPy conversion, Exact equivalence, Factored equivalence, Complexity monotonicity, Dimensional checking).
- `tests/test_pipeline.py`: 5 tests passed (End-to-end recovery across all 5 benchmark systems).
- `tests/test_baselines.py`: 2 tests passed (OLS dense baseline, PySINDy 2.1.0 parity).
- `tests/test_adversarial.py`: 3 tests passed (Harmonic collinearity degeneracy, Inadequate candidate library falsification, Leaky dataset attack).

---

## 2. Representative Equation Recovery Reproduction

End-to-end recovery was re-verified via the NOMOS CLI on held-out simulated trajectories:

```bash
nomos discover --system harmonic_oscillator
# Result: dx/dt = 1.0*v, dv/dt = -1.0*x  (Exact match)

nomos discover --system lotka_volterra --threshold 0.05
# Result: dx/dt = 1.5*x - 1.0*x*y, dy/dt = 1.0*x*y - 3.0*y  (Exact match)

nomos discover --system nonlinear_pendulum --threshold 0.05
# Result: dtheta/dt = 1.0*omega, domega/dt = -9.81*sin(theta)  (Exact match)
```

M1 reproduction is complete and robust. Repository is cleared to begin Milestone M2 development.
