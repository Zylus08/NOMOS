# Project NOMOS — Milestone M3
## Spatiotemporal Identifiability & Monochromatic Collinearity

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** A01 (Identifiability Theory)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### Mathematical Theorem: Monochromatic Differential Collinearity

Let $u(x, t) = A \sin(k x - \omega t)$.
Then for any spatial derivative of odd order $2m + 1$:
$$rac{\partial^{2m+1} u}{\partial x^{2m+1}} = (-1)^m k^{2m} rac{\partial u}{\partial x}$$

**Corollary:** Along any single pure Fourier mode, linear advection ($u_x$), 3rd-order dispersion ($u_{xxx}$), and 5th-order hyper-dispersion ($u_{xxxxx}$) are strictly collinear. Unconstrained regression splits coefficients across all odd basis terms.
**Remedy:** Identifiability strictly requires multi-frequency excitation or non-harmonic profiles.
