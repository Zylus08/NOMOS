# Project NOMOS — Milestone M4
## Spatiotemporal PDE Benchmark Protocol & Experimental Methodology

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 9 Protocol Specification  
**Date:** 2026-11-23  

---

### 1. Benchmark Systems Matrix

Milestone M4 establishes a 6-system benchmark suite spanning 1D and coupled 2D spatial manifolds:

| System | Dimension | Channels | Governing Physics | Spatial Grid | Temporal Steps | Ground-Truth Invariants |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Viscous Burgers** | 1D | $u$ | Advection-diffusion shock steepening | $N=64$ | $M=50$ | Viscous decay |
| **Korteweg–de Vries (KdV)** | 1D | $u$ | Nonlinear dispersive solitary waves | $N=128$ | $M=50$ | Soliton mass/momentum |
| **Kuramoto–Sivashinsky** | 1D | $u$ | Reaction-diffusion spatiotemporal chaos | $N=128$ | $M=50$ | Conserved spatial mean |
| **Gray–Scott** | 2D | $u, v$ | Coupled autocatalytic spot division | $32 \times 32$ | $M=30$ | Positivity $u, v \ge 0$ |
| **FitzHugh–Nagumo** | 2D | $u, v$ | Coupled excitable spiral waves | $32 \times 32$ | $M=40$ | Limit-cycle bounded |
| **Navier–Stokes 2D** | 2D | $\omega, u, v$ | Incompressible vortex transport | $32 \times 32$ | $M=25$ | $\nabla \cdot \mathbf{u} = 0$, circulation |

---

### 2. Evaluator Sandbox & Data Leakage Protection

- **Clean Observation Stripping:** All discovery engines observe only `SpatiotemporalField` with `u_clean = None`, `u_t_true = None`, and `true_parameters = None`.
- **Measurement Noise Injection:** Additive Gaussian noise is injected relative to empirical field channel standard deviation:
  $$\mathbf{u}_{\text{obs}} = \mathbf{u} + \eta \cdot \operatorname{std}(\mathbf{u}) \cdot \mathcal{N}(0, 1)$$
  across 4 controlled levels: $0.0\%$, $1.0\%$, $5.0\%$, and $10.0\%$.
- **Seed Reproducibility:** Each evaluation is repeated across 3 independent pseudo-random seeds ($42, 43, 44$).
- **Total Ledger Size:** $6 \text{ Systems} \times 4 \text{ Methods} \times 4 \text{ Noise Levels} \times 3 \text{ Seeds} = 288$ execution records in `audit/m4/RAW_EXPERIMENTS.csv`.

---

### 3. Evaluation Metrics

1. **Exact Support Recall / Precision / F1:**
   $$\text{Precision} = \frac{|\hat{S} \cap S^*|}{|\hat{S}|}, \quad \text{Recall} = \frac{|\hat{S} \cap S^*|}{|S^*|}, \quad \text{F1} = \frac{2 P R}{P + R}$$
2. **Mean Relative Coefficient Error:**
   $$\text{Error}_c = \frac{1}{|S^*|} \sum_{k \in S^*} \frac{|\hat{c}_k - c_k^*|}{|c_k^*|}$$
3. **Exact Recovery Rate:**
   A run is classified as **Exact Recovery** if and only if $\text{F1} = 1.000$ (zero false positives and zero false negatives) and $\text{Error}_c \le 0.25$.
