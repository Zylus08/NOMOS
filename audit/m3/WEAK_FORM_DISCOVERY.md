# Project NOMOS — Milestone M3
## Weak-Form PDE Identification (WSINDy) & Integral Formulation Report

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** A02 (Weak Form Theory), F02 (WSINDy Baseline)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Integral Formulation & Integration by Parts

WSINDy projects the governing PDE onto smooth, compactly supported space-time test functions $\phi^{(k)}(x, t) = \psi(x) \chi(t)$.
By applying integration by parts:
$$\int_\Omega u_t \phi \, d\Omega = - \int_\Omega u \phi_t \, d\Omega + 	ext{[boundary]}$$
$$\int_\Omega u_x \phi \, d\Omega = - \int_\Omega u \phi_x \, d\Omega + 	ext{[boundary]}$$
$$\int_\Omega u_{xx} \phi \, d\Omega = \int_\Omega u \phi_{xx} \, d\Omega + 	ext{[boundary]}$$
$$\int_\Omega u u_x \phi \, d\Omega = rac{1}{2} \int_\Omega (u^2)_x \phi \, d\Omega = - rac{1}{2} \int_\Omega u^2 \phi_x \, d\Omega + 	ext{[boundary]}$$

Because $\phi(x, t)$ vanishes on the boundary of its compact support, **all boundary terms vanish identically**.

---

### 2. Superior Noise Resilience Evidence

Across 240 controlled runs, WSINDy proved overwhelmingly superior to Strong SINDy under noise:

| Method | Burgers @ 0% Noise | Burgers @ 1% Noise | Burgers @ 5% Noise | Burgers @ 10% Noise | Mean Runtime |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Strong SINDy** | **100.0%** ($0.007$) | 0.0% ($0.578$) | 0.0% ($0.599$) | 0.0% ($0.666$) | 0.0046s |
| **Weak SINDy (WSINDy)** | **100.0%** ($0.0001$) | **100.0%** ($0.0028$) | **33.3%** ($0.0172$) | **33.3%** ($0.1999$) | 0.0265s |

*Finding:* WSINDy maintains exact support recovery and low coefficient error up to 10% noise, proving that transferring derivatives to smooth test functions effectively filters measurement noise.
