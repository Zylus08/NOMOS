# SWARM WORKTREE & FILE OWNERSHIP DIRECTIVE
**Agent Role:** H08 — Repository Hygiene & Dependency Audit  
**Integration Overseer:** J01 / J03  
**Status:** FROZEN & ENFORCED

---

## 1. Architectural File Ownership Rules

To prevent merge collisions, uncontrolled overwrites, and state corruption:
1. **Interface Immutability:** Core contracts in `nomos/core/` are defined first and frozen. Any change requires J01/J02 sign-off.
2. **Exclusive File Ownership:** Every file in the repository has a primary owner role and designated reviewer.
3. **No Uncontrolled Edits:** Roles may only commit to their assigned files.
4. **Integration Gate:** Only Division J (Integration) merges into canonical `main`.

---

## 2. File Ownership Table

| Module / Path | Primary Owner | Reviewer | Division | Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| `nomos/core/system.py` | A01 | J02 | A | Dynamical system interface & identifiability contracts |
| `nomos/core/library.py` | A02 | D10 | A/D | Feature library abstract base class |
| `nomos/core/optimizer.py` | A02 | D01 | A/D | Sparse regression optimizer base class |
| `nomos/core/symbolic.py` | A03 | E01 | A/E | Symbolic equation interfaces |
| `nomos/physics/base.py` | B10 | B07 | B | Base physics simulator & invariant tracker |
| `nomos/physics/harmonic_oscillator.py` | B01 | B07 | B | Linear harmonic oscillator simulator |
| `nomos/physics/damped_oscillator.py` | B02 | B07 | B | Damped harmonic oscillator simulator |
| `nomos/physics/pendulum.py` | B03, B04 | B07 | B | Simple nonlinear pendulum simulator |
| `nomos/physics/lotka_volterra.py` | B05 | B09 | B | Lotka-Volterra predator-prey simulator |
| `nomos/physics/lorenz63.py` | B06 | A05 | B | Lorenz-63 chaotic attractor simulator |
| `nomos/physics/solvers.py` | A04, B07, B08 | I02 | B | Solver tolerances & convergence studies |
| `nomos/physics/benchmarks.py` | B11, B12 | I03 | B | Unified benchmark suite factory |
| `nomos/data/schema.py` | C01, C08, C10 | C12 | C | Trajectory dataset schema & SHA-256 integrity |
| `nomos/data/sampling.py` | C02, C03 | I03 | C | Initial condition & parameter regime sampling |
| `nomos/data/splits.py` | C04 | I04 | C | Trajectory-disjoint splitting |
| `nomos/data/corruption.py` | C05, C06, C07 | G07 | C | Noise injection & irregular sampling |
| `nomos/data/isolation.py` | C09 | I04 | C | Metadata sandboxing & blind discovery wrapper |
| `nomos/data/audit.py` | C11, C12 | G04 | C | Leakage detection & dataset audit |
| `nomos/differentiation/finite_difference.py` | D11 | I02 | D | High-order finite difference differentiators |
| `nomos/differentiation/savitzky_golay.py` | D12 | I02 | D | Savitzky-Golay filtering differentiator |
| `nomos/differentiation/spline.py` | D13 | I02 | D | Smoothing cubic spline differentiator |
| `nomos/differentiation/diagnostics.py` | D14 | G07 | D | Derivative error estimation & spectra |
| `nomos/library/polynomial.py` | D08 | G05 | D | Polynomial candidate basis generator |
| `nomos/library/trigonometric.py` | D09 | G05 | D | Trigonometric harmonic basis generator |
| `nomos/library/custom.py` | D10 | G05 | D | Composite candidate library builder |
| `nomos/library/scaling.py` | D04 | I01 | D | Feature normalization & exact unscaling |
| `nomos/sparse/stlsq.py` | D01, D07 | I01 | D | Sequentially Thresholded Least Squares engine |
| `nomos/sparse/active_set.py` | D02 | I01 | D | Sparse active set refitting |
| `nomos/sparse/threshold.py` | D03 | I05 | D | AIC/BIC automated threshold selector |
| `nomos/sparse/ridge.py` | D05, D06 | I01 | D | SVD / Ridge regularized least squares |
| `nomos/symbolic/representation.py` | E01, E09 | I01 | E | Symbolic equation schema & serializer |
| `nomos/symbolic/sympy_converter.py` | E02 | E10 | E | Matrix-to-SymPy analytical converter |
| `nomos/symbolic/simplification.py` | E03, E04 | I01 | E | Rational algebraic pruning & LaTeX export |
| `nomos/symbolic/comparison.py` | E05, E06, E10 | I01 | E | Structural and algebraic equivalence tests |
| `nomos/symbolic/complexity.py` | E07 | I06 | E | Kolmogorov tree complexity measures |
| `nomos/symbolic/dimensional.py` | A06, E08 | I01 | E | Physical dimensional analysis checker |
| `nomos/evaluation/metrics.py` | F01, F06, F07, F08 | I05 | F | Trajectory, derivative & attractor metrics |
| `nomos/evaluation/rollout.py` | F02, F03 | I02 | F | Closed-loop simulation of discovered laws |
| `nomos/evaluation/support.py` | F04 | I05 | F | Sparsity pattern Precision / Recall / F1 |
| `nomos/evaluation/coefficients.py` | F05 | I05 | F | Parameter relative error & Frobenius norm |
| `nomos/evaluation/baselines.py` | F09, F10 | I05 | F | OLS baseline & PySINDy reference adapter |
| `nomos/evaluation/aggregation.py` | F11, F12 | I05 | F | Multi-seed statistical aggregator |
| `nomos/pipeline/discovery.py` | D16 | J01 | D/J | Unified DiscoveryEngine pipeline |
| `nomos/pipeline/config.py` | D15 | J02 | D | Experiment configuration schema |
| `nomos/utils/logging.py` | H04 | J01 | H | Structured JSON / stream logger |
| `nomos/utils/manifest.py` | H05 | J05 | H | Experiment manifest & hardware logger |
| `nomos/utils/parallel.py` | H06 | J04 | H | Resource-bounded process execution pool |
| `nomos/cli.py` | H02 | J01 | H | Command Line Interface entry point |
| `tests/*` | G01–G10, H07 | J04 | G | Verification, unit & adversarial test suites |
| `audit/*` | All Specialist Roles | J05, J06 | All | Formal milestone audit & evidence |
