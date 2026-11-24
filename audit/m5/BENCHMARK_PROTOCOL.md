# Project NOMOS — Milestone M5
## Canonical Benchmark Protocol: Autonomous Closed-Loop Physical Law Discovery

**Principal Investigator / Git Identity:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Milestone:** M5 — Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery  
**Target Systems:** KdV, Viscous Burgers, Gray-Scott 2D, FitzHugh-Nagumo 2D, Navier-Stokes 2D  

---

### 1. Benchmark Objective & Scope

The objective of the Milestone M5 benchmark protocol is to evaluate whether active closed-loop experimentation yields a statistically significant and reproducible advantage in governing-law discovery compared to passive, random, and uncoordinated acquisition strategies under strictly matched observation budgets.

The matrix evaluates:
- **5 Physical Dynamical Systems:**
  1. Korteweg-de Vries (KdV) Equation (1D nonlinear dispersive wave)
  2. Viscous Burgers' Equation (1D nonlinear advective-diffusive shock)
  3. Gray-Scott Reaction-Diffusion (2D coupled Turing pattern formation)
  4. FitzHugh-Nagumo Reaction-Diffusion (2D excitable neural media)
  5. Incompressible Navier-Stokes Equations (2D vorticity-streamfunction fluid dynamics)
- **5 Experiment Acquisition Strategies:**
  1. `greedy_disagreement`: Functional vector-field divergence maximization between top competing hypotheses.
  2. `cost_normalized`: Vector-field disagreement normalized by multi-resource experimental cost.
  3. `uncertainty_aware`: Predictive variance across Bayesian evidence-weighted hypothesis ensemble.
  4. `fixed`: Deterministic sequential schedule (standard fixed-condition experimental design).
  5. `random`: Uniform stochastic selection over the admissible experiment pool.
- **4 Noise Levels:** $0\%$, $1\%$, $5\%$, $10\%$ additive Gaussian observation noise.
- **5 Random Seeds:** $42, 43, 44, 45, 46$.
- **Total Executed Episodes:** $5 \times 5 \times 4 \times 5 = 500$ complete closed-loop investigations.

---

### 2. Strict Observation Budget Matching

To ensure rigorous scientific validity, active and passive strategies operate under strictly matched observation constraints:
- **Maximum Budget ($B_{max}$):** 4 trajectory queries per investigation episode.
- **Time Horizon:** $T = 0.5$ ($M = 30$ temporal snapshots per trajectory).
- **Spatial Discretization:**
  - 1D Systems: $N = 128$ points for KdV ($[-10, 10]$), $N = 64$ points for Burgers ($[0, 2\pi]$).
  - 2D Systems: $32 \times 32$ spatial grids ($1,024$ spatial points per snapshot).
- **Total Spatiotemporal Volume:**
  - 1D: $V = \Delta x \cdot \Delta t \cdot N \cdot M$.
  - 2D: $V = \Delta x \cdot \Delta y \cdot \Delta t \cdot N_x \cdot N_y \cdot M$.
Every strategy accesses identically constrained simulation oracles. No strategy is allowed additional data queries.

---

### 3. Physical Quarantine & Information Boundary

1. **Quarantine Sandbox:** The discovery agent never interacts with simulator internals. All queries pass through `SimulationOracle.execute_experiment(req)`.
2. **Observation Sanitization:** `create_learner_field_observation` strictly purges:
   - Ground truth simulator references (`_simulator`, `simulator`).
   - Clean field trajectories (`u_clean = None`).
   - Ground truth time derivatives (`u_t_true = None`).
   - Hidden physical parameters (`true_parameters = None`).
3. **No Leakage:** Acquisition scoring functions and stopping criteria evaluate only observed field trajectories and discovered candidate models; they have zero access to the simulator's true parameter values.

---

### 4. Evaluation Criteria & Certification Metrics

1. **Exact Support Recovery ($S_{exact}$):** True differential operators are recovered without spurious terms (extraneous terms must have coefficient $< 0.04$ or be absent).
2. **Parameter Accuracy:** Recovered coefficients must be within $25\%$ of ground truth physical constants.
3. **Sample Efficiency:** Number of trajectory queries required before reaching conclusive statistical identifiability ($\Delta \text{BIC} \ge 10$).
4. **Falsification Ratio:** Predictive residual divergence between true physical law and competing impostor hypotheses on acquired states.
