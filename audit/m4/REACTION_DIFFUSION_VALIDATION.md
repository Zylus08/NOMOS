# Project NOMOS — Milestone M4
## Coupled 2D Reaction–Diffusion Simulators Validation Audit

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 3 Validation  
**Date:** 2026-11-23  

---

### 1. Mathematical Models & Physical Formulation

Milestone M4 establishes two coupled 2D reaction-diffusion physical benchmark systems:

#### 1. Gray–Scott Model (Chemical Kinetics & Turing Patterns)
$$\frac{\partial u}{\partial t} = D_u \nabla^2 u - u v^2 + F(1 - u)$$
$$\frac{\partial v}{\partial t} = D_v \nabla^2 v + u v^2 - (F + k) v$$
- **Coupling Mechanics:** Species $u$ is consumed by the autocatalytic reaction $-u v^2$ and fed externally at rate $F(1-u)$. Species $v$ grows via $+u v^2$ and decays at rate $-(F+k)v$.
- **Dissipation & Diffusion:** $D_u = 0.16$, $D_v = 0.08$ on 2D torus $\mathbb{T}^2 = [0, 2.5]^2$.
- **Non-Conservative Dynamics:** Mass is actively created/destroyed: $\frac{d}{dt}\int (u+v)dx dy \neq 0$.
- **Positivity Invariant:** $u(x,y,t) \ge 0, v(x,y,t) \ge 0 \quad \forall t \ge 0$.

#### 2. FitzHugh–Nagumo Model (Excitable Media & Spiral Waves)
$$\frac{\partial u}{\partial t} = D_u \nabla^2 u + u - u^3 - v$$
$$\frac{\partial v}{\partial t} = D_v \nabla^2 v + \epsilon(u - a_1 v - a_0)$$
- **Coupling Mechanics:** Fast activator potential $u$ coupled to slow recovery variable $v$ ($\epsilon = 0.05$).
- **Wave Fronts:** Models action potential propagation, wavefront curvature, and re-entrant spiral wave excitation in biological tissue.
- **Diffusive Transport:** $D_u = 1.0, D_v = 0.0$ on $[-10, 10]^2$.

---

### 2. Numerical Integration Scheme (Integrating-Factor RK4)

Both systems exhibit severe numerical stiffness from 2D spatial diffusion ($\Delta t_{\text{CFL}} \sim \mathcal{O}(\Delta x^2)$).
To guarantee unconditional stability without numerical dispersion, NOMOS implements the 2D pseudo-spectral Integrating-Factor Runge–Kutta 4 (IF-RK4) algorithm:
1. Transforming state into 2D Fourier space $\hat{u}(\mathbf{k}, t)$ with wavenumbers $\mathbf{k} = (k_x, k_y)$.
2. Integrating the linear diffusion operator analytically:
   $$\hat{w}(\mathbf{k}, t) = e^{D \|\mathbf{k}\|^2 t} \hat{u}(\mathbf{k}, t)$$
3. Stepping the nonlinear reaction kinetics through 4th-order Runge–Kutta stages in physical space using inverse 2D FFTs.

---

### 3. Physical Invariants & Numerical Stability Matrix

| Simulator | Numerical Method | Grid | Time Steps | Conserved Invariant | Positivity Maintained | Stability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gray–Scott** | 2D Spectral IF-RK4 | $32 \times 32$ | $M=50$ | None (Open kinetic mass) | Yes ($u \ge 0, v \ge 0$) | 100% Stable (0 NaNs) |
| **FitzHugh–Nagumo** | 2D Spectral IF-RK4 | $32 \times 32$ | $M=50$ | None (Excitable limit cycle) | N/A ($u \in [-2, 2]$) | 100% Stable (0 NaNs) |
