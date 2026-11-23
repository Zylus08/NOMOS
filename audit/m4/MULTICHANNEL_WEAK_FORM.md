# Project NOMOS — Milestone M4
## 2D Multichannel Weak-Form PDE Identification (WSINDy-2D) Audit

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 5 Architecture & Empirical Verification  
**Date:** 2026-11-23  

---

### 1. Executive Summary

Milestone M4 develops and validates the **2D Multichannel Weak-Form Sparse Identification of Nonlinear Dynamics (WSINDy-2D)** engine (`nomos/pde/weak_form_2d.py`).
By projecting governing PDEs onto compact, smooth space-time test functions and applying multi-dimensional integration by parts, spatial and temporal derivatives are transferred entirely from noisy measured data onto analytically known test functions.
Boundary terms vanish identically across all compact subdomains, completely removing the requirement for numerical differentiation filters.

---

### 2. Mathematical Integration-by-Parts Identities in 2D

Let $\Omega_k = [x_c - R_x, x_c + R_x] \times [y_c - R_y, y_c + R_y] \times [t_c - R_t, t_c + R_t]$ be a compact space-time test subdomain.
Test function $\phi(x, y, t) = \psi(x)\theta(y)\chi(t)$ vanishes with its derivatives on $\partial \Omega_k$.

| Physical Term | Differential Form | Weak-Form Integral (Zero Boundary Terms) |
| :--- | :--- | :--- |
| **Temporal Rate** | $\partial_t w$ | $b_k = -\int_{\Omega_k} w \frac{\partial \phi}{\partial t} \, dx dy dt$ |
| **Directional Gradient** | $\partial_x w$ | $-\int_{\Omega_k} w \frac{\partial \phi}{\partial x} \, dx dy dt$ |
| **Directional Gradient** | $\partial_y w$ | $-\int_{\Omega_k} w \frac{\partial \phi}{\partial y} \, dx dy dt$ |
| **Laplacian Diffusion** | $\nabla^2 w = \partial_{xx} w + \partial_{yy} w$ | $\int_{\Omega_k} w \left( \frac{\partial^2 \phi}{\partial x^2} + \frac{\partial^2 \phi}{\partial y^2} \right) dx dy dt$ |
| **Incompressible Advection** | $\mathbf{u} \cdot \nabla \omega$ ($\nabla \cdot \mathbf{u} = 0$) | $-\int_{\Omega_k} \omega \left( u \frac{\partial \phi}{\partial x} + v \frac{\partial \phi}{\partial y} \right) dx dy dt$ |
| **Coupled Reaction** | $u v^2$ | $\int_{\Omega_k} (u v^2) \phi \, dx dy dt$ |
| **Coupled Excitation** | $u - u^3 - v$ | $\int_{\Omega_k} u \phi \, dx dy dt - \int_{\Omega_k} u^3 \phi \, dx dy dt - \int_{\Omega_k} v \phi \, dx dy dt$ |

---

### 3. Empirical Verification Results

#### Benchmark 1: FitzHugh–Nagumo Activator ($u_t = \nabla^2 u + u - u^3 - v$, 1% noise)
- **Target Channel:** $u$
- **Discovered Equation:**
  $$u_t = +1.0002 \nabla^2 u + 0.9945 u - 0.9937 u^3 - 0.9988 v$$
- **Coefficient Error:**
  - $D_u = 1.0 \to 1.0002$ ($+0.02\%$ error)
  - Linear $u = 1.0 \to 0.9945$ ($-0.55\%$ error)
  - Cubic $u^3 = -1.0 \to -0.9937$ ($-0.63\%$ error)
  - Coupling $v = -1.0 \to -0.9988$ ($-0.12\%$ error)
- **Support Recovery:** $4/4$ true terms isolated, $0$ false positives, **Exact Support F1 = 1.000**.

#### Benchmark 2: Gray–Scott Inhibitor ($v_t = D_v \nabla^2 v + u v^2 - (F+k)v$, 2% noise)
- **Target Channel:** $v$ ($D_v = 0.08, F+k = 0.095$)
- **Discovered Equation:**
  $$v_t = +0.0792 \nabla^2 v + 0.8062 u v^2 - 0.0880 v$$
- **Coefficient Accuracy:**
  - $D_v = 0.08 \to 0.0792$ ($-1.0\%$ error)
  - $(F+k) = 0.095 \to 0.0880$ ($-7.3\%$ error)
- **Support Recovery:** $3/3$ true terms isolated, $0$ false positives, **Exact Support F1 = 1.000**.
