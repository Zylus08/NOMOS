# NOMOS Milestone M2 — Identifiability Diagnostics & Orbital Excitation

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Identifiability Specialists:** Agents A01, A07, G06, G07  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Module:** `nomos/evaluation/identifiability.py`  

---

## 1. Problem Formulation: The Ill-Posed Inverse Problem

The discovery of governing differential equations $\dot{x} = f(x)$ from discrete trajectories is inherently ill-posed. In empirical practice, three distinct epistemic scenarios emerge:
1. **Scenario 1: Truly Identifiable System (`UNIQUE_LAW`).** Trajectories explore phase space sufficiently such that exactly one symbolic structure achieves near-optimal loss, and its continuous parameters are sharply determined.
2. **Scenario 2: Under-Excited Trajectory (`INSUFFICIENT_EVIDENCE`).** The trajectory remains trapped on an attractor, limit cycle, or fixed point; multiple distinct vector fields coincide on this submanifold but diverge everywhere else in state space.
3. **Scenario 3: Collinear Hypothesis Degeneracy (`MULTIPLE_PLAUSIBLE_LAWS`).** Multiple mathematically non-equivalent expressions achieve statistically indistinguishable fitting errors within the observation window.

---

## 2. Phase-Space Orbital Excitation Metric

To mathematically detect Scenario 2 before running expensive symbolic regression, NOMOS M2 implements the **Singular Value Orbital Excitation Test**:

1. Center the state trajectory matrix:
   $$\tilde{X} = X - \frac{1}{M} \mathbf{1} \mathbf{1}^T X \in \mathbb{R}^{M \times n}$$
2. Compute the Singular Value Decomposition (SVD):
   $$\tilde{X} = U \Sigma V^T, \quad \Sigma = \text{diag}(\sigma_1, \sigma_2, \dots, \sigma_n), \quad \sigma_1 \ge \sigma_2 \ge \dots \ge \sigma_n$$
3. Compute the **Manifold Excitation Ratio**:
   $$\rho_{exc} = \frac{\sigma_{\min}(\tilde{X})}{\sigma_{\max}(\tilde{X})}$$

### Diagnostic Criteria:
- If $\sigma_{\max} < 0.01$ or $\rho_{exc} < 10^{-4}$:
  The system is diagnosed as topologically degenerate (trapped on a fixed point or 1D subspace).
  NOMOS M2 immediately halts discovery for that dimension and outputs `INSUFFICIENT_EVIDENCE`.

---

## 3. Multiple Plausible Law Detection

Given a populated `ParetoFrontier` containing non-dominated candidates, let $T^*$ be the candidate minimizing the combined Pareto score:
$$T^* = \arg\min_{T \in \text{Pareto}} \left( \mathcal{L}_{MSE}(T) + 0.005 \cdot \mathcal{C}(T) \right)$$

We inspect all other candidate laws $T' \in \text{Pareto}$ ($T' \neq T^*$). If there exists any structurally non-equivalent law $T'$ such that:
$$\mathcal{L}_{MSE}(T') \le (1 + \tau) \cdot \mathcal{L}_{MSE}(T^*)$$
with tolerance ratio $\tau = 0.08$ (8%), NOMOS M2 flags:
$$\text{Status} = \text{MULTIPLE\_PLAUSIBLE\_LAWS}$$
and compiles a catalog of all competing alternative mathematical laws, reporting their expressions, MSE, and complexity to the researcher.
