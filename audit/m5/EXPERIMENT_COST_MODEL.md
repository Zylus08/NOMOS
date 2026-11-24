# Project NOMOS — Milestone M5
## Experimental Cost Modeling & Resource Accounting

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M5 Phase 7 Cost Model  
**Date:** 2026-11-24  

---

### 1. Multi-Resource Accounting Principles

In physical laboratory and large-scale simulation science, experimentation is never free.
To prevent arbitrary scalar scoring, NOMOS defines transparent, dimensionally consistent experimental resource metrics:

| Resource Metric | Symbol | Unit | Physical Interpretation |
| :--- | :--- | :--- | :--- |
| **Trajectory Queries** | $N_q$ | integer queries | Number of independent experimental runs initiated. |
| **Total Temporal Steps** | $M_{\text{total}}$ | steps | Total integrated time discretizations $\sum M_k$. |
| **Spatial Sensor Points** | $N_{\text{pts}}$ | sensors | Discretized spatial measurement points $N_x \times N_y$. |
| **Observation Volume** | $\mathcal{V}_{\text{obs}}$ | $\text{m}^d \cdot \text{s}$ | Spatiotemporal volume $\int_{\Omega \times T} d\mathbf{x} dt$. |
| **Simulation Compute Time**| $T_{\text{sim}}$ | seconds | Wall-clock numerical integration time. |
| **Discovery Search Time**  | $T_{\text{search}}$| seconds | Algorithmic time spent on beam search / WSINDy. |

---

### 2. Cost-Normalized Experiment Selection

The cost-normalized acquisition objective (`AcquisitionStrategy.COST_NORMALIZED`) balances discrimination against cost:
$$\operatorname{Gain}(u_0) = \frac{\mathcal{D}(u_0)}{C(u_0)}$$
where:
$$C(u_0) = w_q N_q + w_v \mathcal{V}_{\text{obs}} + w_t T_{\text{sim}}$$
By default, unit-normalized weights ($w_q = 1.0$) allow fair comparison across matched experimental queries.
Observation budget parity between Active and Passive experimentation is enforced by evaluating algorithms at **identical cumulative $N_q$ and $M_{\text{total}}$**.
