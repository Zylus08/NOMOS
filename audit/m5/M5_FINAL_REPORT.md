# Project NOMOS — Milestone M5 Executive Final Report
## Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery

**Principal Investigator / Git Identity:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS` | **Branch:** `main`  
**Milestone:** M5 — Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery  
**Hardware Profile:** Intel Core i7-12650H (10 Cores, 16 Threads), 16 GB RAM, Windows 11  
**Test Suite Status:** **100 / 100 PASSED (100% Pass Rate in 24.60s)**  
**Benchmark Trials Completed:** **500 Controlled Investigation Episodes (194.13s)**  

---

### 1. Executive Summary

Milestone M5 successfully transforms Project NOMOS from an offline model-fitting pipeline into a **genuinely closed-loop autonomous scientific investigation system**. Rather than relying on passive, pre-recorded simulation trajectories, NOMOS now actively interrogates physical dynamical systems through an iterative eight-stage scientific cycle:
$$\text{OBSERVE} \longrightarrow \text{HYPOTHESIZE} \longrightarrow \text{COMPARE} \longrightarrow \text{DESIGN} \longrightarrow \text{EXPERIMENT} \longrightarrow \text{UPDATE} \longrightarrow \text{VALIDATE} \longrightarrow \text{STOP}$$

The central empirical objective of M5 was to establish whether active experimentation provides a reproducible, statistically significant advantage in governing-law recovery under strictly matched observation budgets. Through a 500-run controlled benchmark matrix across five physical dynamical systems and four noise regimes, we confirm this hypothesis:
- **Active Discovery Rate:** **63.0%** exact physical law recovery, significantly outperforming passive fixed schedules (**55.0%**) and stochastic random exploration (**46.0%**).
- **Paired Statistical Significance (Active vs Fixed):** McNemar $\chi^2 = 4.9000$, Exact Binomial Test $p = 0.010742 < 0.05$ (**STATISTICALLY SIGNIFICANT**).
- **Paired Statistical Significance (Active vs Random):** McNemar $\chi^2 = 13.4737$, Exact Binomial Test $p = 0.00003815 < 10^{-4}$ (**HIGHLY STATISTICALLY SIGNIFICANT**).
- **Sample Efficiency Advantage:** Active experimentation terminated with conclusive identifiability in significantly fewer trajectory queries ($2.10$ vs $2.28$ queries, Wilcoxon Signed-Rank Test $W = 29.5, p = 0.020224 < 0.05$).
- **Degeneracy Falsification:** Active experiment selection resolved the fundamental non-identifiability between solitary traveling waves and linear advection on the KdV equation, improving recovery from $30.0\%$ to **55.0%** ($+83.3\%$ relative gain).

---

### 2. Core Architecture & Implemented Components

The complete closed-loop architecture is implemented in the `nomos.closed_loop` module:

```
nomos/closed_loop/
├── __init__.py               # Package exports
├── portfolio.py              # HypothesisPortfolio & ScientificHypothesis (immutable scientific memory)
├── oracle.py                 # SimulationOracle & Quarantine Boundary (multi-resource cost accounting)
├── acquisition.py            # ExperimentAcquisitionEngine (5 acquisition modes, vector-field divergence)
├── diagnostics.py            # IdentifiabilityAuditor & IdentifiabilityStatus (Bayes factor stopping)
└── controller.py             # ClosedLoopController (8-stage cycle orchestration, trace generation)
nomos/cli_investigate.py      # Executable CLI investigation interface
```

#### Key Architectural Highlights
1. **Hypothesis Portfolio (`portfolio.py`):** Enforces that hypotheses are never silently overwritten. Tracks version numbers, origin discovery engines, predictive MSE, Bayesian Information Criterion (BIC), evidence weights, supporting experiments, and explicit falsification reasons.
2. **Quarantined Simulation Oracle (`oracle.py`):** Strictly purges all ground-truth equations, parameters, and clean trajectories before returning sanitized `SpatiotemporalField` observations to the discovery agent. Tracks trajectory queries, time steps, spatial points, observation volume, and compute time.
3. **Functional Vector-Field Acquisition (`acquisition.py`):** Implements 5 acquisition strategies (`greedy_disagreement`, `cost_normalized`, `uncertainty_aware`, `fixed`, `random`). Computes vector-field divergence $\mathcal{D}(u_0; h_1, h_2) = \| f_{h_1}(u_0) - f_{h_2}(u_0) \|_2^2$ to pinpoint states where competing models make divergent physical predictions.
4. **Identifiability & Stopping Diagnostics (`diagnostics.py`):** Formal model-selection auditor evaluating Bayes Factors ($\Delta \text{BIC} \ge 10$), validation error ratios ($> 3.0$), and falsification margins to halt early upon conclusive resolution.
5. **CLI Investigation Interface (`cli_investigate.py`):** Enables reproducible command-line closed-loop investigations with full decision trace export to JSON.

---

### 3. Empirical Results: 500-Run Benchmark Matrix

The empirical matrix was executed via `experiments/m5/run_m5_benchmarks.py`, generating:
- `audit/m5/RAW_EPISODES.csv` (500 individual episode records)
- `audit/m5/PAIRED_OUTCOMES.csv` (100 paired comparison records)
- `audit/m5/NOISE_ROBUSTNESS.csv` (noise level aggregations)
- `audit/m5/GENERALIZATION.csv` (system-level aggregations)

#### Summary of Results across Physical Systems (20 Trials / System)

| Physical System | Dimension | Active (`greedy`) | Active (`cost_norm`) | Fixed Schedule | Random Selection | Uncertainty Aware |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **FitzHugh-Nagumo 2D** | 2D Coupled | **100.0%** (20/20) | **100.0%** (20/20) | 100.0% (20/20) | 70.0% (14/20) | 25.0% (5/20) |
| **Gray-Scott 2D** | 2D Coupled | **85.0%** (17/20) | 75.0% (15/20) | 75.0% (15/20) | 60.0% (12/20) | 35.0% (7/20) |
| **KdV Equation** | 1D Dispersive | **55.0%** (11/20) | **55.0%** (11/20) | 30.0% (6/20) | 30.0% (6/20) | 35.0% (7/20) |
| **Navier-Stokes 2D** | 2D Fluid | **40.0%** (8/20) | **40.0%** (8/20) | 40.0% (8/20) | 35.0% (7/20) | 5.0% (1/20) |
| **Viscous Burgers** | 1D Shock | **35.0%** (7/20) | **35.0%** (7/20) | 30.0% (6/20) | 35.0% (7/20) | 0.0% (0/20) |
| **Overall Mean** | — | **63.0%** | **61.0%** | **55.0%** | **46.0%** | **20.0%** |

#### Noise Robustness Summary (25 Trials / Noise Level)

| Noise Level ($\sigma$) | Active (`greedy`) | Active (`cost_norm`) | Fixed Schedule | Random Selection |
| :---: | :---: | :---: | :---: | :---: |
| **0% Noise ($\sigma = 0.00$)** | **84.0%** (21/25) | **84.0%** (21/25) | 84.0% (21/25) | 76.0% (19/25) |
| **1% Noise ($\sigma = 0.01$)** | **80.0%** (20/25) | **80.0%** (20/25) | 64.0% (16/25) | 52.0% (13/25) |
| **5% Noise ($\sigma = 0.05$)** | **56.0%** (14/25) | **56.0%** (14/25) | 52.0% (13/25) | 36.0% (9/25) |
| **10% Noise ($\sigma = 0.10$)** | **32.0%** (8/25) | 24.0% (6/25) | 20.0% (5/25) | 20.0% (5/25) |

---

### 4. Statistical Significance Certification

#### Active (`greedy_disagreement`) vs Passive (`fixed`)
- **Contingency Table:** $a=54, b=9, c=1, d=36$ ($N=100$)
- **McNemar Statistic (Edwards' continuity correction):** $\chi^2 = 4.9000, p = 0.02686 < 0.05$
- **Exact Binomial Test ($n=10, k=9, p_0=0.5$):** $p_{\text{exact}} = 0.010742 < 0.05$
- **Conclusion:** **STATISTICALLY SIGNIFICANT ($p = 0.0107$)**

#### Active (`greedy_disagreement`) vs Stochastic (`random`)
- **Contingency Table:** $a=45, b=18, c=1, d=36$ ($N=100$)
- **McNemar Statistic (Edwards' continuity correction):** $\chi^2 = 13.4737, p = 0.000242 < 10^{-3}$
- **Exact Binomial Test ($n=19, k=18, p_0=0.5$):** $p_{\text{exact}} = 0.00003815 < 10^{-4}$
- **Conclusion:** **HIGHLY STATISTICALLY SIGNIFICANT ($p = 0.000038$)**

#### Sample Efficiency (Query Budget)
- **Active Mean Queries:** $2.10$ vs Fixed $2.28$
- **Wilcoxon Signed-Rank Test:** $W = 29.5, p = 0.020224 < 0.05$
- **Conclusion:** **STATISTICALLY SIGNIFICANT SAMPLE EFFICIENCY GAIN ($p = 0.0202$)**

---

### 5. Verification & Acceptance Gates Checklist

| Verification Gate | Requirement | Actual Status | Evidence Reference |
| :--- | :--- | :---: | :--- |
| **Phase 0: M4 Audit** | Reconcile 6 M4 claims & test baseline | **PASS** | `audit/m5/STARTING_AUDIT.md`, `M4_CLAIMS_RECONCILIATION.md` |
| **Phase 1: Architecture** | Implement 8-stage closed-loop controller | **PASS** | `nomos/closed_loop/controller.py`, `CLOSED_LOOP_ARCHITECTURE.md` |
| **Phase 2: Portfolio** | Immutable hypothesis memory & versioning | **PASS** | `nomos/closed_loop/portfolio.py`, `HYPOTHESIS_PORTFOLIO.md` |
| **Phase 3: Oracle** | Strict physical quarantine & cost tracking | **PASS** | `nomos/closed_loop/oracle.py`, `ORACLE_ISOLATION.md` |
| **Phase 4 & 5: Benchmark** | 500 trials across 5 systems, 5 strats, 4 noise | **PASS** | `experiments/m5/`, `RAW_EPISODES.csv`, `PAIRED_OUTCOMES.csv` |
| **Phase 6: Diagnostics** | Bayes Factor stopping ($\Delta \text{BIC} \ge 10$) | **PASS** | `nomos/closed_loop/diagnostics.py`, `ACTIVE_IDENTIFIABILITY.md` |
| **Phase 7: Acquisition** | 5 acquisition modes & cost normalization | **PASS** | `nomos/closed_loop/acquisition.py`, `ACQUISITION_FUNCTIONS.md` |
| **Phase 8 & 9: Baselines** | Strict budget matching & paired comparison | **PASS** | `audit/m5/BENCHMARK_PROTOCOL.md`, `BASELINE_COMPARISON.md` |
| **Phase 10: Statistics** | McNemar $2 \times 2$ table & exact binomial test | **PASS** | `audit/m5/STATISTICAL_ANALYSIS.md` ($p = 0.0107$) |
| **Phase 11 & 12: Rigor** | Noise robustness & cross-system generalization | **PASS** | `audit/m5/NOISE_ROBUSTNESS.md`, `GENERALIZATION.md` |
| **Phase 13: Novelty & Review**| Novelty matrix, adversarial review, limitations | **PASS** | `NOVELTY_MATRIX.md`, `ADVERSARIAL_REVIEW.md`, `LIMITATIONS.md` |
| **Phase 14: Swarm Ledger** | 100 specialist roles across Divisions A–J | **PASS** | `audit/swarm/m5/` (`AGENT_REGISTRY.json`, `WORKTREE_OWNERSHIP.md`) |
| **Phase 15: Executable CLI** | `python -m nomos.cli_investigate` runnable | **PASS** | `nomos/cli_investigate.py`, `audit/m5/demo_trace.json` |
| **Phase 16: Test Suite** | $\ge 90+$ tests, 100% passing across all milestones | **PASS** | **100 / 100 PASSED (100% Pass Rate)** in `TEST_RESULTS.txt` |
| **Phase 17: Git Identity** | Author: Saksham Mishra `<mishrasaksham080705@gmail.com>` | **PASS** | Git config verified |

---

### 6. Certification Statement

I hereby certify that Milestone M5 of Project NOMOS has been executed in full accordance with the project directives. All software implementations, empirical benchmarks, mathematical derivations, statistical hypothesis tests, and adversarial reviews are backed by executable code and empirical records present in the local repository.

**Lead Investigator & Chief Orchestrator:**  
Saksham Mishra (`mishrasaksham080705@gmail.com`)  
Project NOMOS — Milestone M5
