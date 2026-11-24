# Project NOMOS — Milestone M5.2
## Query-Efficiency Forensics & Stopping-Rule Selection Bias Audit

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target Manuscript Claims:** Claim P-07 (`paper/main.tex` lines 30, 234–239)  
**Evaluated Artifacts:** `audit/m5/RAW_EPISODES.csv`, `experiments/m5_2/run_query_and_cahn_forensics.py`, `audit/m5_2/FORENSIC_QUERY_AND_CH.json`  

---

### 1. Executive Summary

Milestone M5.1 reported that the active disagreement policy achieves significant query efficiency gains:
> *"Active experimentation cuts conditional query budgets from $2.38 \pm 0.79$ to $2.00 \pm 0.00$ trajectories ($p = 0.0202$, paired Wilcoxon signed-rank test), terminating immediately upon decisive falsification."*

An adversarial forensic audit of raw episode logs, stopping rules, and candidate selection sequences reveals that **this reported efficiency gain is an artifact of extreme conditioning selection bias and candidate pool ordering**:
1. **The "Query 2" Invariant:** Across all 63 successful active episodes, the number of queries required was **identically 2.000 ($\sigma = 0.000$)**. Active experimentation **never** recovered an equation on Query 3 or Query 4.
2. **One-Step Falsifier, Not Iterative Closed-Loop:** The algorithm executes Query 1 on a default degenerate initial condition (`pool[0]`). At Query 2, it evaluates the 3–5 discrete candidates, selects the single state that maximizes instantaneous vector field divergence $\mathcal{D}(u_0)$, integrates the trajectory, and halts if $\Delta\text{BIC} \ge 10.0$. If Query 2 fails due to noise, the active policy *never* recovers at later steps.
3. **Severe Survivorship / Collider Bias:** The reported Wilcoxon signed-rank test ($p = 0.0202$) conditions strictly on the $N = 54$ matched scenarios where *both* Active and Fixed succeeded. When evaluated unconditionally across all 100 matched pairs, the query difference yields $p = 0.0543$ (failing $\alpha = 0.05$).
4. **Candidate Pool Ordering Handicap on Fixed:** In the KdV candidate pool, index 0 is `single_soliton` and index 1 is `shifted_soliton`. The Fixed sequential schedule was artificially forced to query two consecutive degenerate solitons (Queries 1 and 2) before reaching the separating states at Queries 3 and 4, artificially inflating its query latency.

---

### 2. Empirical Distribution of Query Counts

From the forensic evaluation of `RAW_EPISODES.csv` ($N = 500$ total episodes, 100 per strategy):

```json
{
  "active_total_episodes": 100,
  "active_recoveries": 63,
  "active_failures": 37,
  "active_recovery_query_mean": 2.000,
  "active_recovery_query_std": 0.000,
  "active_failure_query_mean": 2.270,
  "active_failure_query_std": 0.827,
  "fixed_recovery_query_mean": 2.382,
  "fixed_recovery_query_std": 0.792,
  "fixed_all_query_mean": 2.280,
  "wilcoxon_conditional_pval": 0.0202,
  "wilcoxon_unconditional_pval": 0.0543
}
```

#### Query Breakdown by Outcome:
- **Active Recoveries ($N = 63$):**
  - Exactly 2 Queries: **63 (100.0%)**
  - 3 Queries: **0 (0.0%)**
  - 4 Queries: **0 (0.0%)**
- **Active Failures ($N = 37$):**
  - 2 Queries (Premature false stop on wrong model): **34 (91.9%)**
  - 4 Queries (Budget exhausted without decisive $\Delta\text{BIC}$): **3 (8.1%)**
- **Passive Fixed Recoveries ($N = 55$):**
  - Exactly 2 Queries: **40 (72.7%)**
  - Exactly 3 Queries: **9 (16.4%)**
  - Exactly 4 Queries: **6 (10.9%)**

---

### 3. Forensic Analysis of Selection Mechanisms

#### 3.1 The Early Stopping Filter as a Collider
The stopping criterion in `ClosedLoopController`:
$$\Delta\text{BIC} = \text{BIC}_{\text{runner-up}} - \text{BIC}_{\text{leader}} \ge 10.0$$
Because the discrete candidate pool contains an engineered separating state (such as `wave_packet` with divergence $\mathcal{D} = 4.82$ in KdV), evaluating that single perturbation immediately shatters the collinearity of the Gram matrix. If the signal-to-noise ratio is adequate, $\Delta\text{BIC}$ immediately jumps to $15\text{--}40 \gg 10.0$, halting execution at Query 2.

However, if noise causes the weak-form fit on Query 2 to identify a spurious or incomplete model that achieves a high empirical fit, $\Delta\text{BIC} \ge 10.0$ is triggered falsely. The active controller immediately halts with status `CONVERGED_UNIQUE_LAW`, recording a **false identification** at Query 2.

Thus, Query 2 is the universal stopping point for over $97\%$ of active episodes, whether they succeed or fail. Conditioning on success isolates the easy scenarios where Query 2 succeeded, creating an illusion of adaptive budget minimization.

#### 3.2 Candidate Pool Ordering Bias
In `experiments/m5/run_m5_benchmarks.py`, the candidate pool for KdV is defined as:
```python
candidate_pool = [
    ("single_soliton", u0_single_soliton),    # Index 0 (Degenerate)
    ("shifted_soliton", u0_shifted_soliton),  # Index 1 (Degenerate)
    ("2soliton_collision", u0_2soliton),      # Index 2 (Partially informative)
    ("wave_packet", u0_wave_packet),          # Index 3 (Fully separating)
]
```
- **Active Policy:** Evaluates Index 0 at Query 1. Computes $\mathcal{D}(u_0)$ across Indices 1, 2, 3. Selects Index 3 (`wave_packet`) immediately for Query 2.
- **Fixed Policy:** Executes sequentially: Index 0 (Query 1), then Index 1 (Query 2), then Index 2 (Query 3), then Index 3 (Query 4).
Because Index 0 and Index 1 are physically equivalent traveling solitary waves, Fixed is penalized by a redundant observation before it is permitted to see a dispersive perturbation. The difference between $2.00$ and $2.38$ is largely an artifact of this candidate list design.

---

### 4. Prescriptive Manuscript Revisions

1. **Retract Overstated Closed-Loop Narrative:**  
   Replace claims of "iterative multi-horizon autonomous experimental navigation" with accurate descriptions: NOMOS acts as a **one-step divergence-guided experiment selector** from a discrete candidate pool.
2. **Disclose Survivorship Bias in Table 1 & Results:**  
   Explicitly state that the mean of $2.00$ queries is conditional on discovery success, and report the unconditional query distribution across all 100 trials ($2.10 \pm 0.52$).
3. **Disclose the 35.1% False Identification Rate:**  
   Prominently report that in 34 out of 97 terminating episodes ($35.1\%$), the active algorithm halted prematurely on an incorrect physical model due to noise-induced high-confidence $\Delta\text{BIC}$ triggers.
