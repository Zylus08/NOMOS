# Project NOMOS — Milestone M5
## Methodological Novelty Matrix: Closed-Loop Active Experimentation vs Prior Art

**Principal Investigator / Git Identity:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Milestone:** M5 — Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery  

---

### 1. Context & Prior Art Survey

Standard scientific machine learning and equation identification methods typically operate under **passive, offline regimes**:
- **SINDy (Brunton et al., 2016):** Operates on pre-collected historical time-series. Assumes observation trajectories already contain sufficient dynamic excitation.
- **Weak-Form WSINDy (Reinbold et al., 2020 / Messenger & Bortz, 2021):** Solves noise degradation via test-function integration, but remains strictly passive and offline.
- **Active Learning in Regression (Settles, 2009):** Focuses on pointwise input selection ($x^*$) to minimize prediction variance in black-box models, not symbolic law identifiability.
- **Bayesian Experimental Design (Chaloner & Verdinelli, 1995):** Maximizes expected information gain (mutual information) on parameter distributions, but typically assumes a single parametric model rather than discriminating competing structural equation families.

Milestone M5 introduces a **closed-loop autonomous hypothesis-discrimination framework** specifically designed to resolve structural non-identifiabilities in governing physical laws under constrained observation budgets.

---

### 2. Novelty Matrix

| Dimension | Classical SINDy / WSINDy | Bayesian Exp. Design | Active Learning (ML) | **NOMOS Milestone M5** |
| :--- | :--- | :--- | :--- | :--- |
| **Observation Mode** | Passive, static dataset | Active, parameter focus | Active, point label queries | **Closed-loop autonomous 8-stage cycle** |
| **Model Representation** | Single candidate library | Single parametric model | Black-box neural network / GP | **Competing symbolic hypotheses portfolio** |
| **Acquisition Criterion** | None (fixed data) | Expected parameter info gain | Uncertainty / variance | **Functional vector-field divergence & cost normalization** |
| **Physical Isolation** | Unconstrained data access | Simulated or manual | Unconstrained label oracle | **Quarantined sandbox with multi-resource cost accounting** |
| **Identifiability Audit** | Post-hoc residual checks | Fisher information matrix | Confidence intervals | **Decisive Bayes Factor ($\Delta \text{BIC} \ge 10$) & paired falsification** |
| **Memory / Lineage** | Overwrites on refit | Posterior distribution | Dataset accumulation | **Immutable hypothesis portfolio with versioned lineage** |
| **Degeneracy Resolution** | Fails on solitary waves | Parameter tuning only | Exploits smooth interpolation | **Actively targets dispersive wave packets & colliding states** |

---

### 3. Key Algorithmic Contributions

1. **Closed-Loop Hypothesis Portfolio (`HypothesisPortfolio`):** Immutable scientific memory tracking candidate equation lineages, versions, supporting trials, and explicit falsification reasons without silent overwrites.
2. **Functional Vector-Field Divergence (`compute_pairwise_disagreement`):** Computes $\mathcal{D}(u_0; h_1, h_2) = \| f_{h_1}(u_0) - f_{h_2}(u_0) \|_2^2$ directly from candidate vector fields to pinpoint initial states that maximally separate competing hypotheses.
3. **Multi-Resource Cost-Normalized Acquisition (`cost_normalized`):** Trades off information gain against trajectory query volume, temporal duration, and computational cost.
4. **Information-Theoretic Stopping Audit (`IdentifiabilityAuditor`):** Concludes autonomous experimentation when Bayes Factor $\Delta \text{BIC} \ge 10$ provides decisive Kass-Raftery statistical separation, or halts when budget is exhausted.
