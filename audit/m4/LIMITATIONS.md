# Project NOMOS — Milestone M4
## Limitations, Boundary Conditions & Known Failure Modes

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 13 Forensic Limitations Audit  
**Date:** 2026-11-23  

---

### 1. High-Order Chaotic PDEs (Kuramoto–Sivashinsky)

While the M4 scale-adaptive search successfully identifies Kuramoto–Sivashinsky ($u_t = -u u_x - u_{xx} - u_{xxxx}$) under multi-harmonic initial conditions, exact recovery rate across the aggregate noise matrix was $0.0\%$.
- **Root Cause:** The 4th spatial derivative $\partial_{xxxx} u$ possesses Fourier symbol $k^4$. At $N=128$, high wavenumber modes amplify measurement noise by $k^4 \sim (64)^4 \approx 1.6 \times 10^7$.
- **Mitigation:** Requires spectral cutoff filtering or higher-order polynomial weak-form test functions ($p \ge 6$) on finer grids ($N \ge 256$).

---

### 2. Physical Collinearity & Solitary Wave Invariants

- **Single Traveling Wave Degeneracy:** As proved in `audit/m4/NONLINEAR_SEARCH_FAILURE.md`, observing a single solitary wave $\phi(x - ct)$ identically satisfies the traveling wave equation $\partial_t u = -c \partial_x u$.
- **SINDy Degradation:** Without active multi-soliton or multi-frequency excitation, discovery engines collapse KdV to linear advection. Active Identifiability (`nomos/pde/active_identifiability.py`) is required to break this degeneracy.

---

### 3. Boundary Condition Assumptions

- Current 2D Navier–Stokes and Reaction–Diffusion simulators assume periodic toroidal topology $\mathbb{T}^2$.
- Non-periodic physical domains (no-slip walls, inflow/outflow boundaries) require non-periodic boundary integration-by-parts corrections where boundary terms $\oint_{\partial \Omega} (\mathbf{n} \cdot \mathbf{J}) dS$ must be retained or eliminated using Dirichlet-zero test stencils.

---

### 4. Neural Dynamics Surrogate Scalability

- The 1D Conv surrogate proved ineffective for equation discovery guidance, adding $18\times$ compute overhead with 0% recovery gain.
- Scaling neural guidance to 2D spatiotemporal dynamics will require physics-informed Fourier Neural Operators (FNO) or Neural ODEs trained over diverse initial condition distributions rather than single-trajectory ConvNets.
