# Project NOMOS — Milestone M5.1
## Query Efficiency, Right-Censoring & Early Stopping Re-Analysis

**Review Role:** Independent Statistical Auditor  
**Auditor / Git Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  

---

### 1. The Right-Censoring & Early Termination Trap

In Milestone M5, `audit/m5/STATISTICAL_ANALYSIS.md` stated:
> "Active experimentation terminates with conclusive identifiability in significantly fewer trajectory observations than passive schedules (2.10 vs 2.28 mean queries, Wilcoxon $p = 0.0202$)."

**Auditor Red Flag:**
Does a lower mean query count necessarily imply sample efficiency?
If an algorithm halts prematurely on an *incorrect* model, its query count will be artificially low! To distinguish genuine sample efficiency from premature false stopping, we must dissect the 500 episodes into distinct operational outcomes.

---

### 2. Comprehensive Outcome Classification

For every episode ($N = 500$), we cross-tabulate termination status against true ground-truth recovery:

| Strategy | Total Episodes | Successful Identification | Incorrect Confident Identification | Multiple Plausible Laws Unresolved | False Identification Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Active (`greedy_disagreement`)** | 100 | **63** (63.0%) | 34 (34.0%) | 3 (3.0%) | **35.1%** (34/97) |
| **Active (`cost_normalized`)** | 100 | **61** (61.0%) | 37 (37.0%) | 2 (2.0%) | **37.8%** (37/98) |
| **Passive (`fixed` schedule)** | 100 | 55 (55.0%) | 43 (43.0%) | 2 (2.0%) | **43.9%** (43/98) |
| **Stochastic (`random` selection)** | 100 | 46 (46.0%) | 52 (52.0%) | 2 (2.0%) | **53.1%** (52/98) |
| **Ensemble (`uncertainty_aware`)** | 100 | 20 (20.0%) | 74 (74.0%) | 6 (6.0%) | **78.7%** (74/94) |

#### Critical Findings:
1. **False Identification Rate:** When passive or random methods halt with `status = IDENTIFIED`, they are **incorrect in 43.9% to 53.1% of cases**. Active experimentation reduces the false identification rate to **35.1%**.
2. **Premature Termination on Degenerate Models:** When an uninformative experiment is acquired (e.g., quiet initial condition in FitzHugh-Nagumo or Taylor-Green vortex in Navier-Stokes), the only active surviving hypothesis is often an incomplete physics prior (such as pure diffusion $u_t = \nabla^2 u$). The auditor evaluates $\Delta \text{BIC}$ against no strong competitor and erroneously terminates early!

---

### 3. Conditional Query Efficiency (Successful Episodes Only)

When we analyze queries required **conditional on successful exact recovery**:

| Strategy | Successful Episodes | Mean Queries (Success Only) | Std Dev | Queries $\le 2$ Rate | Queries $\le 3$ Rate | Queries $\le 4$ Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Active (`greedy_disagreement`)** | 63 | **2.000** | 0.000 | **63.0%** | **63.0%** | **63.0%** |
| **Active (`cost_normalized`)** | 61 | **2.000** | 0.000 | **61.0%** | **61.0%** | **61.0%** |
| **Passive (`fixed` schedule)** | 55 | 2.382 | 0.892 | 44.0% | 50.0% | 50.0% |
| **Stochastic (`random` selection)** | 46 | 2.196 | 0.582 | 41.0% | 42.0% | 46.0% |
| **Ensemble (`uncertainty_aware`)** | 20 | 2.400 | 0.503 | 12.0% | 20.0% | 20.0% |

#### Key Insights:
1. **Instant Falsification at Step 1:** In every single successful Active episode ($63/63$), the system identified the true law on exactly Query 2. Step 0 (solitary/default state) generated candidate hypotheses; Step 1 acquired the maximally divergent experiment, immediately falsified the competing impostor, and established decisive Bayes Factor evidence.
2. **Fixed Schedule Latency:** In the Fixed schedule, successful recovery was delayed across Queries 2, 3, and 4 (mean 2.382), because Fixed was forced to cycle through uninformative solitary shifts before reaching an informative state.
3. **Budget Constrained Cumulative Recovery:** At an observation budget of $B = 2$ queries, Active achieves **63.0%** recovery, compared to **44.0%** for Fixed and **41.0%** for Random (**$+19.0\%$ absolute gain**, $+43.2\%$ relative gain).
