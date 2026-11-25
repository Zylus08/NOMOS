# PROJECT NOMOS — MILESTONE M5.3.1 AUDIT REPORT
## Deliverable 1: Experimental Budget Lifecycle & Forensic Accounting

**Date:** 2026-11-25  
**Auditor:** Independent Scientific Audit Commission & Replication Orchestrator  
**Commit Baseline:** `e401fa836c1a7c98313b663d7f6a3175f24448ce`  
**Repository:** `E:\NOMOS`  

---

### Executive Summary

Milestone M5.3 declared a maximum experimental budget of $B = 4$ trajectory queries per scientific investigation episode. However, an adversarial inspection of the M5.3 raw empirical artifacts revealed that **122 out of 480 episodes (25.4% of all runs; 28.6% of active runs)** recorded `experiments_queried == 5`.

This forensic audit traced the entire execution lifecycle of trajectory queries across `nomos/closed_loop/oracle.py`, `nomos/closed_loop/controller.py`, `experiments/m5_3/run_blind_benchmarks.py`, and reporting scripts. 

We established the exact mechanical cause of the fifth-query anomaly, implemented hard budget enforcement at the simulation boundary, re-executed the 480-episode benchmark under the strict $B \le 4$ contract, and generated a complete per-query transaction ledger (`ORACLE_CALL_LEDGER.csv`).

---

### 1. Root Cause Forensics: The Mechanics of Query 5

Tracing the query lifecycle in `nomos/closed_loop/controller.py` lines 105–188 revealed three compounding architectural defects:

#### Mechanism 1: Uncounted Initial Query in Stage 0
At the start of `run_investigation(initial_field=None)`, the controller observed an initial dataset. When `initial_field` was omitted, the controller executed Query 1 directly from `candidate_pool[0]`:
```python
# Stage 0: OBSERVE initial dataset
init_lbl, init_u0, _ = self.candidate_pool[0]
req = ExperimentRequest(
    experiment_id=f"exp_{iteration:02d}_{init_lbl}", # iteration was 0
    u0=init_u0,
    noise_level=self.noise_level,
    random_seed=self.random_seed,
)
resp = self.oracle.execute_experiment(req)
# self.oracle.query_count is now 1
```
However, the variable `iteration` was initialized to `0` and **remained 0** after this query was executed. The auditor checked:
```python
status, winning_h, diag = self.auditor.audit_portfolio(self.portfolio, iteration, self.max_budget)
# Passed current_budget_used = 0, despite 1 oracle query already consumed!
```

#### Mechanism 2: Off-By-One While-Loop Termination
Immediately following Stage 0, the controller entered the adaptive loop:
```python
while iteration < self.max_budget and status in (MULTIPLE_PLAUSIBLE_LAWS, INSUFFICIENT_EXCITATION):
    iteration += 1 # iteration values: 1, 2, 3, 4
    ...
    resp = self.oracle.execute_experiment(req) # Executed queries 2, 3, 4, 5
```
Because `max_budget` was set to `4`, the loop executed for `iteration = 1`, `iteration = 2`, `iteration = 3`, and `iteration = 4`. Each iteration dispatched an experiment to the oracle. Consequently:
- `iteration = 0` (Stage 0): Query 1 (`exp_00_<init_lbl>`)
- `iteration = 1` (Adaptive Step 1): Query 2 (`exp_01_<cand_lbl>`)
- `iteration = 2` (Adaptive Step 2): Query 3 (`exp_02_<cand_lbl>`)
- `iteration = 3` (Adaptive Step 3): Query 4 (`exp_03_<cand_lbl>`)
- `iteration = 4` (Adaptive Step 4): Query 5 (`exp_04_<cand_lbl>`)

Total oracle queries executed before loop termination was $1 + 4 = 5$.

#### Mechanism 3: Missing Budget Rejection in SimulationOracle
In `nomos/closed_loop/oracle.py`, `SimulationOracle` was constructed as an unconstrained query counter:
```python
class SimulationOracle:
    def __init__(self, simulator: Any, grid: Any):
        self._simulator = simulator
        self._grid = grid
        self._query_count = 0
```
`SimulationOracle` possessed no `max_budget` property and performed no rejection checks. Any component could call `execute_experiment()` indefinitely without raising an exception.

