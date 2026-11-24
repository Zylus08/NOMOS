# Project NOMOS — Milestone M5
## Information-Gain Experiment Acquisition Strategies & Mathematical Objectives

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M5 Phase 3 Mathematical Specification  
**Date:** 2026-11-24  

---

### 1. Acquisition Strategy Formulation

Let $\mathcal{H}_{\text{active}} = \{ h_1, h_2, \dots, h_K \}$ denote the set of active candidate physical hypotheses, each parameterizing a spatial vector field $u_t = f_{h_i}(u; \boldsymbol{\theta}_i)$.
Let $\mathcal{U}_{\text{pool}} = \{ u_0^{(1)}, u_0^{(2)}, \dots \}$ denote the candidate space of experimental configurations, with associated resource cost $C(u_0)$.

---

### 2. Strategy Taxonomy & Mathematical Formulations

#### Strategy A: Random Acquisition (`AcquisitionStrategy.RANDOM`)
$$u_0^* \sim \operatorname{Uniform}(\mathcal{U}_{\text{pool}})$$
Represents stochastic non-adaptive sampling. Provides an unbiased baseline but suffers from high sample complexity when degeneracies are prevalent.

#### Strategy B: Fixed Sequential Design (`AcquisitionStrategy.FIXED`)
$$u_0^{(k)} = \mathcal{U}_{\text{pool}}[k \pmod{|\mathcal{U}_{\text{pool}}|]}$$
Represents standard non-adaptive scientific protocols that step through a predetermined schedule regardless of intermediate data.

#### Strategy C: Greedy Model Disagreement (`AcquisitionStrategy.GREEDY_DISAGREEMENT`)
Targeted pairwise discrimination between the top two leading candidate laws:
$$u_0^* = \arg\max_{u_0 \in \mathcal{U}_{\text{pool}}} \int_{\Omega} \left\| f_{h_{(1)}}(u_0) - f_{h_{(2)}}(u_0) \right\|_2^2 d\mathbf{x}$$
Directly seeks configurations where leading hypotheses make the most divergent physical predictions.

#### Strategy D: Cost-Normalized Disagreement (`AcquisitionStrategy.COST_NORMALIZED`)
Balances information gain against experimental resource expenditure:
$$u_0^* = \arg\max_{u_0 \in \mathcal{U}_{\text{pool}}} \frac{\int_{\Omega} \left\| f_{h_{(1)}}(u_0) - f_{h_{(2)}}(u_0) \right\|_2^2 d\mathbf{x}}{C(u_0)}$$
where $C(u_0)$ accounts for integration time steps, sensor spatial volume, and compute overhead.

#### Strategy E: Uncertainty-Aware Ensemble Variance (`AcquisitionStrategy.UNCERTAINTY_AWARE`)
Maximizes the evidence-weighted predictive variance across the full active hypothesis portfolio:
$$\bar{f}(u_0) = \sum_{k=1}^K w_k f_{h_k}(u_0), \quad w_k = \frac{\exp(-\frac{1}{2}\Delta \text{BIC}_k)}{\sum_j \exp(-\frac{1}{2}\Delta \text{BIC}_j)}$$
$$u_0^* = \arg\max_{u_0 \in \mathcal{U}_{\text{pool}}} \sum_{k=1}^K w_k \int_{\Omega} \left\| f_{h_k}(u_0) - \bar{f}(u_0) \right\|_2^2 d\mathbf{x}$$
Promotes exploration across regions of high epistemic model uncertainty.
