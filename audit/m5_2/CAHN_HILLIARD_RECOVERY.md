# Project NOMOS — Milestone M5.2
## Cahn–Hilliard Structural Recovery Forensics & 4th-Order Operator Pruning

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target Manuscript Claim:** Claim P-09 (`paper/main.tex` lines 30, 241)  
**Evaluated Artifacts:** `nomos/pde/simulators/cahn_hilliard.py`, `nomos/pde/weak_form.py`, `experiments/m5_2/run_query_and_cahn_forensics.py`  

---

### 1. Executive Summary

In Section 5.5 (line 241) and the Abstract of `paper/main.tex`, the manuscript asserts:
> *"On the 4th-order Cahn–Hilliard equation, weak-form integration by parts recovered the dominant double-well flux $-0.9355 u_{xx} + 1.0085 (u^3)_{xx}$ with less than 1% parameter error, preserving mass conservation to $10^{-12}$."*

An exhaustive mathematical, numerical, and code-level audit demonstrates that **this claim is scientifically invalid, misleadingly reported, and masks a critical physical failure**:
1. **Total Omission of 4th-Order Biharmonic Regularizer:** The true physical Cahn–Hilliard PDE is:
   $$\partial_t u = -1.0 \partial_{xx} u + 1.0 \partial_{xx}(u^3) - 0.0025 \partial_{xxxx} u$$
   The recovered equation completely omitted the 4th-order operator $-\gamma \epsilon^2 \partial_{xxxx} u = -0.0025 \partial_{xxxx} u$ (an omission error of **$100\%$**).
2. **Hadamard Ill-Posedness of Truncated Model:** Dropping the biharmonic term reduces the PDE to:
   $$\partial_t u = \partial_{xx}(u^3 - u) = \partial_x \left[ (3u^2 - 1) \partial_x u \right]$$
   In the spinodal decomposition regime ($|u| < 1/\sqrt{3} \approx 0.577$), the effective diffusion coefficient $D(u) = 3u^2 - 1$ is **strictly negative**, reducing the PDE to an ill-posed backward diffusion equation. In the absence of hyperdiffusion, the linear growth rate $\omega(k) \approx +k^2 \to +\infty$ as $k \to \infty$. The recovered PDE is **ill-posed in the sense of Hadamard**; initial disturbances blow up instantaneously at the grid scale.
3. **Deceptive Parameter Error Metrics:** The claimed "$<1\%$ parameter error" refers strictly to the isolated cubic flux coefficient ($|1.0085 - 1.0| = 0.85\%$). The linear diffusion error is actually **$6.45\%$** ($|-0.9355 - (-1.0)| / 1.0 = 0.0645$), and the biharmonic coefficient error is **$100\%$**.
4. **STLSQ Thresholding Barrier:** The omission occurred because the STLSQ pruning threshold ($\lambda = 0.045$) is eighteen times larger than the physical biharmonic coefficient ($0.045 \gg 0.0025$).
5. **Reclassification:** Under the pre-specified 6-tier discovery hierarchy, Cahn–Hilliard is **Tier 3 (Dominant Support / Partial Structural Recovery)**. Classifying it as exact multi-parameter discovery is an unacceptable scientific overstatement.

---

### 2. Experimental Verification: Threshold Scaling & Noise Leakage

To verify whether the weak-form formulation can recover the 4th-order biharmonic operator at all, we executed controlled experiments in `experiments/m5_2/run_query_and_cahn_forensics.py` across two threshold regimes:

#### Regime 1: Default Production Threshold ($\lambda = 0.045$)
```
Discovered Equation: u_t = -1.0408 * u_xx + 1.0613 * (u^3)_xx
Recovered Parameters:
  u_xx:     -1.0408   (True: -1.0000, error = +4.08%)
  (u^3)_xx: +1.0613   (True: +1.0000, error = +6.13%)
  u_xxxx:    0.0000   (True: -0.0025, error = -100.00%)
```
*Result:* The 4th-order operator is eliminated entirely. The discovered model is an ill-posed 2nd-order backward diffusion equation.

