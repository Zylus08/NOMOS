# Project NOMOS — Milestone M5.1
## Experimental Unit Forensic Audit & Pseudoreplication Analysis

**Review Role:** Independent Methodology & Experimental Design Auditor  
**Auditor / Git Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  

---

### 1. The Experimental Unit Dilemma in Scientific Discovery

A critical vulnerability in computational benchmarks is **pseudoreplication** (Hurlbert, 1984): treating non-independent observations as independent statistical trials.

In Milestone M5:
- 100 matched pairs were formed by crossing:
  $$\text{5 Physical Systems} \times \text{4 Noise Levels} \times \text{5 Random Seeds} = 100 \text{ Condition Scenarios}$$
- Each scenario was evaluated across 5 acquisition strategies ($100 \times 5 = 500$ episodes).

**Auditor Question:** Are these 100 matched pairs independent replications of the governing-law discovery process?

**Forensic Finding:**
1. **Physical Mechanism Dependency:** The 100 pairs are grouped into 5 distinct physical systems. Dynamics within the same system family (e.g., KdV across seeds 42–46) share the exact underlying equation, coordinate domain, and candidate library.
2. **Noise Regime Clustering:** Trials sharing the same noise level share common signal-to-noise ratios.
3. **True Replications vs Scenario Exploration:**
   - The genuine independent replication unit for *algorithm stability* is the **random seed** (different noise realizations and stochastic perturbations) within a fixed physical system.
   - The genuine independent replication unit for *scientific generality* is the **physical system family** ($N = 5$).
   - Therefore, the 100 scenarios represent 100 matched experimental challenges, **NOT 100 independent discoveries of novel physical laws**.

---

### 2. Stratified Analysis: Controlling for System Clustered Effects

When we disaggregate the paired outcomes across the 5 physical systems:

| Physical System | Pairs ($n$) | Active Recovery | Fixed Recovery | Discordant $b$ (Active) | Discordant $c$ (Fixed) | Net Advantage ($b - c$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **FitzHugh-Nagumo 2D** | 20 | 100.0% (20/20) | 100.0% (20/20) | 0 | 0 | 0 |
| **Gray-Scott 2D** | 20 | 85.0% (17/20) | 75.0% (15/20) | 2 | 0 | +2 |
| **KdV Equation** | 20 | 55.0% (11/20) | 30.0% (6/20) | 5 | 0 | **+5** |
| **Navier-Stokes 2D** | 20 | 40.0% (40/20) | 40.0% (8/20) | 1 | 1 | 0 |
| **Viscous Burgers** | 20 | 35.0% (7/20) | 30.0% (6/20) | 1 | 0 | +1 |
| **Total** | **100** | **63.0%** | **55.0%** | **9** | **1** | **+8** |

#### Key Insights:
1. **Source of the Active Advantage:** The primary active advantage is heavily driven by **dispersive wave mechanics (KdV)** ($+25.0\%$ absolute gain, $b=5, c=0$) and **pattern formation (Gray-Scott)** ($+10.0\%$ absolute gain, $b=2, c=0$).
2. **System Invariance:** In FitzHugh-Nagumo, both structured protocols easily identify excitable dynamics ($100.0\%$). In Navier-Stokes, both methods achieve $40.0\%$ recovery due to vorticity gradient noise.
3. **No Inversion:** Across all 5 systems, Fixed never consistently beats Active ($c \le 1$ in all systems).

---

### 3. Cluster-Robust GEE Modeling

To rigorously account for clustering within matched pairs and repeated measurements across physical systems, we fitted a Generalized Estimating Equations (GEE) model with binomial family and exchangeable working correlation:
$$\text{logit}(P(\text{Recovery})) = \beta_0 + \beta_{\text{active}} \cdot \mathbf{1}_{\text{Active}} + \sum_{s} \alpha_s \cdot \mathbf{1}_{\text{System}=s} + \gamma \cdot \text{NoiseLevel}$$

#### GEE Estimation Results:
- **Active Effect ($\beta_{\text{active}}$):** $+0.7514$
- **Cluster-Robust Standard Error:** $0.2771$
- **Wald $z$-statistic:** $2.712$
- **$p$-value:** $\mathbf{0.0067} < 0.01$
- **Odds Ratio ($\text{OR}$):** $e^{0.7514} = \mathbf{2.12}$ ($95\%$ CI: $[1.23, 3.65]$)

#### Conclusion:
Even after clustering on matched pairs and controlling for physical system baseline difficulty and noise degradation, the active discovery policy confers a **$2.12\times$ increase in the odds of exact physical-law recovery ($p = 0.0067$)**. Pseudoreplication does not invalidate the central finding, but the report must explicitly disclose that the sample size represents 100 scenario evaluations across 5 physical systems.
