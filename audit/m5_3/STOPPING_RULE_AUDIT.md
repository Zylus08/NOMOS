# Project NOMOS — Milestone M5.3
# Stopping Rule, Falsification Dynamics & False Identification Audit

**Date:** 2026-11-25  
**Auditor:** Chief Scientific Integrity Auditor  
**Empirical Evidence:** [`audit/m5_3/BLIND_RAW_EPISODES.csv`](file:///e:/NOMOS/audit/m5_3/BLIND_RAW_EPISODES.csv) (480 episodes)

---

## 1. Dissection of the "Query 2 Invariant"

A prominent finding reported in Milestone M5.0 and M5.1 was the claim that:
> *"The active closed-loop controller exhibits an invariant stopping time of exactly 2 trajectory queries across physical systems."*

The M5.2 red-team review suspected that this invariant was an artifact of experimental setup. In Milestone M5.3, the empirical evidence confirms that **the Query 2 invariant was an artifact of hardcoded impostor seeding**.

### Empirical Query Distribution Under Blind Candidate Proposal
Under true zero-leakage conditions, where candidate hypotheses are generated autonomously via multi-threshold WSINDy and parsimonious sub-models:

| Acquisition Strategy | Query = 2 | Query = 3 | Query = 4 | Query = 5 (Budget Exhausted) | Mean Trajectory Queries |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Greedy Disagreement** | 73 (73.0%) | 5 (5.0%) | 1 (1.0%) | 21 (21.0%) | **2.70** |
| **Cost-Normalized** | 69 (69.0%) | 5 (5.0%) | 0 (0.0%) | 26 (26.0%) | **2.83** |
| **Random (Passive)** | 60 (60.0%) | 15 (15.0%) | 5 (5.0%) | 20 (20.0%) | **2.85** |
| **Fixed (Passive)** | 70 (70.0%) | 8 (8.0%) | 2 (2.0%) | 20 (20.0%) | **2.72** |

### Why Did Query 2 Dominate Previously?
1. In M5.0, exactly **one** discrete rival hypothesis was injected into the portfolio (e.g. `hyp_linear_advection_impostor` with exact parameter $u_x = -2.0$).
2. The initial condition pool contained a single pre-designed discriminant experiment (e.g. `wave_packet` for KdV) that immediately separated these two models.
3. Once that single rival was falsified at Query 2, exactly one model remained active, triggering early termination via the single-survivor rule:
   ```python
   if len(active_hypotheses) == 1:
       if top.val_mse < 0.2 and len(top.supporting_experiments) >= 1:
           return IdentifiabilityStatus.IDENTIFIED
   ```
4. In M5.3, because the candidate generator produces multiple competing sub-models directly from data, and because overcomplete libraries contain distractor operators, the controller requires **adaptive multi-step exploration** (taking 3, 4, or 5 queries in 27% of active runs).

---

## 2. False Identification Rate Audit

A crucial safety concern in autonomous scientific discovery is **false positive identification**: declaring that a physical law has been uniquely identified when the identified model is structurally incorrect or retains unpruned distractor terms.

In M5.3, an episode is classified as a **False Identification** if:
$$\text{Controller Status} == \text{IDENTIFIED} \quad \wedge \quad \text{Recovery Tier} \in \{3, 4, 5, 6\}$$

### False Identification Comparison (N=100 episodes per strategy)

| Strategy | Total Identified | True Tier 1 Identification | False Identifications | False Identification Rate |
| :--- | :---: | :---: | :---: | :---: |
| **Greedy Disagreement** | 74 | 45 | **29** | **29.0%** |
| **Cost-Normalized** | 70 | 45 | **25** | **25.0%** |
| **Random (Passive)** | 76 | 39 | **37** | **37.0%** |
| **Fixed (Passive)** | 75 | 29 | **46** | **46.0%** |

### Key Findings
1. **Active Learning Reduces False Discoveries**: Greedy disagreement and cost-normalized strategies reduce false identification by **37.0% to 45.7%** relative to the fixed passive baseline (25–29 vs 46).
2. **Failure Modes of Fixed Baseline**: The fixed baseline repeatedly queries the same uninformative regimes (e.g. single soliton or homogeneous states), leaving spurious hypotheses un-falsified. The Bayesian information criterion (BIC) then prematurely crowns an incorrect model due to lack of contradictory data.
3. **Noise Breakdown**: Across all strategies, false identifications concentrate almost entirely at $\sigma = 0.05$ (5% noise) and $\sigma = 0.10$ (10% noise), where noise variance inflates the weak-form residual, obscuring subtle physical operators (e.g. high-order dispersion $u_{xxx}$ or small diffusion).

---

## 3. Policy Recommendation

1. The claim of an "invariant 2-query stopping time" must be retracted from the manuscript and replaced with the empirical distribution: **mean $2.70 \pm 1.25$ queries**.
2. Stopping rules in automated scientific discovery should incorporate **cross-validation stability across independent query batches** rather than relying solely on within-sample BIC margins at high noise levels.
