# Project NOMOS — Milestone M5.2
## Cluster-Robust Inference Stress Test & Small-Cluster GEE Bias Analysis

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target Manuscript Claim:** Claim P-05 (`paper/main.tex` lines 30, 208–221)  
**Evaluated Artifacts:** `audit/m5_1/PSEUDOREPLICATION_AUDIT.md`, `experiments/m5_2/audit_statistics_and_clusters.py`  

---

### 1. Executive Summary

Milestone M5.1 introduced a Generalized Estimating Equations (GEE) logit model clustered on physical systems to address concerns regarding pseudoreplication across random seeds. The manuscript claimed:
> *"A paired generalized estimating equations (GEE) analysis clustered on physical systems confirms the robustness of the active discovery advantage ($\beta_{\text{active}} = 0.7514 \pm 0.2771, z = 2.712, p = 0.0067$), yielding a certified odds ratio of 2.12 (95% CI: [1.23, 3.65])."*

The M5.2 red-team audit subjected this claim to a rigorous statistical stress test and concludes that **this asymptotic inferential claim is methodologically invalid and must be retracted or substantially qualified**:
1. **Severe Finite-Sample Sandwich Bias ($K=5$):** Clustered Huber–White / Liang–Zeger sandwich covariance estimators are valid strictly asymptotically as the number of independent clusters $K \to \infty$. A vast body of statistical literature (Cameron & Miller 2015; Mancl & DeRouen 2001; Kauermann & Carroll 2001) proves that with only $K = 5$ clusters, sandwich standard errors are downward-biased by up to $30\%\text{--}50\%$, severely inflating test statistics and leading to empirical Type I error rates of $20\%\text{--}50\%$ at nominal $\alpha = 0.05$.
2. **Re-estimation Under Controlled Specification:** Re-estimating the two-group Active vs. Fixed model controlling for noise level yields $\beta_{\text{active}} = 0.4119 \pm 0.2439$, $z = 1.6885$, and $p = 0.0913$ (Odds Ratio $1.51$, $95\%$ CI: $[0.94, 2.44]$). It does not achieve statistical significance at $\alpha = 0.05$.
3. **Leave-One-System-Out (LOSO) Instability:** When the KdV equation is omitted, the estimated active coefficient collapses to $\beta_{\text{active}} = 0.1919 \pm 0.1366$, $p = 0.1600$, $\text{OR} = 1.21$. The active effect is completely non-significant on the remaining four PDE families.
4. **Confirmatory Standard:** Confirmatory statistical evidence for NOMOS must rest strictly on the exact, finite-sample two-sided paired binomial tests across the 100 scenario conditions ($p = 0.0215$ vs. Fixed, $p = 0.00015$ vs. Random). The GEE model can only be reported as an exploratory descriptive summary within the tested sample.

---

### 2. Theoretical Breakdown: Why GEE Fails with $K=5$ Clusters

In the GEE formulation:
$$y_{ij} \sim \text{Bernoulli}(\mu_{ij}), \quad \text{logit}(\mu_{ij}) = \mathbf{x}_{ij}^T \boldsymbol{\beta}$$
where $i \in \{1, \dots, K\}$ indexes the physical PDE system ($K = 5$), and $j \in \{1, \dots, m_i\}$ indexes the experimental trials within each cluster ($m_i = 40$ for active + fixed).

The empirical sandwich variance estimator is given by:
$$\mathbf{V}_{\text{sandwich}} = \mathbf{M}_0^{-1} \left( \sum_{i=1}^K \mathbf{S}_i \mathbf{S}_i^T \right) \mathbf{M}_0^{-1}$$
where $\mathbf{M}_0 = \sum_{i=1}^K \mathbf{D}_i^T \mathbf{V}_i^{-1} \mathbf{D}_i$ is the model-based information matrix and $\mathbf{S}_i = \mathbf{D}_i^T \mathbf{V}_i^{-1} (\mathbf{y}_i - \boldsymbol{\mu}_i)$ is the cluster score vector.

#### Known Failure Modes at $K < 30$:
- **Downward Bias:** The cluster score cross-products $\mathbf{S}_i \mathbf{S}_i^T$ use estimated residuals $\mathbf{y}_i - \hat{\boldsymbol{\mu}}_i$ rather than true errors $\mathbf{y}_i - \boldsymbol{\mu}_i$. Because $\hat{\boldsymbol{\mu}}_i$ is fitted to the data, residuals are systematically smaller than errors, underestimating the variance.
- **Rank Deficiency:** The matrix $\sum_{i=1}^K \mathbf{S}_i \mathbf{S}_i^T$ is the sum of only $K=5$ rank-1 outer products. It has at most rank 5, leaving almost zero degrees of freedom to estimate covariance across multi-parameter vectors.
- **Normal Quantile Fallacy:** Evaluating $z = 2.712$ against the standard normal distribution $N(0, 1)$ assumes infinite clusters. Applying small-sample $t$-corrections with degrees of freedom $K - p = 5 - 3 = 2$ requires a critical threshold of $t_{0.975, 2} = 4.303$. The observed statistic $z = 2.712$ yields $p = 0.114$, completely failing to reject the null hypothesis.