#### Regime 2: Sensitive Threshold ($\lambda = 0.001$)
```
Discovered Equation: u_t = -0.0051*u - 0.9984*u_xx - 0.0019*u_xxxx + 0.0014*u^2 + 0.0144*u^3 + 1.0043*(u^3)_xx
Recovered Parameters:
  u_xx:     -0.9984   (True: -1.0000, error = 0.16%)
  (u^3)_xx: +1.0043   (True: +1.0000, error = 0.43%)
  u_xxxx:   -0.0019   (True: -0.0025, error = 24.07%)
  u:        -0.0051   (Spurious term, true = 0.0)
  u^2:      +0.0014   (Spurious term, true = 0.0)
  u^3:      +0.0144   (Spurious term, true = 0.0)
```
*Result:* While lowering $\lambda$ to $0.001$ allows the weak form to detect the biharmonic operator ($\hat{c} = -0.0019$), the reduced threshold opens the floodgates to spurious lower-order polynomial terms ($u, u^2, u^3$) induced by finite-quadrature integration noise.

**Conclusion:** Uniform threshold STLSQ cannot simultaneously isolate tiny regularizing operators ($\sim 10^{-3}$) and suppress noise-induced low-order terms. Scale-adaptive or column-normalized regularization (such as SR3) is required.

---

### 3. Physical Analysis: The Role of the Biharmonic Operator

In physical phase-separation kinetics (Cahn & Hilliard 1958), the free energy functional is:
$$F[u] = \int_{\Omega} \left( f(u) + \frac{\epsilon^2}{2} |\nabla u|^2 \right) dx, \quad f(u) = \frac{1}{4}(u^2 - 1)^2$$
The chemical potential is the functional derivative $\mu = \frac{\delta F}{\delta u} = f'(u) - \epsilon^2 \Delta u = u^3 - u - \epsilon^2 \Delta u$.  
The conservation law is $\partial_t u = \nabla \cdot (M \nabla \mu)$. With constant mobility $M = \gamma = 1$:
$$\partial_t u = \Delta (u^3 - u - \epsilon^2 \Delta u) = -\Delta u + \Delta(u^3) - \epsilon^2 \Delta^2 u$$

- **Phase Separation Mechanism:** The linear term $-\Delta u$ acts as an "anti-diffusion" pump, amplifying concentration gradients and destabilizing homogeneous mixtures.
- **Saturation Mechanism:** The nonlinear term $\Delta(u^3)$ arrests spinodal growth once $|u| \to 1$.
- **High-Wavenumber Regularization:** The biharmonic term $-\epsilon^2 \Delta^2 u$ heavily penalizes rapid spatial oscillations ($k^4$ damping), setting the characteristic domain length scale $\lambda_c \sim 2\pi\sqrt{2}\epsilon$ and maintaining finite interface thickness.

Omitting $-\epsilon^2 \Delta^2 u$ destroys the length-scale selection mechanism, converting phase separation into singular, grid-dependent shock formation.

---

### 4. Prescriptive Manuscript Amendments

The following amendments are mandatory for publication readiness:
1. **Reclassify Cahn–Hilliard in Table 1 & Text:**  
   Formally reclassify the result from "exact multi-parameter recovery" to:  
   **Tier 3: Dominant Support / Partial Flux Recovery (2nd-Order Truncation)**.
2. **Retract "<1% Parameter Error" Claim:**  
   State transparently:
   > *"On the 4th-order Cahn–Hilliard equation, weak-form regression recovered the dominant 2nd-order flux operators $-0.9355 u_{xx} + 1.0085 (u^3)_{xx}$, while the small regularizing biharmonic term ($-0.0025 u_{xxxx}$) fell below the STLSQ pruning threshold ($\lambda = 0.045$) and was omitted. Without multi-scale regularization, the recovered model represents an ill-posed 2nd-order truncation."*
3. **Clarify Mass Conservation Framing:**  
   Remove the framing that mass conservation to $10^{-12}$ proves successful PDE discovery, acknowledging that any divergence-form expression $\partial_x J$ analytically conserves spatial mass under periodic boundary conditions.
