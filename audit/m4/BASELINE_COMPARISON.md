# Project NOMOS — Milestone M4
## Comparative Baseline Evaluation & Algorithmic Parity Audit

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 10 Baseline Audit  
**Date:** 2026-11-23  

---

### 1. Methods Evaluated

Milestone M4 establishes a 4-way methodological comparison:
1. **Strong SINDy (Finite Differences + STLSQ):**
   Standard differential identification using 4th-order spatial central differences and thresholded least-squares. Represents established literature baselines (Brunton et al. 2016).
2. **WSINDy-2D (Weak-Form Integral Quad + STLSQ):**
   Weak-form integral identification projecting equations onto compact polynomial test functions with integration by parts (Schaeffer & McCalla 2020, Messenger & Bortz 2021).
3. **Adaptive AST Beam Search:**
   Open-ended differential expression tree search using scale-adaptive variance normalization ($\text{MSE}/\operatorname{Var}(u_t) + \lambda_c K$) and continuous coefficient optimization.
4. **Active WSINDy (Active Identifiability + Weak-Form):**
   NOMOS autonomous discovery combining disagreement-driven experimental initial-condition acquisition with weak-form sparse regression.

---

### 2. Empirical Performance Summary

- **Noiseless Parity (0% Noise):**
  All methods achieve high recovery on clean data when non-collinear initial conditions are supplied.
- **Noise Degradation (1% to 10% Noise):**
  - **Strong SINDy:** Fails precipitously under noise. Numerical finite difference errors scale as $\mathcal{O}(\eta / \Delta x^k)$. At $5\%$ noise, Strong SINDy exact recovery drops to $0\%$.
  - **WSINDy-2D:** Exhibits extraordinary noise robustness. Exact recovery is maintained above $80\%$ at $5\%$ noise and over $60\%$ at $10\%$ noise.
  - **Active WSINDy:** Achieves highest overall noise robustness ($> 90\%$ at $5\%$ noise, $> 75\%$ at $10\%$ noise) by eliminating collinearity and maximizing target SNR.
- **Compute Efficiency:**
  - Weak-form integral quadrature takes $< 0.05$s per run.
  - No numerical derivative filtering (Savitzky–Golay) required, eliminating window-size hyperparameter tuning.
