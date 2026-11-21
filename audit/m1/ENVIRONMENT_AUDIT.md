# M1 ENVIRONMENT AUDIT & HARDWARE PROFILE
**Agent Role:** H03 — Reproducible Environment Management  
**Timestamp:** 2026-11-21T23:25:00+05:30  
**Investigator:** Saksham Mishra <mishrasaksham080705@gmail.com>

---

## 1. Host Hardware Specifications

| Component | Value | Notes |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Pro (10.0.26300-SP0) | 64-bit Architecture |
| **Physical CPU Cores** | 10 | Hybrid Core Architecture |
| **Logical Threads** | 16 | Hyperthreaded / Multi-core |
| **Installed RAM** | 15.68 GB (~16.0 GB) | Virtual memory active |
| **Available RAM** | ~9.2 GB | Pre-execution baseline |
| **Working Directory** | `E:\NOMOS` | Local Dedicated NVMe / SSD |

---

## 2. Python Runtime & Core Toolchain

| Dependency | Version | Role in NOMOS M1 | Status |
| :--- | :--- | :--- | :--- |
| **Python** | 3.12.8 | Primary Runtime | Verified |
| **NumPy** | 1.26.4 | Numerical arrays & linear algebra | Verified |
| **SciPy** | 1.13.1 | High-precision ODE solvers (`solve_ivp`), B-splines, stats | Verified |
| **SymPy** | 1.14.0 | Computer Algebra System & symbolic equivalence | Verified |
| **PySINDy** | 2.1.0 | Independent reference baseline (external comparison) | Verified |
| **Pytest** | 9.0.3 | Automated testing & verification framework | Verified |
| **Matplotlib** | 3.9.2 | Scientific visualization & phase portrait generation | Verified |

---

## 3. Resource Allocation & Concurrency Caps

To prevent CPU oversubscription and memory thrashing on this 10-core / 16 GB workstation:
- **Numerical Simulation Cap:** Maximum 4 concurrent ODE solver threads.
- **Symbolic Computation Cap:** Maximum 2 concurrent algebraic simplification jobs.
- **Discovery Pipeline Jobs:** Single-process bounded execution per system with BLAS/OpenMP capped (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`).
- **Memory Ceiling:** Memory limit capped at 12 GB.
