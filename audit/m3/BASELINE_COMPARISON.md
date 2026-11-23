# Project NOMOS — Milestone M3
## Controlled Baseline Comparison Across 4 PDE Discovery Paradigms

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** F01–F06 (Baselines)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### Comparative Performance Matrix (240 Runs)

| Discovery Method | Mean Exact Support Rate | Mean Wall-Clock Time | Candidate Evaluations | Strengths | Limitations |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Strong SINDy** | 10.0% | **0.0046s** | 9 | Extremely fast; exact on noiseless data | Highly fragile to noise ($>1\%$) |
| **Weak SINDy (WSINDy)** | **20.0%** | 0.0265s | 8 | Exceptional noise robustness on nonlinear PDEs | Requires numerical quadrature |
| **Pure Beam Search** | 20.0% | 0.0105s | 35 | Open-ended search; recovers linear/parabolic PDEs | Bounded by combinatorial depth |
| **Neural Beam Search** | 20.0% | 0.1855s | 35 | Learned sensitivity priors | 18x compute overhead with zero recovery gain |
