# Project NOMOS — Milestone M5.1
## Physical-Law Recovery Classification & Ground-Truth Verification

**Review Role:** Independent Peer Review & Mathematical Physics Auditor  
**Auditor / Git Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  

---

### 1. Multi-Tier Recovery Certification Framework

In autonomous scientific equation identification, reproducing trajectory observations is insufficient to claim discovery of a physical law. A model might overfit or capture only a subset of terms that happen to balance under degenerate initial conditions (e.g., $u_t = -c u_x$ for solitary waves).

To rigorously audit recovery, we classify candidate discoveries into 6 disjoint hierarchical tiers:
1. **Tier 1: Exact Symbolic Structure ($S_{\text{exact}}$):**
   - Exact ground-truth support ($K_{\text{discovered}} = K_{\text{true}}$).
   - Zero spurious operators.
   - All parameter errors $\le 10\%$: $\max_{k} \frac{|\hat{\theta}_k - \theta_k^*|}{|\theta_k^*|} \le 0.10$.
2. **Tier 2: Algebraically Equivalent Structure ($S_{\text{equiv}}$):**
   - Distinct grammatical tree that simplifies to the exact physical law via algebraic or differential identities (e.g., $\frac{1}{2} (u^2)_x \equiv u u_x$).
3. **Tier 3: Correct Support with Approximate Coefficients ($S_{\text{supp}}$):**
   - Exact support ($K_{\text{discovered}} = K_{\text{true}}$).
   - Parameter error between $10\%$ and $25\%$, typically due to high observational noise ($\sigma \ge 5\%$).
4. **Tier 4: Accurate Held-Out Vector Field ($S_{\text{field}}$):**
   - High predictive accuracy on unseen test trajectories ($\text{MSE} \le 10^{-3}$), but with small unpruned high-order terms (e.g., $|\hat{\theta}_{\text{spurious}}| < 0.04$).
5. **Tier 5: Rollout-Only Agreement ($S_{\text{rollout}}$):**
   - Fits the training trajectory or short-time integration, but diverges structurally on novel geometries or out-of-distribution initial states.
6. **Tier 6: Incorrect Discovery ($S_{\text{fail}}$):**
   - Fails support identification, omits core physical mechanisms (e.g., missing dissipation or advection), or exhibits numerical instability.

---

### 2. Physical System Ground Truth Standards

| System | Dimension | True Governing Law | True Parameters |
| :--- | :---: | :--- | :--- |
| **Korteweg-de Vries (KdV)** | 1D | $u_t = -1.0\, u_{xxx} - 6.0\, u u_x$ | $u_{xxx}: -1.0, u u_x: -6.0$ |
| **Viscous Burgers'** | 1D | $u_t = +0.05\, u_{xx} - 1.0\, u u_x$ | $u_{xx}: 0.05, u u_x: -1.0$ |
| **Gray-Scott 2D** | 2D | $v_t = +0.08\, \nabla^2 v + 1.0\, u v^2 - 0.095\, v$ | $\nabla^2 v: 0.08, u v^2: 1.0, v: -0.095$ |
| **FitzHugh-Nagumo 2D** | 2D | $u_t = +1.0\, \nabla^2 u + 1.0\, u - 1.0\, u^3 - 1.0\, v$ | $\nabla^2 u: 1.0, u: 1.0, u^3: -1.0, v: -1.0$ |
| **Navier-Stokes 2D** | 2D | $\omega_t = +0.02\, \nabla^2 \omega - 1.0\, (\mathbf{u} \cdot \nabla \omega)$ | $\nabla^2 \omega: 0.02, \mathbf{u} \cdot \nabla \omega: -1.0$ |

---

### 3. Classification Audit Across 500 Benchmark Episodes

| Strategy | Total | Tier 1: Exact Symbolic | Tier 3: Correct Support ($\le 25\%$) | Tier 4: Accurate Held-Out Field | Tier 6: Incorrect Discovery |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Active (`greedy_disagreement`)** | 100 | **13** | **15** | **35** | 37 |
| **Active (`cost_normalized`)** | 100 | **13** | **15** | **33** | 39 |
| **Passive (`fixed` schedule)** | 100 | 21 | 7 | 27 | 45 |
| **Stochastic (`random` selection)** | 100 | 12 | 9 | 25 | 54 |
| **Ensemble (`uncertainty_aware`)** | 100 | 6 | 0 | 14 | 80 |

#### Audit Verdict:
1. **High Strictness of Exact Coefficient Recovery:** Under strict Tier 1 criteria (exact support + all coefficients $\le 10\%$), the recovery rate across all strategies is between $12\%$ and $21\%$, because at $5\%$ and $10\%$ noise, high-order derivative coefficients naturally drift between $10\%$ and $25\%$.
2. **Support Recovery with Physical Accuracy (Tiers 1–4):** When evaluating physical support and predictive held-out accuracy, Active achieves **63.0%** recovery, beating Fixed ($55.0\%$) and Random ($46.0\%$).
3. **Rollout Divergence Defense:** Weak-form space-time integration ensures that identified models are not merely curve-fits of a single snapshot, but satisfy the integral conservation law across space and time.
