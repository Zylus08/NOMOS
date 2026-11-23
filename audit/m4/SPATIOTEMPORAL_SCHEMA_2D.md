# Project NOMOS — Milestone M4
## 2D & Multichannel Spatiotemporal Field Schema & Isolation Audit

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 2 Specification  
**Date:** 2026-11-23  

---

### 1. Architectural Overview

Milestone M4 expands Project NOMOS from 1D scalar fields to genuine 2D multichannel spatiotemporal PDE systems.
The field schema is generalized in `nomos/pde/schema.py` through two core classes:
- `Grid2D`: 2D spatial discretization over $(x, y) \in [x_{\min}, x_{\max}] \times [y_{\min}, y_{\max}]$ with $N_x \times N_y$ nodes, supporting periodic and non-periodic topologies and meshgrid representations.
- `SpatiotemporalField`: Generalized data structure representing fields of dimension $(M, N_x, N_y)$ or $(M, N_x, N_y, C)$, where $M$ is the number of time integration steps and $C$ is the number of coupled physical channels (e.g., $(u, v)$ for reaction-diffusion, $(\omega, u, v)$ for Navier–Stokes).

---

### 2. Schema Specification & Shape Invariants

| Attribute | 1D Single Channel | 1D Multi-Channel | 2D Single Channel | 2D Multi-Channel |
| :--- | :--- | :--- | :--- | :--- |
| `spatial_dim` | 1 | 1 | 2 | 2 |
| `x` coordinate | $(N_x,)$ | $(N_x,)$ | $(N_x,)$ | $(N_x,)$ |
| `y` coordinate | `None` | `None` | $(N_y,)$ | $(N_y,)$ |
| `t` coordinate | $(M,)$ | $(M,)$ | $(M,)$ | $(M,)$ |
| `u` array | $(M, N_x)$ | $(M, N_x, C)$ | $(M, N_x, N_y)$ | $(M, N_x, N_y, C)$ |
| `channel_names` | `['u']` | `['u', 'v', ...]` | `['u']` | `['u', 'v', ...]` |
| `dx`, `dy`, `dt` | $dx, 0.0, dt$ | $dx, 0.0, dt$ | $dx, dy, dt$ | $dx, dy, dt$ |
| SHA-256 Hash | $H(pde, x, t, u)$ | $H(pde, x, t, u)$ | $H(pde, x, y, t, u)$ | $H(pde, x, y, t, u)$ |

---

### 3. Evaluator Isolation Sandbox (`nomos/pde/isolation.py`)

To prevent data leakage during scientific discovery, the evaluator sandbox strictly filters:
- `u_clean`: Purged (`None`). The learner only accesses noisy measurements `u`.
- `u_t_true`: Purged (`None`). True analytical time derivatives are unavailable to learners.
- `true_parameters`: Purged (`None`). Ground truth simulation constants ($D_u, D_v, \nu, F, k$) are withheld.
- Cryptographic provenance tracking: Marked with `isolated: True` and linked back to source dataset hashes.
