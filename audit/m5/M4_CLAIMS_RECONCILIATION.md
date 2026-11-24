# Project NOMOS — Milestone M5
## M4 Claims Reconciliation, Forensic Corrections & Versioned Errata

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Date:** 2026-11-24  

---

### 1. Investigation 1: Kuramoto–Sivashinsky Recovery Status

- **M4 Finding:** In `audit/m4/RAW_EXPERIMENTS.csv`, exact recovery for Kuramoto–Sivashinsky ($u_t = -u u_x - u_{xx} - u_{xxxx}$) is recorded as $0.0\%$ across all noisy runs, despite high Support F1 scores ($0.9722$ for adaptive beam search).
- **Physical Derivation:** The 4th spatial derivative $\partial_{xxxx} u$ possesses the Fourier multiplier $k^4$. At $N=128$, the highest resolved wavenumber $k \sim 64$ amplifies measurement noise by $k^4 \sim (64)^4 \approx 1.68 \times 10^7$. Consequently, even tiny noise perturbations severely distort numerical 4th-derivative coefficients beyond the 25% relative error threshold.
- **Certified Errata & Clarification:**
  Milestone M4 demonstrated **exact structural support discovery** of Kuramoto–Sivashinsky (identifying all 3 true physical operators without false positives under multi-mode excitation), but did **NOT** achieve exact numerical parameter recovery under noisy observations. In M5, KS recovery must be classified as *Correct Support / Inaccurate Coefficients* under noise.

---

### 2. Investigation 2: Integrating-Factor Runge–Kutta 4 (IF-RK4) Stability

- **M4 Finding:** M4 documents claimed IF-RK4 provides "unconditional stability" for PDE simulation.
- **Mathematical Derivation:** In IF-RK4, the stiff linear operator (diffusion $\nu \nabla^2$ or dispersion $\partial_{xxx}$) is transformed into Fourier space and stepped analytically via the exact matrix exponential $e^{L \Delta t}$. For dissipative operators ($\text{Re}(L) \le 0$), $\|e^{L \Delta t}\| \le 1$, which is unconditionally stable.
- **Limitation & Correction:** However, the nonlinear advection stage ($\mathbf{u} \cdot \nabla \omega$ or $u u_x$) is stepped using explicit Runge–Kutta 4 stages. Explicit nonlinear stepping remains subject to the standard Courant–Friedrichs–Lewy (CFL) condition:
  $$\Delta t \le C_{\text{CFL}} \frac{\Delta x}{\max \|\mathbf{u}\|}$$
- **Certified Errata:** IF-RK4 is **linearly unconditionally stable** with respect to spatial diffusion/dispersion, but **conditionally stable** with respect to nonlinear advection.

---

### 3. Investigation 3: 2D Navier–Stokes Validation Domain

- **M4 Finding:** Primary validation for Navier–Stokes 2D was performed on the Taylor–Green vortex decay.
- **Forensic Check:** For the Taylor–Green vortex:
  $$\mathbf{u} \cdot \nabla \omega = u \partial_x \omega + v \partial_y \omega \equiv 0$$
  The nonlinear convective advection vanishes identically for all $(x, y, t)$.
- **Certified Errata & Action:** The Taylor–Green test certifies 2D Poisson streamfunction inversion and viscous dissipation, but does *not* validate the nonlinear convective term $\mathbf{u} \cdot \nabla \omega$. In M5, 2D fluid dynamics validation is formally extended to convective vortex mergers and dipoles where $\mathbf{u} \cdot \nabla \omega \neq 0$.

---

### 4. Investigation 4: Active vs. Passive Experiment Budget Parity

- **M4 Protocol Review:** In M4, active and passive WSINDy runs were executed on single trajectory instances of length $M$.
- **M5 Protocol Enforcement:** To eliminate observation budget discrepancies, all active and passive experimentation comparisons in M5 must operate under **strictly matched experimental resource budgets**:
  - Matched total simulation queries ($N_{\text{queries}}$).
  - Matched total time steps integrated ($M_{\text{total}}$).
  - Matched total space-time observation volume ($\int_{\Omega \times T} dV$).

---

### 5. Investigation 5: Statistical Significance & McNemar 2x2 Contingency Reporting

- **M4 Review:** M4 reported McNemar significance $\chi^2 = 20.05, p = 7.56 \times 10^{-6}$ for Active vs. Fixed design.
- **M5 Enforcement:** Every McNemar test must explicitly report the full $2 \times 2$ contingency table:
  $$\begin{pmatrix} n_{00} & n_{01} \\ n_{10} & n_{11} \end{pmatrix}$$
  where $n_{10}$ denotes cases where the Active strategy succeeded and the Baseline failed, and $n_{01}$ denotes cases where the Baseline succeeded and Active failed. Exact binomial two-sided $p$-values must be reported when discordant counts are small ($n_{10} + n_{01} < 25$).

---

### 6. Investigation 6: Oracle Isolation & No Hidden Information Leakage

- **Audit:** Checked `nomos/pde/active_identifiability.py`. Model disagreement $\mathcal{D}(u_0) = \int \| f_{\mathcal{M}_1}(u_0) - f_{\mathcal{M}_2}(u_0) \|^2 dx$ was computed purely using the learned candidate surrogate functions without accessing simulator internals.
- **M5 Enforcement:** The closed-loop controller will be architected such that simulator oracle access is quarantined behind a strict client-server or functional isolation boundary, guaranteeing that neither experiment selection nor stopping criteria ever inspect ground-truth equations or hidden parameters.
