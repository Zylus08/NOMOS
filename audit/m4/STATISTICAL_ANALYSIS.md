# Project NOMOS — Milestone M4
## Rigorous Statistical Analysis & Paired Significance Testing

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 11 Statistical Audit  
**Date:** 2026-11-23  

---

### 1. Methodology & Hypothesis Formulation

To avoid degenerate tests (such as one-sample t-tests on identical distributions identified in M2.1 forensics), Milestone M4 employs non-parametric paired significance tests across 288 experimental observations:
1. **Wilcoxon Signed-Rank Test:** Evaluates paired differences in Support F1 score between Weak-Form Identification and Strong SINDy under identical physical systems, random seeds, and noise levels.
2. **McNemar's Exact Test:** Evaluates binary exact support recovery ($\text{F1} = 1.0$) between paired algorithms.
3. **Primary Hypothesis Test:**
   $H_0$: Active Disagreement-Driven experiment selection achieves equal or lower exact recovery compared to fixed experimental design.  
   $H_1$: Active Disagreement-Driven experiment selection achieves strictly superior exact recovery under limited observation regimes.

---

### 2. Paired Statistical Comparison Results

#### Comparison 1: WSINDy vs Strong SINDy (Noise Robustness across $\eta \in [0.01, 0.10]$)
- **Sample Size:** $N = 54$ matched system-seed-noise pairs.
- **Mean Support F1 Score:**
  - Strong SINDy: $0.342 \pm 0.285$
  - WSINDy: $0.887 \pm 0.142$
- **Wilcoxon Signed-Rank Test Statistic:** $W = 12.0, \quad p = 2.14 \times 10^{-9}$
- **Significance:** $p < 0.001$. Reject $H_0$. Weak-form integral identification is statistically significantly superior to strong-form differentiation under noisy observations.

#### Comparison 2: Active Identifiability vs Fixed Design (Identifiability Degeneracy)
- **Sample Size:** $N = 36$ matched trials across KdV and Gray-Scott regimes.
- **McNemar's Contingency Matrix:**
  - Both Recovered: 12
  - Active Only Recovered: 22
  - Fixed Only Recovered: 0
  - Neither Recovered: 2
- **McNemar's Test Statistic:** $\chi^2 = 20.045, \quad p = 7.56 \times 10^{-6}$
- **Significance:** $p < 0.001$. Reject $H_0$. Disagreement-driven experiment selection statistically significantly improves structural identifiability compared with fixed experimental design.
