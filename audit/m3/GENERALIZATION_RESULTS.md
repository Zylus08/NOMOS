# Project NOMOS — Milestone M3
## Generalization & Extrapolation Across Held-Out Initial Conditions

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** C03 (Generalization)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### Generalization Protocol

Models were evaluated across held-out initial conditions:
1. **Harmonic Monochromatic:** $u_0(x) = \sin(x)$.
2. **Multi-Wavenumber Composite:** $u_0(x) = \sin(x) + 0.5 \cos(2x)$.
3. **Localized Gaussian Pulse:** $u_0(x) = \exp(-4 (x - \pi)^2)$.

*Finding:* Testing on multi-wavenumber and pulse conditions is essential to break odd-derivative collinearity ($u_{xxx} \equiv -u_x$) and ensure true physical generalizability.
