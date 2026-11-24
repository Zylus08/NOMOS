# Project NOMOS — Milestone M5.1
## Original M5 Results Independent Reproduction & Ledger Audit

**Review Role:** Independent Chief Replication Orchestrator  
**Auditor / Git Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Baseline Commit:** `bf309750dabc147600ae2a59944f15e473d8a069`  

---

### 1. Reproduction Methodology

To audit whether the 500-episode M5 benchmark is bitwise or statistically reproducible, we evaluated the experimental script `experiments/m5/run_m5_benchmarks.py` using its exact parameter configurations:
- **Systems:** 5 physical dynamical systems (KdV, Viscous Burgers, Gray-Scott 2D, FitzHugh-Nagumo 2D, Navier-Stokes 2D).
- **Strategies:** 5 acquisition strategies (`greedy_disagreement`, `cost_normalized`, `uncertainty_aware`, `fixed`, `random`).
- **Noise Levels:** $\sigma \in \{0.00, 0.01, 0.05, 0.10\}$.
- **Random Seeds:** $\{42, 43, 44, 45, 46\}$.
- **Observation Budget:** $B_{max} = 4$ trajectory queries.

---

### 2. Comparative Audit of Committed vs Recomputed Data

| Metric | Committed in `audit/m5/` | Independently Recomputed in M5.1 | Discrepancy |
| :--- | :---: | :---: | :---: |
| **Total Investigation Episodes** | 500 | 500 | 0 |
| **Active (`greedy`) Overall Recovery** | 63.0% (63/100) | 63.0% (63/100) | 0.0% |
| **Active (`cost_norm`) Overall Recovery** | 61.0% (61/100) | 61.0% (61/100) | 0.0% |
| **Passive (`fixed`) Overall Recovery** | 55.0% (55/100) | 55.0% (55/100) | 0.0% |
| **Stochastic (`random`) Overall Recovery** | 46.0% (46/100) | 46.0% (46/100) | 0.0% |
| **Active vs Fixed Discordant Pairs** | $b=9, c=1$ | $b=9, c=1$ | 0 |
| **Active vs Random Discordant Pairs** | $b=18, c=1$ | $b=18, c=1$ | 0 |
| **Active Mean Queries to Stop** | 2.10 | 2.10 | 0.0 |
| **Fixed Mean Queries to Stop** | 2.28 | 2.28 | 0.0 |

---

### 3. Detailed Audit of Raw Records

Inspection of `RAW_EPISODES.csv` reveals:
1. **Determinism:** Seeded NumPy and simulation runs produce identical trajectories and hypothesis evaluations across independent executions.
2. **Trajectory Sanity:** All 500 episodes executed without numerical blowup or NaN divergence.
3. **Execution Runtime:** Total benchmark execution time was 194.13 seconds across 500 episodes (average 0.388 seconds per closed-loop episode), demonstrating high computational efficiency on the 10-core Intel i7-12650H architecture.

---

### 4. Reproduction Verdict

**VERDICT: REPRODUCED (100% Concordance).**  
All reported metrics, raw outcomes, recovery percentages, and paired discordant counts in `audit/m5/` are verified as genuine outputs of the committed algorithms and random seeds. No data falsification or synthetic inflation was detected.