---

### 3. Empirical Re-Estimation & Stress-Test Results

The re-estimation was executed using `statsmodels` GEE with an exchangeable correlation structure across the 200 episodes belonging to Active (`greedy_disagreement`) and Passive (`fixed`):

```python
gee_model = smf.gee(
    "exact_rec ~ is_active + noise_level",
    "system",
    df_gee,
    family=sm.families.Binomial(),
    cov_struct=sm.cov_struct.Exchangeable(),
)
```

#### Results Summary:
| Parameter | Coefficient ($\beta$) | Robust SE | Wald $z$ | $p$-value | Odds Ratio | 95% Confidence Interval |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Intercept** | $+0.7852$ | $0.4120$ | $1.9058$ | $0.0567$ | — | — |
| **Active Policy ($\mathbf{1}_{\text{Active}}$)** | **$+0.4119$** | **$0.2439$** | **$1.6885$** | **$0.0913$** | **$1.51$** | **$[0.94, 2.44]$** |
| **Noise Level ($\sigma$)** | $-7.8105$ | $2.1450$ | $-3.6412$ | $0.0003$ | — | — |

**Key Findings:**
1. Controlling for baseline difficulty and noise level, the Active effect is $+0.4119$, yielding an Odds Ratio of **$1.51$** (not $2.12$).
2. The robust standard error is $0.2439$, giving a $z$-statistic of $1.6885$ and $p = 0.0913$.
3. The $95\%$ confidence interval for the odds ratio spans $[0.9359, 2.4351]$, **which overlaps 1.000**.
4. Even under asymptotic assumptions, the claim that active experimentation provides a statistically significant cross-system advantage after controlling for noise fails to meet $\alpha = 0.05$.

---

### 4. Leave-One-System-Out (LOSO) Sensitivity Analysis

To test whether the active advantage generalizes uniformly or is anchored to specific physical mechanics, we sequentially dropped each of the 5 physical systems and re-fitted the GEE model:

| Dropped System | Retained Clusters ($K$) | Active $\beta$ | Robust SE | $p$-value | Odds Ratio | Significant at $\alpha=0.05$? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **None (Full Sample)** | 5 | $+0.4119$ | $0.2439$ | $0.0913$ | $1.51$ | NO |
| **Drop KdV Equation** | **4** | **$+0.1919$** | **$0.1366$** | **$0.1600$** | **$1.21$** | **NO** |
| **Drop Gray–Scott 2D** | 4 | $+0.3530$ | $0.2871$ | $0.2189$ | $1.42$ | NO |
| **Drop Viscous Burgers** | 4 | $+0.4846$ | $0.2992$ | $0.1053$ | $1.62$ | NO |
| **Drop Navier–Stokes 2D**| 4 | $+0.5193$ | $0.3147$ | $0.0989$ | $1.68$ | NO |
| **Drop FitzHugh–Nagumo** | 4 | $+0.5765$ | $0.3449$ | $0.0946$ | $1.78$ | NO |

#### Findings:
1. **Zero Significant Models:** In not a single leave-one-out configuration does the active effect achieve $p < 0.05$.
2. **KdV Leverage:** Dropping KdV cuts the active coefficient in half (from $0.41$ to $0.19$) and drops the odds ratio to $1.21$. This confirms Reviewer B and Reviewer C's finding that the active learning advantage is overwhelmingly concentrated in breaking solitary wave degeneracies in dispersive PDEs.

---

### 5. Final Scientific Audit Verdict

> **VERDICT: RETRACT ASYMPTOTIC GEE GENERALIZATION CLAIMS**  
> - Claim P-05 in `paper/main.tex` asserting that GEE confirms a generalizable $2.12\times$ odds ratio ($p=0.0067$) across physical systems is **scientifically defective**.
> - The manuscript will be amended to:
>   1. Retract the claim of certified generalizable odds ratios from the Abstract and Section 5.2.
>   2. Present the exact paired binomial tests ($b=9, c=1, p=0.0215$) as the sole primary confirmatory inference across the 100 scenario conditions.
>   3. Accurately report the small-cluster limitation ($K=5$) and present GEE strictly as an exploratory, descriptive within-sample analysis.
