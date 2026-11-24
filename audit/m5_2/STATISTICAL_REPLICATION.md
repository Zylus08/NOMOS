# Project NOMOS — Milestone M5.2
## Statistical Replication, Multiplicity Family Audit, and Exact Paired Inference

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Audit Target:** Milestone M5.1 Baseline & `paper/main.tex` Claims P-05, P-06  
**Audited Datasets:** `audit/m5/RAW_EPISODES.csv`, `audit/m5_1/CORRECTED_PAIRED_OUTCOMES.csv`  

---

### 1. Executive Summary

Milestone M5.1 corrected several historical statistical reporting errors, establishing a paired testing framework across 100 matched scenario trials (5 physical systems $\times$ 4 noise regimes $\times$ 5 random seeds). The M5.2 audit independently re-executed the full statistical pipeline, recomputing exact contingency counts, two-sided binomial tests, multiple testing adjustments across pre-specified families, and paired difference score intervals.

The audit confirms:
1. **Active vs. Fixed Schedule:** $b = 9, c = 1$ out of $n = 100$ matched pairs. The exact two-sided binomial $p$-value is **$p = 0.0215$**.
2. **Active vs. Random Selection:** $b = 18, c = 1$ out of $n = 100$ matched pairs. The exact two-sided binomial $p$-value is **$p = 7.63 \times 10^{-5}$**.
3. **Multiplicity Control:**
   - Under the primary confirmatory family $m = 2$ (Active vs. Fixed, Active vs. Random), Holm-adjusted $p$-values are **$p = 0.0215$** and **$p = 0.00015$**, retaining formal statistical significance at $\alpha = 0.05$.
   - Under an expanded family $m = 4$ encompassing all evaluated comparators, the Holm-adjusted comparison against Fixed yields **$p = 0.0645$**, crossing the marginal significance threshold.
4. **Newcombe Method 10 Paired Score Intervals:**
   - Active vs. Fixed: $\hat{\delta} = +8.00\%$, $95\%$ CI: $[+1.64\%, +13.77\%]$.
   - Active vs. Random: $\hat{\delta} = +17.00\%$, $95\%$ CI: $[+8.57\%, +24.17\%]$.

---

### 2. Paired Contingency Tables and Exact Tests

#### 2.1 Active (`greedy_disagreement`) vs. Passive (`fixed`)
Across the $n = 100$ matched conditions:
- Both Succeeded ($a$): **54**
- Active Succeeded, Fixed Failed ($b$): **9**
- Fixed Succeeded, Active Failed ($c$): **1**
- Both Failed ($d$): **36**
- Total Discordant Pairs ($n_{\text{disc}} = b + c$): **10**

Under the sharp paired null hypothesis $H_0: p = 0.5$ (no directional advantage):
$$P(X \ge 9 \mid n_{\text{disc}}=10, p=0.5) = \sum_{k=9}^{10} \binom{10}{k} 0.5^{10} = \frac{11}{1024} \approx 0.01074$$
Two-sided exact binomial $p$-value:
$$p = 2 \times 0.01074 = \mathbf{0.02148} \quad (< 0.05)$$

#### 2.2 Active (`greedy_disagreement`) vs. Passive (`random`)
- Both Succeeded ($a$): **45**
- Active Succeeded, Random Failed ($b$): **18**
- Random Succeeded, Active Failed ($c$): **1**
- Both Failed ($d$): **36**
- Total Discordant Pairs ($n_{\text{disc}} = b + c$): **19**

Under $H_0: p = 0.5$:
$$P(X \ge 18 \mid n_{\text{disc}}=19, p=0.5) = \frac{20}{524288} \approx 0.00003815$$
Two-sided exact binomial $p$-value:
$$p = 2 \times 0.00003815 = \mathbf{0.0000763} \quad (< 0.001)$$

---

### 3. Multiplicity Adjustments Across Pre-Specified Families

| Multiplicity Family | Comparison | Raw Two-Sided $p$ | Holm Multiplier | Adjusted $p$ | Significant ($\alpha=0.05$) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Family 1: Primary Confirmatory ($m=2$)** | Active vs. Random | $0.000076$ | 2 | **$0.00015$** | **YES** |
| | Active vs. Fixed | $0.0215$ | 1 | **$0.0215$** | **YES** |
| **Family 2: Comprehensive Strategy ($m=4$)** | Active vs. Uncertainty | $< 10^{-12}$ | 4 | $< 10^{-11}$ | **YES** |
| | Active vs. Random | $0.000076$ | 3 | **$0.00023$** | **YES** |
| | Active vs. Fixed | $0.0215$ | 2 | **$0.0645$** | **BORDERLINE** |
| | Active vs. Cost-Norm | $0.6250$ | 1 | $0.6250$ | NO |

**Statistical Takeaway:**  
When pre-registering the primary hypothesis family as the two principal passive baselines (Sequential Fixed and Uniform Random), the directional superiority of active experiment selection survives step-down Holm–Bonferroni multiplicity control. However, if the exploratory family is broadened to all four alternative heuristics, the $+8\%$ margin over fixed schedules becomes marginally non-significant ($p = 0.0645$).

---

### 4. System-Stratified Decomposition and KdV Leverage

A critical forensic finding from the disaggregated data is that discordant pairs are not uniformly distributed across physical dynamics:

| Physical System | Matched Pairs | Active Rec. | Fixed Rec. | Discordant $b$ | Discordant $c$ | Net Gain ($b - c$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **FitzHugh–Nagumo 2D** | 20 | 100.0% (20/20) | 100.0% (20/20) | 0 | 0 | 0 (Ceiling) |
| **Gray–Scott 2D** | 20 | 85.0% (17/20) | 75.0% (15/20) | 2 | 0 | +2 |
| **KdV Equation** | 20 | 55.0% (11/20) | 30.0% (6/20) | **5** | **0** | **+5 (Dispersive)** |
| **Navier–Stokes 2D** | 20 | 40.0% (8/20) | 40.0% (8/20) | 1 | 1 | 0 (Turbulent floor) |
| **Viscous Burgers** | 20 | 35.0% (7/20) | 30.0% (6/20) | 1 | 0 | +1 |
| **Total** | **100** | **63.0%** | **55.0%** | **9** | **1** | **+8** |

#### Forensic Discovery:
- **55.6% of all discordant wins ($5 / 9$) originate from the KdV equation.**
- In FitzHugh–Nagumo, both active and fixed reach 100% recovery (ceiling effect).
- In Navier–Stokes, both reach 40% recovery (vorticity noise floor).
- In KdV, the single-soliton initial condition collapses nonlinear steepening and 3rd-order dispersion onto linear advection ($-6 u u_x - u_{xxx} \equiv -c u_x$). Fixed schedules get stuck on consecutive solitary waves, whereas active selection immediately queries a multi-frequency wave packet, breaking the degeneracy.
- If KdV is excluded from the sample, the discordant counts collapse to $b = 4, c = 1$ across 80 pairs, yielding an exact two-sided $p = 0.375$ (non-significant).
- **Manuscript Correction Required:** The paper must transparently state that the $+8\%$ paired advantage over fixed schedules is driven predominantly by dispersive wave mechanics breaking solitary-wave rank deficiency, rather than a universal uniform gain across all PDE classes.
