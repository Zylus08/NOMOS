# Project NOMOS — Milestone M5.1
## Independent Statistical Audit & Multiplicity Corrections

**Review Role:** Independent Statistical Auditor & Non-Parametric Inference Specialist  
**Auditor / Git Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Baseline Document Audited:** `audit/m5/STATISTICAL_ANALYSIS.md`  

---

### 1. Executive Summary of Statistical Audit

In Milestone M5, `audit/m5/STATISTICAL_ANALYSIS.md` reported:
- Active vs Fixed: One-sided exact binomial $p = 0.010742$.
- Active vs Random: One-sided exact binomial $p = 0.00003815$.

**Audit Evaluation:**
1. **One-Sided vs Two-Sided Testing:** In confirmatory research and publication-oriented peer review, a two-sided test is standard unless a directional hypothesis was pre-registered prior to data collection. Reporting only one-sided $p$-values inflates the apparent significance level by a factor of 2.
2. **Multiplicity Family & FWER Control:** Two primary comparisons were reported (Active vs Fixed and Active vs Random). Family-Wise Error Rate (FWER) must be controlled via the Holm-Bonferroni step-down procedure.
3. **Exact Binomial Calculations Verified:**
   - Active vs Fixed ($n_{disc} = 10, b = 9, c = 1$):
     - One-sided exact $p$: $0.0107421875$
     - Two-sided exact $p$: $0.0214843750$
   - Active vs Random ($n_{disc} = 19, b = 18, c = 1$):
     - One-sided exact $p$: $0.0000381470$
     - Two-sided exact $p$: $0.0000762939$

Both comparisons remain statistically significant under two-sided testing and under Holm multiplicity correction at the nominal $\alpha = 0.05$ level.

---

### 2. Multiplicity Correction: Holm-Bonferroni Procedure

Let $m = 2$ be the primary confirmatory hypotheses:
- $H_{0,1}$: Active and Random have equal marginal probability of exact recovery.
- $H_{0,2}$: Active and Fixed have equal marginal probability of exact recovery.

#### Two-Sided Raw $p$-Values in Ascending Order:
1. $p_{(1)} = 0.000076294$ (Active vs Random)
2. $p_{(2)} = 0.021484375$ (Active vs Fixed)

#### Step-Down Testing:
1. **Step 1 ($k = 1$):**
   Compare $p_{(1)}$ to $\frac{\alpha}{m - 1 + 1} = \frac{0.05}{2} = 0.0250$.
   $$0.000076294 \le 0.0250 \implies \mathbf{REJECT\ } H_{0,1}$$
   Holm-adjusted $p$-value: $p_{adj,(1)} = 2 \times 0.000076294 = \mathbf{0.00015259} < 0.05$.

2. **Step 2 ($k = 2$):**
   Compare $p_{(2)}$ to $\frac{\alpha}{m - 2 + 1} = \frac{0.05}{1} = 0.0500$.
   $$0.021484375 \le 0.0500 \implies \mathbf{REJECT\ } H_{0,2}$$
   Holm-adjusted $p$-value: $p_{adj,(2)} = 1 \times 0.021484375 = \mathbf{0.02148438} < 0.05$.

**Conclusion:** Both primary confirmatory comparisons survive Holm-Bonferroni correction with statistical significance.

---

### 3. Expansion to Larger Multiplicity Family ($m = 4$)

If the multiplicity family is expanded to encompass all 4 comparator strategies evaluated against Active (`greedy_disagreement`):
1. Active vs Uncertainty-Aware: Discordant pairs $b = 43, c = 0 \implies p < 10^{-12}$.
2. Active vs Random: Two-sided $p = 0.0000763$.
3. Active vs Fixed: Two-sided $p = 0.0214844$.
4. Active vs Cost-Normalized: Recovery rates $63.0\%$ vs $61.0\%$. Discordant pairs $b = 3, c = 1 \implies n_{disc} = 4, p = 0.6250$.

Under Holm correction for $m = 4$:
- Comparison 1 (vs Uncertainty-Aware): $p_{adj} < 10^{-11} < 0.05$ (**REJECT $H_0$**)
- Comparison 2 (vs Random): $p_{adj} = 3 \times 0.0000763 = 0.000229 < 0.05$ (**REJECT $H_0$**)
- Comparison 3 (vs Fixed): $p_{adj} = 2 \times 0.0214844 = 0.042969 < 0.05$ (**REJECT $H_0$**)
- Comparison 4 (vs Cost-Normalized): $p_{adj} = 1 \times 0.6250 = 0.6250 > 0.05$ (**FAIL TO REJECT $H_0$**)

**Insight:** Active greedy disagreement and cost-normalized active disagreement are statistically indistinguishable ($p = 0.625$), while both significantly outperform passive fixed schedules and random exploration.
