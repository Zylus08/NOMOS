# Project NOMOS — Milestone M5.2
## Autocorrelation Calibration, Effective Degrees of Freedom & BIC Scaling

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target Manuscript Claim:** Claim P-03 (`paper/main.tex` lines 105–124)  
**Evaluated Artifacts:** `nomos/closed_loop/portfolio.py`, `experiments/m5_2/run_ablations.py`, `audit/m5_2/ABLATIONS_AND_BIC.json`  

---

### 1. Executive Summary

Milestone M5.1 introduced an autocorrelation-calibrated Bayesian Information Criterion ($\text{BIC}_{\text{eff}}$) based on spatial correlation lengths ($\xi_x$) and temporal persistence scales ($\tau_t$). The manuscript claimed:
> *"Treating every spatiotemporal grid point $(x_i, t_m)$ as an independent observation constitutes rampant pseudoreplication, inflating nominal sample sizes by $20\times\text{--}30\times$. Calibrating $\text{BIC}_{\text{eff}}$ with $N_{\text{eff}} = \frac{L_x T}{4 \xi_x \tau_t}$ prevents premature stopping on empirical noise."*

The M5.2 audit confirms the mathematical necessity of this calibration while identifying theoretical boundaries in its statistical interpretation:
1. **Gross Pseudoreplication in Continuous Media:** On standard discretization grids, nominal grid counts $N = N_x \times N_t$ overstate the genuine statistical degrees of freedom not merely by $20\times\text{--}30\times$, but by **$245\times\text{--}960\times$**.
2. **Prevention of Noise-Induced False Early Stopping:** Under nominal sample sizes, residual variance discrepancies as small as $0.5\%$ from random noise fluctuations produce $\Delta\text{BIC}_{\text{nominal}} = 63.84\text{--}153.22 \gg 10.0$, falsely triggering "decisive evidence" stopping. Under calibrated $N_{\text{eff}}$, the same noise discrepancy yields $\Delta\text{BIC}_{\text{eff}} = 0.07\text{--}0.62 \ll 10.0$, correctly preventing premature termination.
3. **Statistical Clarification on "Posterior Weights":** The weights $\tilde{w}_k = \frac{\exp(-\frac{1}{2}\Delta\text{BIC}_{k,\text{eff}})}{\sum_j \exp(-\frac{1}{2}\Delta\text{BIC}_{j,\text{eff}})}$ do not represent rigorous Bayesian posterior probabilities. In post-selection thresholded regression (STLSQ), standard regularity conditions fail. The weights function as an **empirical softmax heuristic over correlation-penalized residuals**.

---

### 2. Quantitative Calibration Forensics

From `audit/m5_2/ABLATIONS_AND_BIC.json`:

| Physical System | Domain Dimensions | Grid Points ($N_{\text{nominal}}$) | Spatial Length $\xi_x$ | Temporal Persistence $\tau_t$ | Effective DoF ($N_{\text{eff}}$) | Inflation Ratio | $\Delta\text{BIC}$ on $0.5\%$ Noise (Nominal) | $\Delta\text{BIC}$ on $0.5\%$ Noise (Calibrated) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **KdV 1D** | $L_x=20, T=2.0$ | $128 \times 100 = \mathbf{12,800}$ | $1.50$ | $0.50$ | **$13.3$** | **$960.0\times$** | **$+63.84$** (False stop!) | **$+0.07$** (Robust) |
| **Gray–Scott 2D** | $L_{x,y}=2.5, T=1.0$ | $32 \times 32 \times 30 = \mathbf{30,720}$ | $0.25$ | $0.10$ | **$125.0$** | **$245.8\times$** | **$+153.22$** (False stop!) | **$+0.62$** (Robust) |

#### Analysis:
1. **The Nominal Trap:** If an algorithm employs raw grid points in BIC, any model that overfits by capturing a tiny fraction of measurement noise ($\Delta\text{MSE} / \text{MSE} = 0.5\%$) gains an artificial BIC advantage of over $+60$ units. Citing Kass & Raftery's threshold of $\Delta\text{BIC} \ge 10.0$ would cause the system to declare decisive victory for the overfitted model on observation 1.
2. **The Effective Scale:** By scaling through the integrated autocorrelation scale $\xi_x = \int_0^\infty C_x(r) dr$ and $\tau_t = \int_0^\infty C_t(s) ds$, $N_{\text{eff}}$ correctly reflects the number of statistically independent spatiotemporal coherent structures.

---

### 3. Theoretical Limitations Identified by Peer Review

As noted by Reviewer Group B (Statistics) and Reviewer Group A (Applied Math), the current formulation of $N_{\text{eff}}$ contains three theoretical assumptions that must be disclosed:
1. **Spatiotemporal Separability Assumption:** Eq. (109) assumes $C(r, s) = C_x(r) C_t(s)$. For convective and dispersive equations, space and time are intrinsically coupled via characteristics $x - ct$ or dispersion relations $\omega(k)$, violating separability.
2. **Derivative Scale Mismatch:** The correlation length $\xi_x$ is computed from the state field $u(x, t)$. However, the weak-form regression evaluates higher-order spatial derivatives ($u_{xx}, u_{xxx}$), which possess significantly shorter spatial correlation lengths than $u$.
3. **Spatial Non-Stationarity:** Solitary waves and localized fronts are fundamentally non-stationary. Integrating correlation over the full domain averages the quiescent background with the localized wave packet.

---

### 4. Prescriptive Amendments for Manuscript

1. **Reframe BIC Weights as Softmax Heuristic:**  
   Replace claims of "certified temperature-calibrated posterior probabilities" with:
   > *"We compute empirical hypothesis weights $\tilde{w}_k \propto \exp(-\frac{1}{2}\Delta\text{BIC}_{k,\text{eff}})$ as a penalized residual softmax heuristic, where nominal degrees of freedom are scaled by integrated spatiotemporal correlation lengths to prevent premature stopping on correlated measurement noise."*
2. **Acknowledge Separability & Stationarity Limits:**  
   Add a technical remark in Section 3.3 acknowledging that separable spatial-temporal correlation estimates represent a first-order isotropic approximation to the true non-separable dispersion geometry.
