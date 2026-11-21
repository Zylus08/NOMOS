# NOMOS: Neural & Symbolic Discovery of Physical Laws

**Milestone 1 (M1) — Scientific Discovery Foundation**  
**Principal Investigator / Author:** Saksham Mishra <mishrasaksham080705@gmail.com>

---

## Overview

Project **NOMOS** recovers interpretable governing dynamical laws $\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x}, \mathbf{u}, \boldsymbol{\mu})$ directly from observational trajectories without prior knowledge of the true equations or parameters.

M1 establishes an audited, deterministic, and independently validated foundation:
1. **Mathematical Identifiability & Theory**: Precise condition bounds for sparse recovery on candidate feature bases.
2. **Deterministic Numerical Physics**: 5 canonical dynamical systems (Harmonic Oscillator, Damped Oscillator, Nonlinear Pendulum, Lotka-Volterra, Lorenz-63) with analytical and symplectic invariants.
3. **Data Integrity & Isolation**: Strict trajectory-disjoint splitting, cryptographic SHA-256 integrity hashing, and total isolation between learner and true generative equations.
4. **Original Sparse Discovery Algorithms**: Custom-built Sequentially Thresholded Least Squares (STLSQ), active-set refitting, ridge regularization, polynomial & trigonometric feature libraries, and adaptive differentiators.
5. **Symbolic Mathematics & Simplification**: Conversion to analytical SymPy expressions, algebraic equivalence verification, and complexity measures.
6. **Multi-Seed Benchmarking & Baselines**: Rigorous comparison against standard Ordinary Least Squares (OLS) and PySINDy across noise regimes ($0\%, 1\%, 5\%, 10\%$).
7. **Adversarial Red-Team Audits & Falsification**: Testing for data leakage, collinearity breakdown, and false positives.

## Installation

```bash
git clone <repo-url>
cd NOMOS
pip install -e .
```

## Running Benchmarks & Tests

```bash
# Run all unit and scientific verification tests
python tests/run_all_tests.py

# Run full M1 scientific benchmark matrix
python experiments/run_m1_benchmarks.py
```
