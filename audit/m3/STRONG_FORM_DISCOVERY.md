# Project NOMOS — Milestone M3
## Strong-Form PDE Discovery (PDE-FIND / SINDy-PDE) Report

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** F01 (Sparse Baselines), C02 (Strong Form)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Architecture & Formulation

Strong-form discovery constructs candidate spatial derivatives directly from state snapshots:
$$u_t = \Theta(U) \Xi$$
where $\Theta(U) = [u, u_x, u_{xx}, u_{xxx}, u_{xxxx}, u u_x, u^2, u^3, u^2 u_x]$.
Solved via Sequentially Thresholded Least Squares (STLSQ) with $L_2$ column scaling and active-set refitting.

---

### 2. Empirical Performance & Failure Modes

1. **Noiseless Performance (0% Noise):**
   - **Viscous Burgers:** 100% exact support recovery ($u_t = -1.000 u u_x + 0.050 u_{xx}$, coeff error $0.007$).
   - **Linear Advection:** 100% exact recovery ($u_t = -0.9999 u_x$) when multi-frequency waves break monochromatic collinearity.
2. **Catastrophic Breakdown Under Measurement Noise:**
   - At 1% noise, StrongSINDy exact recovery drops to **0.0%** on Viscous Burgers.
   - At 5% and 10% noise, high-order finite difference derivatives amplify measurement noise exponentially ($O(\eta / \Delta x^m)$), corrupting the design matrix $\Theta(U)$.
