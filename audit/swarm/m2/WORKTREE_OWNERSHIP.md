# NOMOS Milestone M2 — Specialist Role Allocation & Worktree File Ownership

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Chief Research Orchestrator:** NOMOS Swarm Control Plane  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Total Specialist Pool:** 100 Specialist Roles across Divisions A–J  

---

## 1. Division Allocation Overview

| Division | Domain | Roles | Focus Area |
| :--- | :--- | :---: | :--- |
| **Division A** | Scientific Theory & Mathematical Foundations | A01–A08 (8) | Symbolic identifiability, AST theory, dimensional analysis, epistemic uncertainty |
| **Division B** | Dynamical Systems & Simulators | B01–B12 (12) | 10 benchmark dynamical systems, high-precision DOP853 numerical solvers |
| **Division C** | Data Integrity & Experimental Design | C01–C12 (12) | Trajectory datasets, metadata sandboxing, anti-leakage guards, SHA-256 hashing |
| **Division D** | Symbolic & Neural Discovery Algorithms | D01–D16 (16) | Typed expression trees, beam search, GP, PyTorch neural dynamics surrogate |
| **Division E** | Symbolic Algebra & Simplification | E01–E10 (10) | SymPy bi-directional parsing, domain protections, algebraic equivalence |
| **Division F** | Baselines & Empirical Evaluation | F01–F12 (12) | M1 SINDy comparisons, 60 benchmark evaluations, rollout simulations |
| **Division G** | Red-Team & Adversarial Testing | G01–G10 (10) | Identifiability tests, noise degradation, manifold degeneracy, edge cases |
| **Division H** | Infrastructure, Concurrency & Profiling | H01–H08 (8) | Resource throttling, BLAS/OpenMP single-threading, telemetry, reproducibility |
| **Division I** | Independent Peer Review | I01–I06 (6) | Independent code auditing, mathematical derivation review, acceptance sign-offs |
| **Division J** | Integration & Scientific Certification | J01–J06 (6) | Control plane orchestration, milestone delivery, Five-Gate final certification |

---

## 2. Exclusive File Ownership Mapping

To prevent race conditions, merge conflicts, and accidental regressions, file ownership was strictly partitioned across specialist roles:

| Module / Artifact | Primary Owner | Reviewer / Auditor | Status |
| :--- | :---: | :---: | :---: |
| `nomos/symbolic/primitives.py` | Agent D01 | Agent E07 | **INTEGRATED** |
| `nomos/symbolic/trees.py` | Agent D02 | Agent E01 | **INTEGRATED** |
| `nomos/search/optimizer.py` | Agent D04 | Agent D06 | **INTEGRATED** |
| `nomos/search/pareto.py` | Agent D05 | Agent J02 | **INTEGRATED** |
| `nomos/search/beam.py` | Agent D12 | Agent D14 | **INTEGRATED** |
| `nomos/search/genetic.py` | Agent D13 | Agent D02 | **INTEGRATED** |
| `nomos/neural/surrogate.py` | Agent D07 | Agent D08 | **INTEGRATED** |
| `nomos/neural/trainer.py` | Agent D08 | Agent H03 | **INTEGRATED** |
| `nomos/neural/guidance.py` | Agent D09 | Agent D10 | **INTEGRATED** |
| `nomos/search/hybrid.py` | Agent D11 | Agent D15 | **INTEGRATED** |
| `nomos/pipeline/m2_pipeline.py` | Agent D15 | Agent J01 | **INTEGRATED** |
| `nomos/physics/benchmarks_m2.py` | Agent B11 | Agent B12 | **INTEGRATED** |
| `nomos/physics/duffing.py` | Agent B07 | Agent B08 | **INTEGRATED** |
| `nomos/physics/vanderpol.py` | Agent B09 | Agent B10 | **INTEGRATED** |
| `nomos/physics/damped_pendulum.py`| Agent B04 | Agent B05 | **INTEGRATED** |
| `nomos/physics/rational_system.py` | Agent B06 | Agent A03 | **INTEGRATED** |
| `nomos/physics/roessler.py` | Agent B10 | Agent B12 | **INTEGRATED** |
| `nomos/evaluation/identifiability.py`| Agent A07 | Agent G06 | **INTEGRATED** |
| `nomos/evaluation/rollout_m2.py` | Agent F02 | Agent F03 | **INTEGRATED** |
| `experiments/m2/run_m2_benchmarks.py`| Agent F05 | Agent F11 | **INTEGRATED** |
| `audit/m2/*` | Division A & F | Division I | **INTEGRATED** |
| `audit/swarm/m2/*` | Division J | Division I | **INTEGRATED** |
