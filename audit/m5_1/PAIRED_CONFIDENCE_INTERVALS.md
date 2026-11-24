# Project NOMOS — Milestone M5.1
## Rigorous Paired Confidence Intervals for Difference in Recovery Rates

**Review Role:** Independent Statistical Auditor  
**Auditor / Git Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  

---

### 1. Methodology: Matched-Pairs Difference of Proportions

Treating matched-pair outcomes as independent binomial samples is statistically erroneous because it ignores within-pair covariance. For paired binary data with $n$ pairs and $2 \times 2$ table:
$$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$$
where $a$ is mutual success, $b$ is Active success only, $c$ is Comparator success only, and $d$ is mutual failure:
- **Sample Difference of Proportions:** $\hat{\delta} = \hat{p}_{\text{active}} - \hat{p}_{\text{comp}} = \frac{b - c}{n}$.
- **Paired Variance:**
  $$\text{Var}(\hat{\delta}) = \frac{(b + c) - (b - c)^2 / n}{n^2}$$
- **Wald Paired $95\%$ Confidence Interval:**
  $$\hat{\delta} \pm z_{0.975} \sqrt{\text{Var}(\hat{\delta})}$$
- **Newcombe Method 10 Interval:** Incorporates Wilson score single-proportion endpoints $(l_1, u_1)$ and $(l_2, u_2)$ with estimated inter-method correlation $\hat{\phi} = \frac{ad - bc}{\sqrt{(a+b)(c+d)(a+c)(b+d)}}$:
  $$\delta_{\text{lower}} = \hat{\delta} - \sqrt{(\hat{p}_1 - l_1)^2 + (u_2 - \hat{p}_2)^2 - 2 \hat{\phi} (\hat{p}_1 - l_1)(u_2 - \hat{p}_2)}$$
  $$\delta_{\text{upper}} = \hat{\delta} + \sqrt{(u_1 - \hat{p}_1)^2 + (\hat{p}_2 - l_2)^2 - 2 \hat{\phi} (u_1 - \hat{p}_1)(\hat{p}_2 - l_2)}$$

---

### 2. Empirical Paired Confidence Intervals

#### 1. Active (`greedy_disagreement`) vs Passive (`fixed`)
- **Sample Proportions:** $63.0\%$ vs $55.0\%$ ($n = 100$).
- **Observed Difference ($\hat{\delta}$):** $+8.00\%$ ($+0.0800$).
- **Contingency Table:** $a = 54, b = 9, c = 1, d = 36$.
- **Wald Paired Standard Error:** $\text{SE} = \frac{\sqrt{10 - 0.64}}{100} = 0.030594$ ($3.06\%$).
- **Wald Paired 95% CI:** **$[+2.00\%, +14.00\%]$** ($[0.020037, 0.139963]$).
- **Newcombe Method 10 95% CI:** **$[+2.01\%, +13.86\%]$** ($[0.020133, 0.138586]$).
- **Interpretation:** The lower confidence bound is strictly above zero ($> 2.01\%$), confirming a statistically significant advantage under matched-pair procedures.

#### 2. Active (`greedy_disagreement`) vs Stochastic (`random`)
- **Sample Proportions:** $63.0\%$ vs $46.0\%$ ($n = 100$).
- **Observed Difference ($\hat{\delta}$):** $+17.00\%$ ($+0.1700$).
- **Contingency Table:** $a = 45, b = 18, c = 1, d = 36$.
- **Wald Paired Standard Error:** $\text{SE} = \frac{\sqrt{19 - 2.89}}{100} = 0.040137$ ($4.01\%$).
- **Wald Paired 95% CI:** **$[+9.13\%, +24.87\%]$** ($[0.091332, 0.248668]$).
- **Newcombe Method 10 95% CI:** **$[+9.02\%, +24.49\%]$** ($[0.090222, 0.244850]$).
- **Interpretation:** Active experimentation yields between a $+9.02\%$ and $+24.49\%$ absolute improvement in recovery probability over random sampling with 95% confidence.

---

### 3. Summary of Matched-Pair Proportions

| Comparison | $\hat{p}_1$ | $\hat{p}_2$ | Diff ($\hat{\delta}$) | Wald 95% CI | Newcombe 95% CI | Null Hypothesis ($0 \in \text{CI}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Active vs Fixed** | 63.0% | 55.0% | **+8.00%** | $[+2.00\%, +14.00\%]$ | $[+2.01\%, +13.86\%]$ | **REJECTED** |
| **Active vs Random** | 63.0% | 46.0% | **+17.00%** | $[+9.13\%, +24.87\%]$ | $[+9.02\%, +24.49\%]$ | **REJECTED** |
