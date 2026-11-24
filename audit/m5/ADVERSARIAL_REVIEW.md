# Project NOMOS — Milestone M5
## Independent Adversarial Review & Scientific Falsification Audit

**Review Role:** Independent Chief Scientific Auditor & Falsification Specialist  
**Auditor Principal Investigator / Git Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Milestone Under Review:** M5 — Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery  

---

### 1. Executive Summary & Audit Scope

This adversarial review independently investigates the empirical claims, statistical rigor, information boundaries, and numerical stability of Milestone M5. 

We subjected the closed-loop system to adversarial testing across four failure vectors:
1. **Adversarial Initial Condition Degeneracy:** Can active acquisition be tricked by states where competing hypotheses predict identical dynamics?
2. **Oracle Information Leakage Attack:** Does the acquisition function or stopping diagnostic leak ground-truth parameters or clean simulator fields?
3. **Budget Fairness & Cheating:** Does active experimentation gain an unfair advantage through hidden extra trajectory queries or volume?
4. **Statistical Overclaiming:** Are $p$-values inflated or computed using inappropriate parametric assumptions?

---

### 2. Adversarial Findings & Resolution

#### Finding 1: Soliton Indistinguishability Degeneracy
- **Adversarial Probe:** We evaluated KdV against linear advection on single traveling solitary waves $u_0(x) = c \cdot \text{sech}^2(\sqrt{c} x / 2)$.
- **Auditor Verification:** On a single soliton, the weak-form residuals of linear advection ($u_t = -c u_x$) and KdV ($u_t = -6 u u_x - u_{xxx}$) differ by less than $1.1\%$ ($\text{Ratio} \approx 0.989$). Neither hypothesis can falsify the other.
- **Defense Verification:** When presented with candidate initial conditions, active acquisition computed divergence $\mathcal{D} = 0.0$ for shifted solitons, but scored $\mathcal{D} = 12.65$ on dispersive wave packets and $\mathcal{D} = 8.42$ on 2-soliton collisions. The agent autonomously bypassed the solitary waves and acquired the wave packet, yielding a decisive falsification ratio $> 1500\times$, conclusively falsifying linear advection.

#### Finding 2: Simulation Oracle Quarantine Integrity
- **Adversarial Probe:** We inspected all attributes and memory references of `ExperimentResponse.field` returned by `SimulationOracle`.
- **Auditor Verification:**
  - `field.true_parameters` is strictly `None`.
  - `field.u_clean` is strictly `None`.
  - `field.u_t_true` is strictly `None`.
  - `field._simulator` does not exist.
  - `resp.simulator` does not exist.
  - All learner observations pass through `create_learner_field_observation` in `nomos/pde/isolation.py`.
- **Result:** **PASSED**. No ground-truth parameters, true equations, or simulator states leak to the discovery engine.

#### Finding 3: Observation Budget Parity
- **Adversarial Probe:** Did active experimentation secretly use more data than passive baselines?
- **Auditor Verification:** We audited the raw query counters in `audit/m5/RAW_EPISODES.csv`:
  - Active mean queries: $2.10 \le 4.0$
  - Fixed mean queries: $2.28 \le 4.0$
  - Random mean queries: $2.17 \le 4.0$
- **Result:** **PASSED**. Observation budgets were strictly capped at $B_{max} = 4$ trajectories across all strategies. Active experimentation succeeded in *fewer* observations, not more.

#### Finding 4: Non-Parametric Statistical Robustness
- **Adversarial Probe:** Is the reported advantage statistically defensible under rigorous scrutiny?
- **Auditor Verification:**
  - McNemar's test with continuity correction on $2 \times 2$ table yields $\chi^2 = 4.9000$ ($p = 0.0268$).
  - Exact binomial test on 10 discordant pairs ($b=9, c=1$) yields $p = 0.010742 < 0.05$.
  - Against random sampling, discordant pairs ($b=18, c=1$) yield $p = 0.000038 < 10^{-4}$.
  - Wilcoxon test on query budgets yields $W = 29.5, p = 0.0202 < 0.05$.
- **Result:** **PASSED**. The active experimentation advantage is genuine, statistically significant, and verified by exact tests.
