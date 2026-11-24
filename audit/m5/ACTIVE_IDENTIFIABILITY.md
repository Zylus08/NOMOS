# Project NOMOS — Milestone M5
## Active Identifiability & Structural Model Discrimination

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M5 Phase 6 Diagnostics & Theory  
**Date:** 2026-11-24  

---

### 1. Mathematical Identifiability in Spatiotemporal Systems

A physical governing law $\mathcal{M}^*$ parameterized by vector field $f(u; \boldsymbol{\theta}^*)$ is **structurally identifiable** from an observation space $\mathcal{X}$ if and only if:
$$\forall \boldsymbol{\theta}_1, \boldsymbol{\theta}_2: \quad f(u; \boldsymbol{\theta}_1) = f(u; \boldsymbol{\theta}_2) \quad \forall u \in \mathcal{X} \implies \boldsymbol{\theta}_1 = \boldsymbol{\theta}_2$$

#### The Traveling Wave Degeneracy:
Consider a single solitary wave solution $u(x, t) = \phi(x - ct)$ of the Korteweg–de Vries equation:
$$u_t = -6 u u_x - u_{xxx}$$
By the chain rule for any traveling wave:
$$u_t = -c u_x$$
Hence, on the 1-soliton manifold $\mathcal{S}_1 = \{ \phi(x - ct) \mid x \in \mathbb{R} \}$:
$$f_{\text{KdV}}(u) \equiv f_{\text{Advection}}(u) \quad \forall u \in \mathcal{S}_1$$
The models are **structurally unidentifiable** under passive observation of single traveling waves!

---

### 2. Autonomous Diagnostic States (`IdentifiabilityStatus`)

| Status | Definition | Agent Decision |
| :--- | :--- | :--- |
| `IDENTIFIED` | Single hypothesis satisfies $\Delta \text{BIC} \ge 10$ and validation error ratio $\ge 3.0$ with confirmed support. | Terminate loop; return winning law. |
| `MULTIPLE_PLAUSIBLE_LAWS` | Multiple competing laws exhibit comparable predictive accuracy ($\Delta \text{BIC} < 10$). | Continue experimentation; synthesize discriminative design. |
| `INSUFFICIENT_EXCITATION` | Field variance below threshold; dynamics confined to linear or stationary manifold. | Request broadband excitation experiment. |
| `NONIDENTIFIABLE` | All active hypotheses falsified or severe rank deficiency persists across pool. | Terminate; declare unidentifiable. |
| `BUDGET_EXHAUSTED` | Maximum experimental budget reached before conclusive discrimination. | Terminate; output surviving candidates. |
| `NUMERICAL_FAILURE` | Simulator or learner encountered numerical instability (NaN/inf). | Abort episode; record failure. |
