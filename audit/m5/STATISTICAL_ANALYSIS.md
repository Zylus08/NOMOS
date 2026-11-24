# Project NOMOS — Milestone M5
## Rigorous Statistical Analysis: Non-Parametric Hypothesis Testing & Paired Outcomes

**Principal Investigator / Git Identity:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Milestone:** M5 — Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery  

---

### 1. Statistical Methodology & Paired Design

To establish whether active experimentation provides a statistically significant advantage over baseline methods under strictly matched observation budgets ($B_{max} = 4$), we perform paired non-parametric statistical hypothesis testing on the 100 matched condition pairs (5 systems $\times$ 4 noise levels $\times$ 5 random seeds).

Because equation recovery is a binary categorical outcome ($1 = \text{Exact True Law Recovered}, 0 = \text{Failed or Incomplete}$), standard continuous metrics (like paired $t$-tests) are invalid. We employ:
1. **McNemar's Test with Edwards' Continuity Correction:** Evaluates discordant pairs in paired binary outcomes.
2. **Exact Binomial Test:** Computes exact two-tailed and one-tailed $p$-values on discordant pairs ($b$ vs $c$), guaranteeing exact significance without asymptotic Gaussian approximation.
3. **Wilcoxon Signed-Rank Test:** Evaluates trajectory query budgets (sample efficiency) between matched trials.

---

### 2. Paired Comparison: Active (`greedy_disagreement`) vs Passive (`fixed`)

#### $2 \times 2$ Paired Contingency Table
The 100 matched trials cross-tabulate as follows:

| Active \ Fixed | Fixed Success ($1$) | Fixed Failure ($0$) | Total |
| :--- | :---: | :---: | :---: |
| **Active Success ($1$)** | $a = 54$ | $b = 9$ | 63 |
| **Active Failure ($0$)** | $c = 1$ | $d = 36$ | 37 |
| **Total** | 55 | 45 | **100** |

#### Discordant Pair Analysis
- **Active succeeds, Fixed fails ($b$):** 9 trials
- **Fixed succeeds, Active fails ($c$):** 1 trial
- **Net Active Advantage ($b - c$):** $+8$ trials

#### Hypothesis Test Statistics
$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c} = \frac{(|9 - 1| - 1)^2}{9 + 1} = \frac{7^2}{10} = 4.9000$$

- **McNemar Statistic:** $\chi^2 = 4.9000$ (degrees of freedom $= 1$)
- **Asymptotic $p$-value:** $p = 0.02686$ ($< 0.05$)
- **Exact Binomial Test ($n = 10, k = 9, p_0 = 0.5$):**
  $$p_{\text{exact}} = \sum_{k=9}^{10} \binom{10}{k} (0.5)^{10} = \frac{10 + 1}{1024} = 0.010742$$
- **Significance Conclusion:** **REJECT $H_0$ ($p = 0.0107 < 0.05$)**. Active experimentation provides a statistically significant improvement in governing-law recovery over fixed passive observation schedules.

---

### 3. Paired Comparison: Active (`greedy_disagreement`) vs Stochastic (`random`)

#### $2 \times 2$ Paired Contingency Table
The 100 matched trials cross-tabulate as follows:

| Active \ Random | Random Success ($1$) | Random Failure ($0$) | Total |
| :--- | :---: | :---: | :---: |
| **Active Success ($1$)** | $a = 45$ | $b = 18$ | 63 |
| **Active Failure ($0$)** | $c = 1$ | $d = 36$ | 37 |
| **Total** | 46 | 54 | **100** |

#### Discordant Pair Analysis
- **Active succeeds, Random fails ($b$):** 18 trials
- **Random succeeds, Active fails ($c$):** 1 trial
- **Net Active Advantage ($b - c$):** $+17$ trials

#### Hypothesis Test Statistics
$$\chi^2 = \frac{(|18 - 1| - 1)^2}{18 + 1} = \frac{16^2}{19} = \frac{256}{19} = 13.4737$$

- **McNemar Statistic:** $\chi^2 = 13.4737$ (degrees of freedom $= 1$)
- **Asymptotic $p$-value:** $p = 0.000242$ ($< 10^{-3}$)
- **Exact Binomial Test ($n = 19, k = 18, p_0 = 0.5$):**
  $$p_{\text{exact}} = \frac{19 + 1}{2^{19}} = \frac{20}{524288} = 0.00003815$$
- **Significance Conclusion:** **REJECT $H_0$ ($p = 0.000038 < 10^{-4}$)**. Active experimentation provides a decisive, highly statistically significant advantage over random sampling.

---

### 4. Sample Efficiency & Query Budget Analysis

We test the hypothesis that active experimentation requires fewer trajectory queries than passive schedules before concluding identification:
- **Active Mean Queries:** $2.10 \pm 0.36$
- **Fixed Mean Queries:** $2.28 \pm 0.60$
- **Wilcoxon Signed-Rank Test Statistic:** $W = 29.5$
- **Wilcoxon $p$-value:** $p = 0.020224$ ($< 0.05$)

**Conclusion:** Active experiment selection reaches conclusive identification in statistically significantly fewer trajectory observations than passive schedules ($p = 0.0202$).
