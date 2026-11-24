# Project NOMOS: Manuscript Claims & Evidence Traceability Ledger

**Milestone:** NOMOS M5.2 — Pre-Submission Red-Team Review  
**Manuscript:** `paper/main.tex` (Milestone M5.1 Baseline)  
**Author / Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor:** Statistical Inference & Evidence Verification Specialist  

---

## 1. Traceability Mapping

| ID | Manuscript Location | Claim Statement | Evidence Source | Audited Value / Ground Truth | Verification Status | Auditor Objections & Action Required |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **P-01** | Abstract (line 30), Sec. 5.3 (line 227) | "Passive identification falsely converges to incomplete physical models in 43.9% to 53.1% of trials" | `audit/m5/RAW_EPISODES.csv`, `audit/m5_1/QUERY_EFFICIENCY_REANALYSIS.md` | Fixed: 43/98 (43.9%); Random: 52/98 (53.1%) of halting trials | **VERIFIED** | Accurate descriptive statistic across the 500 baseline runs. Clearly distinguish stopping trials from all trials. |
| **P-02** | Abstract (line 30), Sec. 5.1 (line 203), Table 1 | "Active experimentation achieves a paired discovery advantage of +8.00% over sequential schedules ($p = 0.0215$, Holm-adjusted)" | `audit/m5_1/CORRECTED_SUMMARY.csv`, `CORRECTED_PAIRED_OUTCOMES.csv` | Active: 63/100, Fixed: 55/100. $b=9, c=1$. Two-sided exact binomial $p = 0.021484$ | **VERIFIED** | Statistically exact on the 100 matched pairs. Family of confirmatory comparisons must be pre-specified. |
| **P-03** | Abstract (line 30), Sec. 5.1 (line 204), Table 1 | "+17.00% over uniform random querying ($p = 0.00015$, Holm-adjusted)" | `audit/m5_1/CORRECTED_SUMMARY.csv`, `CORRECTED_PAIRED_OUTCOMES.csv` | Active: 63/100, Random: 46/100. $b=18, c=1$. Exact $p = 0.000076$, Holm $p = 0.000153$ | **VERIFIED** | Highly statistically significant paired difference. |
| **P-04** | Abstract (line 30), Sec. 5.1, Table 1 | "Newcombe 95% CI: $[+2.01\%, +13.86\%]$ (vs Fixed) and $[+9.02\%, +24.49\%]$ (vs Random)" | `audit/m5_1/PAIRED_CONFIDENCE_INTERVALS.md` | Method 10 paired difference score interval | **VERIFIED** | Both intervals strictly exclude zero. Valid paired interval estimation. |
| **P-05** | Abstract (line 30), Sec. 5.2 (line 219) | "GEE with exchangeable clustering confirm a $2.12\times$ odds ratio improvement ($95\%$ CI: $[1.23, 3.65]$, $p = 0.0067$)" | `audit/m5_1/PSEUDOREPLICATION_AUDIT.md` | $\beta_{\text{active}} = 0.7514 \pm 0.2771, z=2.712, p=0.0067$ | **OVERSTATED / METHODOLOGICALLY FLAWED** | **FATAL OBJECTION:** GEE was clustered on only $K=5$ physical systems. Asymptotic sandwich covariance estimators are severely anti-conservative for $K < 30$. Must conduct leave-one-out sensitivity and retract cluster-robust generalization claims. |
| **P-06** | Abstract (line 30), Sec. 5.4 (line 234) | "Cutting conditional query budgets from 2.38 to 2.00 trajectories ($p = 0.0202$)" | `audit/m5_1/QUERY_EFFICIENCY_REANALYSIS.md` | Successful episodes: Active mean $= 2.000$, Fixed mean $= 2.382$. Wilcoxon $W=29.5, p=0.0202$ | **NEEDS QUALIFICATION** | All 63 successful active episodes used exactly 2 queries. Query 1 is the initial state; Query 2 is the first active query. This is a consequence of early stopping on Query 2. Must disclose selection bias. |
| **P-07** | Sec. 5.4 (line 238), Fig. 2 | "At budget $B=2$, Active achieves 63.0% recovery compared with Fixed 44.0% (+19.0% absolute advantage)" | `experiments/m5/run_m5_benchmarks.py`, cumulative recovery | Active: 63/100 at $B=2$; Fixed: 44/100 at $B=2$ | **VERIFIED** | Major empirical strength. Demonstrates early budget efficiency. |
| **P-08** | Sec. 5.5 (line 241) | "On 2D Brusselator, NOMOS achieved 50.0% exact multi-parameter recovery" | `audit/m5_1/STRONG_BASELINES.csv`, `HELD_OUT_BENCHMARKS.csv` | 10/20 runs recovered exact support `lap_u, u, u^2*v, 1` | **VERIFIED** | Demonstrates multi-parameter recovery in 2D reaction-diffusion. |
| **P-09** | Sec. 5.5 (line 241) | "On 4th-order Cahn–Hilliard, weak-form recovered dominant double-well flux $-0.9355 u_{xx} + 1.0085 (u^3)_{xx}$ with less than 1% parameter error, preserving mass conservation" | `audit/m5_1/HELD_OUT_BENCHMARKS.csv`, `nomos/pde/simulators/cahn_hilliard.py` | Ground truth: $-1.0 u_{xx} + 1.0 (u^3)_{xx} - 0.0025 u_{xxxx}$. Recovered: $-0.9355 u_{xx} + 1.0085 (u^3)_{xx}$ | **PARTIALLY OVERSTATED** | **CRITICAL DEFECT:** The 4th-order biharmonic term was omitted due to STLSQ thresholding ($\lambda=0.045 > 0.0025$). Claiming $<1\%$ parameter error applies only to the $(u^3)_{xx}$ coefficient, not the full 4th-order PDE. Must reclassify as Tier 3 Partial Support. |
| **P-10** | Sec. 3.3 (line 119) | "$\Delta\text{BIC}_{\text{eff}} \ge 10.0$ corresponds to decisive evidence on Kass--Raftery scale" | `audit/m5_1/BIC_AND_STOPPING_VALIDITY.md` | $N_{\text{eff}} \approx 86.5$ for KdV; $\Delta\text{BIC}_{\text{eff}} = 405.2 \gg 10$ | **VERIFIED WITH CAVEAT** | While $\Delta\text{BIC}_{\text{eff}}$ is decisive for KdV, approximate model weights $\tilde{w}_k$ must not be conflated with exact Bayesian posterior probabilities. |
| **P-11** | Sec. 1 (line 30), Title | Title: "Autonomous Discovery of Physical Governing Laws..." | Whole paper | Controller selects initial conditions from a pre-defined candidate pool | **OVERSTATED FRAMING** | The agent does not design arbitrary function shapes from unconstrained space; it ranks candidates from a discrete experiment pool. The title should reflect this narrower, defensible thesis. |

---

## 2. Summary of Auditor Directives for Paper Revision

1. **Retitle & Re-center:** Change title from unconstrained "Autonomous Discovery" to the narrower, defensible thesis:  
   *Disagreement-Guided Experimental Design for Reducing False Identification in Nonlinear Dynamical-System Discovery*.
2. **Retract GEE Cluster-Robust Significance:** Acknowledge that with only $K=5$ physical systems, cluster-robust standard errors cannot support definitive asymptotic inference across all unobserved dynamical systems. Center inference on the valid, exact matched-pair tests on the 100 empirical conditions.
3. **Correct Cahn-Hilliard Claims:** Explicitly state that Cahn-Hilliard was recovered to **Tier 3 (Dominant Support / Partial Structural Recovery)**, as the 4th-order hyperdiffusion term was sparsified out.
4. **Disclose Query 2 Forensics:** Explain why active recovery occurs on Query 2 (initial observation + 1 active query) and discuss selection bias when conditioning on successful episodes.
