# PROJECT NOMOS — MILESTONE M5.3.1 AUDIT REPORT
## Deliverable 7: Independent Statistical Replication & Hypothesis Testing

**Date:** 2026-11-25  
**Auditor:** Independent Scientific Audit Commission & Statistical Replication Group  
**Commit Baseline:** `e401fa836c1a7c98313b663d7f6a3175f24448ce`  
**Dataset:** `audit/m5_3_1/CORRECTED_EPISODES.csv` & `CORRECTED_PAIRED_OUTCOMES.csv`  

---

### Executive Summary

This deliverable provides the authoritative statistical audit and replication of Project NOMOS under the reconciled hard-budget protocol ($B \le 4$ trajectory queries) and zero-leakage SHA-256 blinding contract. 

All hypothesis tests have been computed from raw, individual episode-level records across $N = 100$ matched pairs (5 physical systems $\times$ 4 noise levels $\times$ 5 random seeds). All p-values are reported to full IEEE 754 float64 machine precision alongside rounded values.

#### Central Statistical Finding:
1. **Active vs. Fixed Sequential Schedule:** Active acquisition demonstrates a statistically significant improvement in strict Tier 1 recovery over fixed sequential querying ($p = 0.00014495849609375 \approx 1.45 \times 10^{-4}$).
2. **Active vs. Uniform Random Acquisition:** Active acquisition shows **no statistically significant improvement** over uniform random acquisition ($p = 0.14599609375 \approx 0.146$). The null hypothesis cannot be rejected at any standard significance level ($\alpha = 0.05, 0.01$).

---

### 1. Classification of Recovery Tiers

To ensure complete scientific transparency, discovery outcomes are stratified into four rigorous tiers:

| Tier | Designation | Formal Definition & Acceptance Criteria |
|:---:|:---|:---|
| **Tier 1** | **Strict Exact Recovery** | 1. Exact mathematical operator support recovered (100% precision, 100% recall against ground truth).<br>2. Zero distractor terms from the overcomplete candidate library.<br>3. Continuous parameter estimation error strictly $\le 5\%$ relative error across all active terms: $\max_i |\hat{\theta}_i - \theta_i^*| / |\theta_i^*| \le 0.05$. |
| **Tier 2** | **Support Recovery** | Correct differential operators identified, but parameter estimation error exceeds $5\%$ due to noise corruption, partial collinearity, or suboptimal gradient conditioning. |
| **Tier 3** | **Distractor Identification** | True physical operators identified, but model includes one or more non-zero distractor terms from the candidate library. |
| **Tier 6** | **Failed / Non-Identifiable** | Search converged to incorrect physical operators, failed identifiability audits, or exhausted experimental budget without resolving competing models. |

---

### 2. Paired Comparison 1: Active Acquisition vs. Fixed Schedule

- **Hypothesis:**
  - $H_0$: The marginal probability of strict Tier 1 recovery under greedy disagreement active learning equals that under a fixed sequential schedule ($p_{\text{active}} = p_{\text{fixed}}$).
  - $H_1$: The recovery probabilities differ ($p_{\text{active}} \ne p_{\text{fixed}}$).
- **Sample Size:** $N = 100$ matched pairs (identical physical systems, noise levels, and numerical seeds).

#### 2x2 Paired Contingency Table:
$$\begin{array}{c|cc|c}
& \text{Fixed: Success (Tier 1)} & \text{Fixed: Failure (Non-Tier 1)} & \text{Total Active} \\
\hline
\text{Active: Success (Tier 1)} & n_{11} = 28 & n_{10} = 17 & 45 \\
\text{Active: Failure (Non-Tier 1)} & n_{01} = 1 & n_{00} = 54 & 55 \\
\hline
\text{Total Fixed} & 29 & 71 & N = 100
\end{array}$$

#### Marginal Proportions:
- $\hat{p}_{\text{active}} = \frac{28 + 17}{100} = 0.4500$ (45.00%)
- $\hat{p}_{\text{fixed}} = \frac{28 + 1}{100} = 0.2900$ (29.00%)
- Paired Risk Difference: $\hat{d} = \hat{p}_{\text{active}} - \hat{p}_{\text{fixed}} = \frac{17 - 1}{100} = +0.1600$ (+16.00 percentage points).

#### Exact McNemar Test:
The test statistic depends exclusively on the discordant pairs $b = n_{10} = 17$ and $c = n_{01} = 1$.  
Total discordant pairs $n_d = b + c = 18$.  
Under $H_0$, $b \sim \text{Binomial}(18, 0.5)$.

The exact two-sided p-value is:
$$p = 2 \times \sum_{k=0}^{\min(b, c)} \binom{n_d}{k} (0.5)^{n_d} = 2 \times \left[\binom{18}{0} + \binom{18}{1}\right] \times \left(\frac{1}{2}\right)^{18}$$
$$p = 2 \times [1 + 18] \times \frac{1}{262144} = \frac{38}{262144} = \frac{19}{131072}$$

**Full Precision Value:**
$$p = 0.00014495849609375$$
$$\text{Rounded Scientific Notation: } p \approx 1.45 \times 10^{-4}$$

