# Project NOMOS — Milestone M3
## PDE Benchmark Suite Physical Specifications

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** B01–B12 (PDE Simulators), A01 (Mathematical PDE Theory)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Overview & Mathematical Formulations

Milestone M3 implements 6 canonical physical partial differential equations spanning parabolic, hyperbolic, dispersive, nonlinear, and chaotic dynamical regimes on 1D spatial domains:

| Benchmark Name | PDE Mathematical Formulation | Regime & Class | Standard Parameters | Spatial Domain | Boundary Conditions | Conserved / Invariant Quantity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Heat Equation** | $u_t = lpha u_{xx}$ | Parabolic / Dissipative | $lpha = 0.1$ | $[0, 2\pi]$ | Periodic | Thermal Mass: $M = \int u \, dx$ |
| **Linear Advection** | $u_t = -c u_x$ | Hyperbolic / Conservative | $c = 1.0$ | $[0, 2\pi]$ | Periodic | Energy ($L_2$ norm): $E = \int u^2 \, dx$ |
| **Viscous Burgers'** | $u_t = -u u_x + 
u u_{xx}$ | Nonlinear Advection-Diffusion | $
u = 0.05$ | $[0, 2\pi]$ | Periodic | Mass: $M = \int u \, dx$ |
| **1D Wave Equation** | $u_t = v, \; v_t = c^2 u_{xx}$ | Hyperbolic 2nd-Order System | $c = 1.0$ | $[0, 2\pi]$ | Periodic | Hamiltonian Energy: $H = rac{1}{2}\int (v^2 + c^2 u_x^2) dx$ |
| **KdV Equation** | $u_t = -6 u u_x - u_{xxx}$ | Nonlinear Dispersive | Nonlin: $6.0$, Disp: $1.0$ | $[-10, 10]$ | Periodic | Soliton Mass: $M = \int u \, dx$, Momentum: $P = rac{1}{2}\int u^2 dx$ |
| **Kuramoto–Sivashinsky** | $u_t = -u u_x - u_{xx} - u_{xxxx}$ | Spatiotemporally Chaotic | Nonlin: $1.0$, Diff: $1.0$, Hyper: $1.0$ | $[0, 32\pi]$ | Periodic | Spatial Mean: $ar{u} = rac{1}{L}\int u \, dx$ |

---

### 2. Analytical Verification Standards

1. **Heat Equation:** Verified against the exact Fourier modal decay $u(x, t) = \exp(-lpha k^2 t) \sin(k x)$. Relative $L_2$ error $< 10^{-5}$.
2. **Linear Advection:** Verified against d'Alembert shift $u(x, t) = u_0(x - c t)$. Full-period return error $< 10^{-4}$.
3. **Viscous Burgers':** Verified against Cole-Hopf travelling viscous shock profile.
4. **1D Wave Equation:** Verified against standing modal wave $u(x, t) = \sin(x) \cos(c t)$ with energy conservation drift $< 10^{-4}$.
5. **KdV Equation:** Verified using the exact 1-soliton analytical solution $u(x, t) = rac{c}{2} 	ext{sech}^2\left(rac{\sqrt{c}}{2}(x - c t - x_0)ight)$.
6. **Kuramoto-Sivashinsky:** Verified for bounded chaotic attractor dynamics ($|u| < 10.0$) and mean conservation.
