# NOMOS Milestone M2 — Epistemic Uncertainty & Bootstrap Diagnostics

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Uncertainty Specialists:** Agents A07, G07  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Module:** `nomos/evaluation/identifiability.py`  

---

## 1. Separation of Aleatoric and Epistemic Uncertainty

In scientific equation discovery, two distinct forms of uncertainty must be quantified:
1. **Aleatoric Uncertainty:** Stochastic observation noise corrupting state measurements: $y(t) = x(t) + \epsilon(t)$.
2. **Epistemic Uncertainty:** Ambiguity in the discovered mathematical functional form and continuous parameter estimates resulting from finite trajectory length, limited phase-space coverage, or model misspecification.

---

## 2. Non-Parametric Residual Bootstrap Protocol

To compute rigorous parameter confidence intervals without making unwarranted Gaussian posterior assumptions, NOMOS M2 implements a **non-parametric residual bootstrap**:

### Algorithm:
1. Let $T^*$ be the discovered expression tree containing $p$ continuous constants $\mathbf{c}^* \in \mathbb{R}^p$.
2. For bootstrap iteration $b = 1, \dots, B$ ($B=15$ default, $B=5$ fast):
   - Resample $M$ indices with replacement from $\{1, \dots, M\}$:
     $$\mathcal{I}_b \sim \text{Uniform}(\{1, \dots, M\})$$
   - Form bootstrap sample $(X^{(b)}, y^{(b)}) = (X[\mathcal{I}_b], y[\mathcal{I}_b])$.
   - Refit continuous constants $\mathbf{c}^{(b)}$ via L-BFGS-B on the bootstrap sample.
3. Compute summary statistics across the bootstrap ensemble:
   - Mean parameter estimate: $\bar{c}_j = \frac{1}{B} \sum_{b=1}^B c_j^{(b)}$
   - Parameter standard deviation: $\hat{\sigma}_j = \sqrt{ \frac{1}{B-1} \sum_{b=1}^B (c_j^{(b)} - \bar{c}_j)^2 }$
   - Empirical 95% Confidence Interval: $[c_{j, 2.5\%}, \; c_{j, 97.5\%}]$.

---

## 3. Structural Stability Score

The bootstrap procedure also computes the **Structural Stability Score**:
$$\mathcal{S}_{\text{struct}} = \frac{1}{B} \sum_{b=1}^B \mathbb{I}\left( \text{loss}(T^*; X^{(b)}) \le 1.1 \cdot \min_{T \in \text{Pareto}} \text{loss}(T; X^{(b)}) \right)$$
If $\mathcal{S}_{\text{struct}} < 0.70$, it indicates that small perturbations in the observation data cause the selected equation structure to be displaced by competing mathematical candidates, signaling structural fragility.
