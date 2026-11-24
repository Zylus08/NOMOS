# Project NOMOS — Milestone M5.3
# Zero-Leakage Blind Benchmark Protocol

**Date:** 2026-11-25  
**Auditor & Orchestrator:** Chief Scientific Integrity Auditor  
**Execution Script:** [`experiments/m5_3/run_blind_benchmarks.py`](file:///e:/NOMOS/experiments/m5_3/run_blind_benchmarks.py)  
**Primary Dataset:** [`audit/m5_3/BLIND_RAW_EPISODES.csv`](file:///e:/NOMOS/audit/m5_3/BLIND_RAW_EPISODES.csv) (480 episodes)  
**Matched Pairs:** [`audit/m5_3/BLIND_PAIRED_OUTCOMES.csv`](file:///e:/NOMOS/audit/m5_3/BLIND_PAIRED_OUTCOMES.csv) (100 matched pairs)

---

## 1. Experimental Design & Quarantine Boundary

The Milestone M5.3 Blind Replication Benchmark Matrix tests whether active closed-loop experiment selection outperforms passive experiment selection under strict zero-leakage conditions.

### Quarantine Safeguards
1. **Opaque System Identity**: All observation fields passed to the learner have `field.pde_name` replaced by `blind_system_<hash>`. No system identity strings (`kdv`, `burgers`, `gray_scott`, `fitzhugh`, `navier_stokes`) are accessible to discovery algorithms.
2. **Autonomous Candidate Proposal**: Hardcoded impostor seeding blocks were completely deleted. Hypotheses are proposed dynamically via multi-threshold WSINDy ($\lambda \in \{0.015, 0.045, 0.12\}$), Differential Beam Search, and least-squares parsimonious sub-model extraction $(G_j^T G_j)^{-1} G_j^T b$.
3. **Overcomplete Candidate Libraries**: Candidate libraries are not tailored minimal bases. Every system is evaluated against an overcomplete library containing genuine distractor terms (e.g. 5 operators for KdV/Burgers, 5-6 operators for Gray-Scott, FitzHugh-Nagumo, and Navier-Stokes).
4. **Universal Multi-Field Validation**: Any active hypothesis is audited against all accumulated historical experimental fields, enforcing physical law invariance across regimes.

---

## 2. Experimental Dimensions & Combinatorics

The benchmark matrix consists of:
- **5 Primary Physical Systems**:
  1. *KdV Equation* (1D nonlinear dispersion): $u_t = -6 u u_x - u_{xxx}$
  2. *Viscous Burgers* (1D nonlinear advection-diffusion): $u_t = -u u_x + 0.05 u_{xx}$
  3. *Gray–Scott 2D* (Coupled reaction-diffusion, $v$-channel): $v_t = 0.08 \nabla^2 v + u v^2 - 0.095 v$
  4. *FitzHugh–Nagumo 2D* (Excitable media, $u$-channel): $u_t = 1.0 \nabla^2 u + u - u^3 - v$
  5. *Navier–Stokes 2D* (Incompressible fluid vorticity): $\omega_t = 0.02 \nabla^2 \omega - (\mathbf{u} \cdot \nabla) \omega$
- **2 Held-Out Replication Systems**:
  6. *Brusselator 2D* (Coupled autocatalytic oscillator): $u_t = 0.1 \nabla^2 u + 1.0 - 4.0 u + u^2 v$
  7. *Cahn–Hilliard 1D* (Phase separation with biharmonic damping): $u_t = -u_{xx} + (u^3)_{xx} - 0.01 u_{xxxx}$
- **4 Acquisition Strategies**:
  - `greedy_disagreement`: Active selection maximizing predictive variance among rival active hypotheses.
  - `cost_normalized`: Active selection maximizing disagreement per unit observation cost.
  - `random`: Passive uniform random selection from the candidate initial condition pool.
  - `fixed`: Passive deterministic sequential polling (representing standard non-adaptive laboratory protocols).
- **4 Noise Levels**: $\sigma \in \{0.0, 0.01, 0.05, 0.10\}$ (additive Gaussian noise relative to field standard deviation).
- **5 Matched Random Seeds**: $S \in \{42, 43, 44, 45, 46\}$.
- **Maximum Experimental Budget**: $B = 4$ active queries per episode (total trajectory queries $\le 5$).

### Total Runs
- Primary: $5 \times 4 \times 5 \times 4 = 400$ episodes.
- Held-Out: $2 \times 4 \times 5 \times 2 = 80$ episodes.
- Total: **480 fully audited autonomous closed-loop episodes**.
- Total Execution Duration: 599.02 seconds (Intel Core i7-12650H, 16 GB RAM).

---

## 3. Strict Tier 1 Evaluation Protocol

Every completed episode was evaluated against analytical ground-truth physics using [`experiments/m5_3/reconcile_metrics.py`](file:///e:/NOMOS/experiments/m5_3/reconcile_metrics.py):
- **Tier 1 (Strict Exact Recovery)**:
  $$\operatorname{supp}(\hat{\xi}) = \operatorname{supp}(\xi^*) \quad \wedge \quad \max_{j} \frac{\|\hat{\xi}_j - \xi^*_j\|}{\|\xi^*_j\|} \le 10\%$$
- Any episode with unpruned distractors, missing terms, or parameter error $> 10\%$ was classified as non-Tier 1.
