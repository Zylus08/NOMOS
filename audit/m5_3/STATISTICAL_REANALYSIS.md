# Project NOMOS — Milestone M5.3
# Formal Statistical Reanalysis & Paired Hypothesis Testing

**Date:** 2026-11-25  
**Auditor:** Statistical Inference Reviewer & Integrity Auditor  
**Primary Dataset:** [`audit/m5_3/BLIND_PAIRED_OUTCOMES.csv`](file:///e:/NOMOS/audit/m5_3/BLIND_PAIRED_OUTCOMES.csv) (100 matched pairs)

---

## 1. Paired Benchmark Contingency Tables

Every test condition (System $\times$ Noise Level $\times$ Random Seed) was evaluated as a **matched pair**, sharing identical initial conditions, noise realization seeds, and maximum budgets.

Evaluation metric: **Tier 1 Strict Exact Support Recovery** ($\operatorname{supp}(\hat{\xi}) = \operatorname{supp}(\xi^*) \wedge \text{error} \le 10\%$).

### Table 1A: Greedy Disagreement vs Fixed Sequential Baseline (N = 100 Matched Pairs)

| | Fixed: Tier 1 (Success) | Fixed: Non-Tier 1 (Failure) | Total Greedy |
| :--- | :---: | :---: | :---: |
| **Greedy: Tier 1 (Success)** | $n_{11} = 28$ | $n_{10} = 17$ (Active Win) | **45** |
| **Greedy: Non-Tier 1 (Failure)** | $n_{01} = 1$ (Passive Win) | $n_{00} = 54$ | **55** |
| **Total Fixed** | **29** | **71** | **100** |

- **Paired Discordant Pairs**: $b = n_{10} = 17$, $c = n_{01} = 1$.
- **Difference in Proportions**: $\Delta = p_{\text{greedy}} - p_{\text{fixed}} = 45.0\% - 29.0\% = \mathbf{+16.0\%}$.
- **Paired 95% Score Confidence Interval**: **$[+8.3\%, +23.7\%]$** (strictly bounded away from 0).
- **Exact Two-Sided McNemar Test**:
  $$P(X \ge 17 \text{ or } X \le 1 \mid X \sim \operatorname{Binomial}(18, 0.5)) = \mathbf{1.45 \times 10^{-4}} \quad (p < 0.001)$$
- **Conclusion**: Greedy disagreement achieves a decisive, statistically certified improvement over fixed sequential experimentation under strict zero-leakage conditions.

---

### Table 1B: Greedy Disagreement vs Random Uniform Baseline (N = 100 Matched Pairs)

| | Random: Tier 1 (Success) | Random: Non-Tier 1 (Failure) | Total Greedy |
| :--- | :---: | :---: | :---: |
| **Greedy: Tier 1 (Success)** | $n_{11} = 36$ | $n_{10} = 9$ (Active Win) | **45** |
| **Greedy: Non-Tier 1 (Failure)** | $n_{01} = 3$ (Passive Win) | $n_{00} = 52$ | **55** |
| **Total Random** | **39** | **61** | **100** |

- **Paired Discordant Pairs**: $b = n_{10} = 9$, $c = n_{01} = 3$.
- **Difference in Proportions**: $\Delta = p_{\text{greedy}} - p_{\text{random}} = 45.0\% - 39.0\% = \mathbf{+6.0\%}$.
- **Paired 95% Score Confidence Interval**: **$[-0.7\%, +12.7\%]$**.
- **Exact Two-Sided McNemar Test**:
  $$P(X \ge 9 \text{ or } X \le 3 \mid X \sim \operatorname{Binomial}(12, 0.5)) = \mathbf{0.145996} \quad (p > 0.05)$$
- **Conclusion**: Active learning outperforms uniform random selection by $+6.0\%$, with 3x more discordant active wins (9 vs 3), but the difference does not cross the conventional significance threshold ($\alpha = 0.05$) when pooled across all noise levels due to small candidate pool size.

---

## 2. Multi-Hypothesis Correction (Holm–Bonferroni Family)

To guard against Family-Wise Error Rate (FWER) inflation across baseline comparisons:

| Hypothesis Test | Baseline Comparison | Raw $p$-value | Holm Rank ($k$) | Adjusted Significance Threshold $\alpha / (M - k + 1)$ | Holm-Adjusted $p$-value | Final Significance |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $H_1$ | Active vs Fixed Sequential | $1.45 \times 10^{-4}$ | 1 | $0.05 / 2 = 0.025$ | $\mathbf{2.90 \times 10^{-4}}$ | **REJECT $H_0$ (Significant)** |
| $H_2$ | Active vs Random Uniform | $0.146$ | 2 | $0.05 / 1 = 0.050$ | $\mathbf{0.146}$ | **FAIL TO REJECT $H_0$** |

---

## 3. Stratified Analysis by System & Noise

### Recovery by Physical System (N = 20 pairs per system)

| System | Greedy Active | Random Passive | Fixed Passive | Greedy vs Fixed ($p$) | Greedy vs Random ($p$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **KdV Equation** | **60.0%** (12/20) | 45.0% (9/20) | 0.0% (0/20) | $\mathbf{4.9 \times 10^{-4}}$ | 0.250 |
| **Viscous Burgers** | **35.0%** (7/20) | 35.0% (7/20) | 30.0% (6/20) | 1.000 | 1.000 |
| **Gray–Scott 2D** | **20.0%** (4/20) | 20.0% (4/20) | 20.0% (4/20) | 1.000 | 1.000 |
| **FitzHugh–Nagumo 2D** | **35.0%** (7/20) | 35.0% (7/20) | 35.0% (7/20) | 1.000 | 1.000 |
| **Navier–Stokes 2D** | **75.0%** (15/20) | 60.0% (12/20) | 60.0% (12/20) | 0.250 | 0.250 |

### Recovery by Noise Level (N = 25 pairs per noise level)

| Noise Level ($\sigma$) | Greedy Active | Random Passive | Fixed Passive | Greedy vs Fixed ($p$) |
| :---: | :---: | :---: | :---: | :---: |
| **0.0% (Clean)** | **96.0%** (24/25) | 88.0% (22/25) | 76.0% (19/25) | $\mathbf{0.062}$ |
| **1.0%** | **48.0%** (12/25) | 40.0% (10/25) | 32.0% (8/25) | $\mathbf{0.125}$ |
| **5.0%** | **32.0%** (8/25) | 24.0% (6/25) | 4.0% (1/25) | $\mathbf{0.016}$ |
| **10.0%** | **4.0%** (1/25) | 4.0% (1/25) | 4.0% (1/25) | 1.000 |

### Crucial Statistical Insight
- At $\sigma = 5.0\%$, Active achieves **32.0%** Tier 1 recovery while Fixed collapses to **4.0%** ($p = 0.016$). When noise makes discrimination difficult, active selection preserves identifiability where passive sequential polling completely breaks down.
- At $\sigma = 10.0\%$, sparse regression in weak form degrades across all methods, requiring enhanced denoising or lower thresholding.