#### Newcombe Score Paired Confidence Interval:
Wilson score intervals for marginal proportions:
- $\hat{p}_{\text{active}} = 0.45 \implies [l_1, u_1] = [0.3562, 0.5477]$
- $\hat{p}_{\text{fixed}} = 0.29 \implies [l_2, u_2] = [0.2096, 0.3857]$
- Paired correlation: $\phi = +0.6620$

Applying Newcombe's method 10 for paired proportions:
$$\text{95\% CI for } (\hat{p}_{\text{active}} - \hat{p}_{\text{fixed}}) = [\mathbf{+0.0825}, \mathbf{+0.2338}]$$
The 95% confidence interval is strictly positive and bounded well away from zero (+8.25% to +23.38%).

---

### 3. Paired Comparison 2: Active Acquisition vs. Random Acquisition

- **Hypothesis:**
  - $H_0$: The marginal probability of strict Tier 1 recovery under greedy disagreement active learning equals that under uniform random experiment selection ($p_{\text{active}} = p_{\text{random}}$).
  - $H_1$: The recovery probabilities differ ($p_{\text{active}} \ne p_{\text{random}}$).
- **Sample Size:** $N = 100$ matched pairs.

#### 2x2 Paired Contingency Table:
$$\begin{array}{c|cc|c}
& \text{Random: Success (Tier 1)} & \text{Random: Failure (Non-Tier 1)} & \text{Total Active} \\
\hline
\text{Active: Success (Tier 1)} & n_{11} = 36 & n_{10} = 9 & 45 \\
\text{Active: Failure (Non-Tier 1)} & n_{01} = 3 & n_{00} = 52 & 55 \\
\hline
\text{Total Random} & 39 & 61 & N = 100
\end{array}$$

#### Marginal Proportions:
- $\hat{p}_{\text{active}} = \frac{36 + 9}{100} = 0.4500$ (45.00%)
- $\hat{p}_{\text{random}} = \frac{36 + 3}{100} = 0.3900$ (39.00%)
- Paired Risk Difference: $\hat{d} = \hat{p}_{\text{active}} - \hat{p}_{\text{random}} = \frac{9 - 3}{100} = +0.0600$ (+6.00 percentage points).

#### Exact McNemar Test:
Discordant pairs: $b = n_{10} = 9$, $c = n_{01} = 3$.  
Total discordant pairs: $n_d = b + c = 12$.  
Under $H_0$, $b \sim \text{Binomial}(12, 0.5)$.

The exact two-sided p-value is:
$$p = 2 \times \sum_{k=0}^{3} \binom{12}{k} (0.5)^{12} = 2 \times [1 + 12 + 66 + 220] \times \frac{1}{4096}$$
$$p = 2 \times 299 \times \frac{1}{4096} = \frac{598}{4096} = \frac{299}{2048}$$

**Full Precision Value:**
$$p = 0.14599609375$$
$$\text{Rounded: } p \approx 0.146$$

#### Newcombe Score Paired Confidence Interval:
- $\hat{p}_{\text{random}} = 0.39 \implies [l_2, u_2] = [0.3003, 0.4878]$
- Paired correlation: $\phi = +0.7412$

Applying Newcombe's method 10:
$$\text{95\% CI for } (\hat{p}_{\text{active}} - \hat{p}_{\text{random}}) = [\mathbf{-0.0215}, \mathbf{+0.1396}]$$
The 95% confidence interval spans zero (-2.15% to +13.96%).

#### Statistical Decision:
Because $p = 0.1460 > 0.05$, **we fail to reject the null hypothesis.** The observed difference between active and random acquisition cannot be distinguished from chance variation.

---

### 4. Family-Wise Error Rate (FWER) Control

When conducting multiple hypothesis tests across the benchmark suite, family-wise error rate control is mandatory:

Applying the step-down **Holm–Bonferroni procedure** to the two primary comparisons:
1. Rank p-values in ascending order:
   - Rank 1 (Active vs. Fixed): $p_{(1)} = 0.000145$
   - Rank 2 (Active vs. Random): $p_{(2)} = 0.145996$
2. Step 1: Compare $p_{(1)}$ against $\alpha / (2 - 1 + 1) = 0.05 / 2 = 0.025$.  
   Since $0.000145 < 0.025$, **Reject $H_{0, \text{fixed}}$**.
3. Step 2: Compare $p_{(2)}$ against $\alpha / (2 - 2 + 1) = 0.05 / 1 = 0.050$.  
   Since $0.145996 > 0.050$, **Fail to reject $H_{0, \text{random}}$**.

Conclusion: Active acquisition maintains statistically significant superiority over a fixed schedule under strict FWER control, but remains non-significant compared to random acquisition.

---

### 5. Research Integrity Directives for Publications

To comply with research integrity standards:
1. **Never claim statistical superiority over random acquisition:** Any manuscript statement claiming that active learning outperformed random acquisition must be revised to state explicitly that the difference was not statistically significant ($p = 0.146$).
2. **Approved Manuscript Claim Language:**  
   *"Disagreement-guided active acquisition improved strict governing-law recovery relative to the tested sequential fixed schedule under specified blinded simulation benchmarks."*
3. **Include Full machine precision numbers in supplementary materials:** All tables and data appendices must report $n_{11}=28, n_{10}=17, n_{01}=1, n_{00}=54, p=0.000145$ and $n_{11}=36, n_{10}=9, n_{01}=3, n_{00}=52, p=0.146$.
