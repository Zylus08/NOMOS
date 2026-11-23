# Project NOMOS — Milestone M3
## Neural PDE Dynamics Surrogate & Operator Guidance Ablation

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** D01–D04 (Neural Surrogates), C04 (Ablation Statistics)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Conv1D Dynamics Surrogate Architecture

A 1D Convolutional Neural Network surrogate was designed for spatiotemporal dynamics:
- Input: field snapshot $u(t, x)$ of shape $(M, 1, N)$.
- Layers: 3 circular-padded 1D convolutional layers with Tanh activations.
- Output: predicted temporal derivative $\hat{u}_t(t, x)$.
- Trained via Adam on MSE loss against finite-difference target derivatives.
- Operator sensitivity weights $w_k$ computed via cosine similarity between predicted $\hat{u}_t$ and candidate differential fields.

---

### 2. Empirical Ablation Verdict: NOT DEMONSTRATED

Across all 240 controlled runs:

| Metric | PureBeam (Unguided) | NeuralBeam (Surrogate-Guided) | Empirical Comparison |
| :--- | :---: | :---: | :---: |
| **Heat Equation Exact Recovery** | **50.0%** | **50.0%** | Identical |
| **Linear Advection Exact Recovery** | **50.0%** | **50.0%** | Identical |
| **Viscous Burgers Exact Recovery** | **0.0%** | **0.0%** | Identical |
| **KdV Soliton Exact Recovery** | **0.0%** | **0.0%** | Identical |
| **Kuramoto-Sivashinsky Recovery** | **0.0%** | **0.0%** | Identical |
| **Mean Wall-Clock Time** | **0.0105s** | **0.1855s** | **17.7x Slower** |
| **Surrogate Training Overhead** | 0.0000s | 0.1730s | Irreducible compute penalty |

*Scientific Verdict:* Neural guidance provides **no statistically significant advantage** over unguided beam search on 1D PDE benchmarks ($p = 1.000$, McNemar's test), while imposing an 18x compute penalty.
