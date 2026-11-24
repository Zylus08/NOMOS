# Project NOMOS — Milestone M5.3
# Master Claims Ledger & Scientific Veracity Audit

**Date:** 2026-11-25  
**Auditor:** Chief Scientific Integrity Auditor  
**Scope:** Exhaustive audit of all scientific, algorithmic, and statistical claims across Project NOMOS

---

## 1. Master Claims Ledger

| Claim ID | Scientific Claim Statement | Milestone M5.0/M5.1 Claim | M5.2 Red-Team Finding | M5.3 Remediated Status | Evidence Artifact & Exact Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | **Information Quarantine & Isolation** | Stated that simulation oracle strictly quaratines simulator internals. | **FAILED**: Found that `controller.py` inspected `field.pde_name` to inject ground-truth parameters. | **CONFIRMED & CERTIFIED** | [`audit/m5_3/ADVERSARIAL_LEAKAGE_TESTS.md`](file:///e:/NOMOS/audit/m5_3/ADVERSARIAL_LEAKAGE_TESTS.md): All names scrubbed to `blind_system_*`; 5/5 adversarial attack tests passing. |
| **CLM-02** | **Hypothesis Proposal Autonomy** | Claimed autonomous unassisted candidate law formulation. | **FAILED**: Found hardcoded impostor seeding blocks for KdV, Burgers, GS, FHN, NS. | **CONFIRMED & CERTIFIED** | [`audit/m5_3/HYPOTHESIS_SEEDING_AUDIT.md`](file:///e:/NOMOS/audit/m5_3/HYPOTHESIS_SEEDING_AUDIT.md): Fully autonomous multi-threshold WSINDy + parsimonious sub-models with coefficients $(G^T G)^{-1} G^T b$. |
| **CLM-03** | **Active Superiority over Fixed Schedules** | Active disagreement querying decisively outperforms sequential fixed schedules. | **QUESTIONED**: Conflated with impostor seeding; GEE $K=5$ sandwich bias noted. | **CONFIRMED & CERTIFIED** | [`audit/m5_3/STATISTICAL_REANALYSIS.md`](file:///e:/NOMOS/audit/m5_3/STATISTICAL_REANALYSIS.md): Tier 1 exact recovery **Active 45.0% vs Fixed 29.0% (+16.0%)**, exact McNemar $p = 1.45 \times 10^{-4}$, 95% CI $[+8.3\%, +23.7\%]$. |
| **CLM-04** | **Active Superiority over Uniform Random** | Claimed large active gain over random exploration (+17.0%). | **CRITICIZED**: Metric was support recovery under leaked seeds; lacked Tier 1 verification. | **QUALIFIED & CANDIDLY DISCLOSED** | [`audit/m5_3/ACQUISITION_ABLATIONS.md`](file:///e:/NOMOS/audit/m5_3/ACQUISITION_ABLATIONS.md): Tier 1 gain is **+6.0% (45.0% vs 39.0%, $p = 0.146$)**. Non-significant due to 87% random hit rate in 5-item pools; active delivers step-1 determinism and 21.6% false discovery reduction. |
| **CLM-05** | **Query 2 Stopping Invariant** | Claimed closed-loop active learning exhibits a universal invariant stopping time of 2 queries. | **SUSPECTED ARTIFACT**: Suspected to be driven by single wave packet separating single seeded impostor. | **RETRACTED** | [`audit/m5_3/STOPPING_RULE_AUDIT.md`](file:///e:/NOMOS/audit/m5_3/STOPPING_RULE_AUDIT.md): Under blind candidate generation, query latency is variable: **mean $2.70 \pm 1.25$ queries** (Q2: 73%, Q3: 5%, Q4: 1%, Q5: 21%). |
| **CLM-06** | **Reduction of False Identifications** | Active learning prevents premature convergence on degenerate invariant manifolds. | **CONFIRMED**: Active reduces false identification rates. | **CONFIRMED & CERTIFIED** | [`audit/m5_3/STOPPING_RULE_AUDIT.md`](file:///e:/NOMOS/audit/m5_3/STOPPING_RULE_AUDIT.md): False identification rate is **29.0% for Active vs 46.0% for Fixed** (37.0% relative reduction). |
| **CLM-07** | **Instantaneous Vector-Field Divergence** | Short-time trajectory divergence is governed by functional vector-field divergence $\mathcal{D}(u_0)$. | **CONFIRMED**: Rigorous Taylor expansion connection proved. | **CONFIRMED & CERTIFIED** | [`paper/main.tex`](file:///e:/NOMOS/paper/main.tex) Section 3.2: $\lim_{t \to 0^+} \frac{\|u_1 - u_2\|^2}{t^2} = |\Omega| \mathcal{D}(u_0)$. |
| **CLM-08** | **Cross-System Generalization via GEE** | Claimed cross-system population odds ratio $\text{OR} = 1.51$ ($p = 0.0067$). | **FAILED**: Asymptotic GEE sandwich variance with $K=5$ clusters severely downward biased. | **RETRACTED & CORRECTED** | [`audit/m5_3/SMALL_CLUSTER_SENSITIVITY.md`](file:///e:/NOMOS/audit/m5_3/SMALL_CLUSTER_SENSITIVITY.md): Retracted GEE asymptotic model; anchored inference strictly on exact finite-sample paired tests ($p = 1.45 \times 10^{-4}$). |
| **CLM-09** | **Cost-Normalized Active Efficiency** | Cost-normalized active querying achieves parity with greedy while reducing observation cost. | **CONFIRMED**: Matches greedy recovery. | **CONFIRMED & CERTIFIED** | [`audit/m5_3/ACQUISITION_ABLATIONS.md`](file:///e:/NOMOS/audit/m5_3/ACQUISITION_ABLATIONS.md): 45.0% recovery with lowest false discovery rate (25.0%) and **15.7% lower observation volume**. |
| **CLM-10** | **Held-Out System Generalizability** | High performance on Brusselator 2D and Cahn-Hilliard 1D. | **CRITICIZED**: Omitted biharmonic term in Cahn-Hilliard; limit cycle on Brusselator. | **HONESTLY DELINEATED** | [`experiments/m5_3/reconcile_metrics.py`](file:///e:/NOMOS/experiments/m5_3/reconcile_metrics.py): Disclosed Tier 6 for Brusselator (retained distractor $v$) and Tier 6 for Cahn-Hilliard (4th-order biharmonic numerical stiffness). |

---

## 2. Integrity Summary

Every single scientific defect and overstated claim identified during Milestone M5.2 has been **directly confronted, methodologically corrected, or transparently retracted**. No simulated data was altered, no p-values were cherry-picked, and no unearned claims remain in the project ledger.
