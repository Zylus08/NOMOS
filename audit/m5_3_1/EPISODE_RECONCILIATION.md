# PROJECT NOMOS — MILESTONE M5.3.1 AUDIT REPORT
## Deliverable 5: Authoritative Episode Accounting & Manifest Delineation

**Date:** 2026-11-25  
**Auditor:** Independent Scientific Audit Commission & Replication Orchestrator  
**Commit Baseline:** `e401fa836c1a7c98313b663d7f6a3175f24448ce`  
**Authoritative Manifest:** `audit/m5_3_1/CORRECTED_EPISODES.csv`  

---

### Executive Summary

Milestone reports M5.1, M5.2, and M5.3 intermittently cited "400 primary episodes" and "480 total episodes," creating potential ambiguity regarding sample accounting, held-out validation, and paired statistical testing. 

This audit provides complete lineage tracking and structural delineation for all 480 episodes in the Project NOMOS benchmark suite. We confirm that the 480 episodes consist of exactly **400 Primary Benchmark Episodes** and **80 Held-Out Generalization Episodes**, with 100% deterministic reproducibility under matched random seeds.

---

### 1. Structural Decomposition of the 480 Episodes

Every benchmark episode represents an end-to-end autonomous investigation executed under strict blinding and hard query budget ($B \le 4$). The 480 episodes are partitioned into two disjoint sets:

```
Total Benchmark Matrix: 480 Episodes
├── 1. Primary Benchmark (400 Episodes, IDs: 1 – 400)
│   ├── Systems (5): KdV, Viscous Burgers, Gray-Scott 2D, FitzHugh-Nagumo 2D, Navier-Stokes 2D
│   ├── Noise Levels (4): 0.00 (0%), 0.01 (1%), 0.05 (5%), 0.10 (10%)
│   ├── Random Seeds (5): 42, 43, 44, 45, 46
│   └── Strategies (4):
│       ├── greedy_disagreement (Active, 100 episodes)
│       ├── cost_normalized (Active, 100 episodes)
│       ├── random (Passive Baseline, 100 episodes)
│       └── fixed (Passive Baseline, 100 episodes)
│   └── 5 x 4 x 5 x 4 = 400 episodes (yielding 100 matched 4-way quadruplets)
│
└── 2. Held-Out Replication Benchmark (80 Episodes, IDs: 401 – 480)
    ├── Systems (2): Brusselator 2D, Cahn-Hilliard 1D
    ├── Noise Levels (4): 0.00, 0.01, 0.05, 0.10
    ├── Random Seeds (5): 42, 43, 44, 45, 46
    └── Strategies (2):
        ├── greedy_disagreement (Active, 40 episodes)
        └── random (Passive Baseline, 40 episodes)
    └── 2 x 4 x 5 x 2 = 80 episodes (yielding 40 matched pairs)
```

---

### 2. Primary vs. Held-Out Delineation

| Feature | Primary Benchmark ($N=400$) | Held-Out Generalization Benchmark ($N=80$) |
|:---|:---|:---|
| **Episode ID Range** | `1` to `400` | `401` to `480` |
| **Physical Simulators** | KdV, Burgers, Gray-Scott, FitzHugh-Nagumo, Navier-Stokes | Brusselator 2D, Cahn-Hilliard 1D |
| **Scientific Objective** | Hypothesis testing against established baselines (McNemar tests, Newcombe CIs) | Out-of-distribution transfer without architectural retuning |
| **Tested Strategies** | 4 strategies: `greedy_disagreement`, `cost_normalized`, `random`, `fixed` | 2 strategies: `greedy_disagreement`, `random` |
| **Statistical Role** | Primary confirmatory hypothesis testing ($N=100$ matched pairs) | Secondary exploratory transfer audit |
| **Candidate Libraries** | Overcomplete with physical distractors | Overcomplete with cross-system distractors |

---

### 3. Authoritative Manifest Schema

All 480 reconciled episodes are recorded in `audit/m5_3_1/CORRECTED_EPISODES.csv` adhering to the mandatory 12-column schema:

1. `episode_id` (int): Unique identifier ($1 \le \text{ID} \le 480$).
2. `benchmark_type` (str): `PRIMARY` or `HELD_OUT`.
3. `system_key` (str): Physical system identity (`kdv`, `burgers`, `gray_scott`, `fitzhugh`, `navier_stokes`, `brusselator`, `cahn_hilliard`).
4. `noise_level` (float): Injected Gaussian noise ratio ($0.0, 0.01, 0.05, 0.10$).
5. `seed` (int): RNG seed for trajectory realization and candidate initialization ($42, 43, 44, 45, 46$).
6. `strategy` (str): Acquisition algorithm (`greedy_disagreement`, `cost_normalized`, `random`, `fixed`).
7. `total_queries` (int): Total trajectory queries executed ($2 \le Q \le 4$).
8. `status` (str): Terminal identifiability state (`IDENTIFIED`, `BUDGET_EXHAUSTED`, `NONIDENTIFIABLE`).
9. `winning_equation` (str): Mathematical expression of winning hypothesis (or `NONE`).
10. `tier` (int): Evaluated scientific recovery tier ($1, 2, 3, 6$).
11. `is_tier1_strict` (int): Binary indicator of strict exact recovery ($1$ if Tier 1, else $0$).
12. `max_parameter_rel_error` (float): Maximum relative error across true parameter coefficients ($-1.0$ if non-recovered).

---

### 4. Reconciled Query Budget Distribution

Under the strict $B \le 4$ contract, query consumption across all 480 episodes is bounded as follows:

| Total Queries | Primary Benchmark ($N=400$) | Held-Out Benchmark ($N=80$) | Total Matrix ($N=480$) | Percentage |
|:---:|:---:|:---:|:---:|:---:|
| **2** | 273 | 42 | 315 | 65.6% |
| **3** | 30 | 4 | 34 | 7.1% |
| **4** | 97 | 34 | 131 | 27.3% |
| **Total** | **400** | **80** | **480** | **100.0%** |

Every episode terminating at query 4 represents a run that exhausted the maximum allocated budget without exceeding it. Zero queries exceeded budget ($Q \le 4$ holds strictly).