---

### 2. Impact on Discovery Outcomes & Scientific Validity

A critical question is whether any Tier 1 discoveries in M5.3 were achieved on Query 5. 

We performed an exhaustive cross-tabulation of `experiments_queried` against `tier` and `is_tier1_strict` across all 480 episodes in `audit/m5_3/BLIND_RAW_EPISODES.csv`:

| Queries Queried | Tier 1 (Exact Recovery) | Tier 2 (Support Recovery) | Tier 3 (Distractor) | Tier 6 (Failed / Non-Identifiable) | Total Episodes |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **2** | 143 | 9 | 14 | 149 | 315 |
| **3** | 13 | 8 | 0 | 13 | 34 |
| **4** | 2 | 1 | 1 | 5 | 9 |
| **5** | **0** | **1** | **0** | **121** | **122** |
| **Total** | **158** | **19** | **15** | **288** | **480** |

#### Key Scientific Finding:
**Zero Tier 1 governing-law discoveries occurred on Query 5.**
Out of 122 episodes reaching Query 5, 121 (99.2%) terminated in complete non-identifiability (Tier 6), and 1 terminated in Tier 2. All 158 Tier 1 discoveries in the repository occurred on or before Query 4 (143 at Query 2, 13 at Query 3, 2 at Query 4).

Therefore, strictly enforcing $B \le 4$ trajectory queries does not alter a single Tier 1 recovery or invalidate any paired statistical comparison.

---

### 3. Reconciled Budget Contract

To guarantee unbreachable budget integrity across Project NOMOS, the following architectural invariants are now enforced:

1. **Total Trajectory Budget Semantics:**  
   The budget parameter $B$ specifies the **strict upper bound on the total number of physical trajectory queries across the entire investigation**, inclusive of initial observations:
   $$\text{Total Queries} = Q_{\text{initial}} + Q_{\text{adaptive}} \le B$$
   For $B = 4$: Stage 0 consumes Query 1; at most 3 adaptive queries ($Q_{\text{adaptive}} \le 3$) are permitted.

2. **Hard Boundary Rejection in `SimulationOracle`:**  
   `SimulationOracle` accepts `max_budget: Optional[int]`. If `self._query_count >= self._max_budget`, `execute_experiment()` raises `BudgetExceededError`:
   ```python
   if self._max_budget is not None and self._query_count >= self._max_budget:
       raise BudgetExceededError(
           f"Simulation oracle query budget exhausted: maximum {self._max_budget} queries allowed."
       )
   ```

3. **Controller Loop Termination Tied to Oracle Counter:**  
   `ClosedLoopController` checks `self.oracle.query_count < self.max_budget`:
   ```python
   while (
       self.oracle.query_count < self.max_budget
       and status in (IdentifiabilityStatus.MULTIPLE_PLAUSIBLE_LAWS, IdentifiabilityStatus.INSUFFICIENT_EXCITATION)
   ):
       ...
   ```
   If the loop exits due to budget exhaustion without unique identification, `status` is explicitly set to `IdentifiabilityStatus.BUDGET_EXHAUSTED`.

---

### 4. Verification & Ledger Integration

The reconciled benchmark runner `experiments/m5_3_1/run_m5_3_1_benchmarks.py` records every oracle query to `audit/m5_3_1/ORACLE_CALL_LEDGER.csv` with:
- `episode_id`: Monotonically increasing episode index (1–480).
- `query_index`: 1-based index of query within the episode ($1 \le q \le 4$).
- `query_type`: `INITIAL` (Stage 0) or `ADAPTIVE` (Stages 1–5).
- `chosen_candidate`: Candidate experiment label selected by acquisition engine.
- `query_cost`: Resource cost (1.0).
- `cumulative_cost`: Cumulative queries executed in episode.
- `oracle_rejection_status`: `ACCEPTED` or `REJECTED_BUDGET_EXCEEDED`.

All 480 episodes strictly satisfy $Q \le 4$.
