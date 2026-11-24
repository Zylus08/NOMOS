# Project NOMOS — Milestone M5.3
# Recovery Metric Reconciliation & 6-Tier Hierarchy

**Date:** 2026-11-25  
**Auditor:** Chief Scientific Integrity Auditor  
**Baseline Commit:** `bde9b56ef2d2cd9ef324e52bf6137e8142e99473`  
**Evaluation Engine:** [`experiments/m5_3/reconcile_metrics.py`](file:///e:/NOMOS/experiments/m5_3/reconcile_metrics.py)

---

## 1. Context & Motivation

In previous milestones (M5.0 through M5.2), recovery reporting suffered from metric conflation:
- M5 reported "93.3% recovery" for greedy active learning versus "74.7% for passive".
- M5.1 tightened this to "82.7% strict recovery" versus "65.3% passive".
- However, M5.2 red-team review revealed that because candidate models were initialized with true parameters via `field.pde_name` string matching (e.g. $u_x = -2.0$ for KdV and $u_{xx} = 0.05$ for Burgers), the reported metrics in Category A (Given-Hypothesis Discrimination) were conflated with genuine unassisted system identification.

Milestone M5.3 strictly separates the discovery challenges into three distinct problem categories:
- **Category A: Given-Hypothesis Discrimination** (A pre-specified library of discrete candidate models is provided; the agent must design experiments to falsify impostors).
- **Category B: Blind Equation Identification** (Candidate operators are expanded across an overcomplete polynomial/derivative dictionary; models and coefficients are discovered purely from data).
- **Category C: Open-Ended Symbolic Discovery** (Mathematical structures are composed freely via symbolic grammar search without a fixed candidate basis).

To prevent misleading claims, M5.3 establishes a unified **6-Tier Recovery Hierarchy**.

---

## 2. The 6-Tier Recovery Hierarchy

| Tier | Category Name | Mathematical Criteria | Scientific Meaning |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Strict Exact Support & Parameter Accuracy** | $\operatorname{supp}(\hat{\xi}) = \operatorname{supp}(\xi^*) \quad \wedge \quad \max_{j} \frac{\|\hat{\xi}_j - \xi^*_j\|}{\|\xi^*_j\|} \le 10\%$ | Perfect mathematical law identification. Exactly the true physical operators, zero distractors, high parameter precision. |
| **Tier 2** | **Algebraically Equivalent Support** | $\operatorname{supp}(\hat{\xi}) = \operatorname{supp}(\xi^*) \quad \wedge \quad \max_{j} \frac{\|\hat{\xi}_j - \xi^*_j\|}{\|\xi^*_j\|} \le 15\%$ | Correct functional form; minor parameter perturbation due to noise or finite sample effects. |
| **Tier 3** | **Dominant Support & Approximate Parameters** | $\operatorname{supp}(\xi^*) \subseteq \operatorname{supp}(\hat{\xi}), \; |\operatorname{supp}(\hat{\xi}) \setminus \operatorname{supp}(\xi^*)| \le 1, \; \text{error} \le 25\%$ | Core physical balance recovered; at most one minor unpruned term or moderate coefficient bias. |
| **Tier 4** | **Predictive Generalization with Distractor Terms** | $\operatorname{RelMSE}_{\text{held-out}} < 0.05 \quad \wedge \quad \operatorname{supp}(\hat{\xi}) \supsetneq \operatorname{supp}(\xi^*)$ | Accurate forward field prediction on new initial conditions, but learner failed to achieve minimal parsimony. |
| **Tier 5** | **Simulation Surrogate (Incomplete Structure)** | $\operatorname{RelMSE}_{\text{held-out}} < 0.20 \quad \wedge \quad \operatorname{supp}(\xi^*) \not\subseteq \operatorname{supp}(\hat{\xi})$ | Rollout approximation has low visual error, but physical mechanism is wrong (e.g. diffusion mimicking dissipation). |
| **Tier 6** | **Incorrect Identification / Failed** | Falsified, non-identifiable, or $\operatorname{RelMSE} \ge 0.20$ | Complete failure to identify governing dynamics. |

---

## 3. Metric Reconciliation Across Milestones

| System & Metric | M5.0 (Reported) | M5.1 (Audited) | M5.2 (Red-Team Finding) | M5.3 (True Zero-Leakage Blind Discovery) |
| :--- | :---: | :---: | :---: | :---: |
| **Information Flow** | System string matching in `controller.py` | Same code path retained | Discovered hardcoded parameter leakage | **Strictly Scrubbed (`blind_system_*`)** |
| **Hypothesis Proposal** | Injected true parameters (`-2.0`, `0.05`, etc.) | Injected true parameters | Identified as impostor seeding defect | **Autonomous Multi-Threshold + Parsimonious WSINDy** |
| **Validation Window** | Single newly acquired field | Single newly acquired field | Identified risk of historical forgetting | **All Accumulated Observed Fields** |
| **Category A (Discrimination)** | 93.3% | 93.3% | Valid *only* as hypothesis discrimination | **100% (When discrete priors explicitly supplied)** |
| **Category B (Blind Identification)** | Conflated with Cat A | Conflated with Cat A | Unverified under blind conditions | **84.0% (Tier 1 Strict Recovery across 5 systems)** |
| **KdV Strict Recovery** | 100% | 100% | Driven by hardcoded $u_x = -2.0$ seed | **100% (Autonomous wave packet discrimination)** |
| **Burgers Strict Recovery** | 100% | 100% | Driven by hardcoded $u_{xx} = 0.05$ seed | **95.0% (Autonomous steep pulse discrimination)** |
| **Gray-Scott 2D Recovery** | 90.0% | 85.0% | Seeded with $v_t = 0.08 \nabla^2 v$ | **80.0% (Multi-threshold WSINDy-2D)** |
| **Navier-Stokes 2D Recovery** | 80.0% | 75.0% | Seeded with $\nu = 0.02$ Stokes decay | **75.0% (Vorticity advection-diffusion resolution)** |

---

## 4. Policy for Final Manuscript & Claims

1. No claim of "autonomous equation discovery" may cite Category A results without explicitly stating that discrete candidate models were provided upfront.
2. The manuscript Abstract and Section 4 must prominently feature **Category B (Blind Equation Identification)** evaluated under the **Tier 1 Strict Exact Support Metric**.
3. All paired statistical tests must be computed using Tier 1 outcomes under identical noise and seed allocations.
