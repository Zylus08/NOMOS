# Project NOMOS — Milestone M5.1
## Independent Closed-Loop Behavior, Candidate Generation & Shortcut Audit

**Review Role:** Independent Peer Review & Code Auditor  
**Auditor / Git Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Inspected Source Files:**
- `nomos/closed_loop/controller.py`
- `nomos/closed_loop/portfolio.py`
- `nomos/closed_loop/oracle.py`
- `nomos/closed_loop/acquisition.py`
- `nomos/closed_loop/diagnostics.py`

---

### 1. Verification of the 8-Stage Closed-Loop Cycle

The controller loop in `ClosedLoopController.run_investigation()` was audited line-by-line:
1. **`OBSERVE` (Initial):** In Step 0, an initial default observation is queried from `SimulationOracle` (e.g., single soliton for KdV, unperturbed diffusion, or Taylor-Green vortex).
2. **`HYPOTHESIZE` (Step 0):** `_generate_initial_hypotheses()` executes discovery engines (1D/2D WSINDy and Beam Search) on the initial observation to formulate candidate models.
3. **`COMPARE`:** Active hypotheses are registered in `HypothesisPortfolio`, sorted by validation error / BIC, and normalized evidence weights are assigned.
4. **`DESIGN`:** `ExperimentAcquisitionEngine.select_experiment()` evaluates the candidate experiment pool using vector-field divergence $\mathcal{D}(u_0; h_1, h_2) = \| f_{h_1}(u_0) - f_{h_2}(u_0) \|_2^2$ or cost-normalized gain.
5. **`EXPERIMENT`:** The selected initial condition $u_0^*$ is dispatched to `SimulationOracle.execute_experiment()`, returning sanitized spatio-temporal observations without true parameters or derivatives.
6. **`UPDATE`:** The newly acquired trajectory generates updated candidate hypotheses; parameters of surviving hypotheses are evaluated on the new observations.
7. **`VALIDATE`:** Weak-form residual errors are computed. Hypotheses whose residual error exceeds a statistical falsification threshold ($> 5\times \min(\text{MSE})$ and normalized error $> 5\%$) are permanently marked `FALSIFIED` with explicit rejection reasons.
8. **`STOP`:** `IdentifiabilityAuditor.audit_portfolio()` evaluates Kass-Raftery Bayes factor evidence ($\Delta \text{BIC} \ge 10$) and validation ratios. If a single physical law decisively dominates, it halts with `status = IDENTIFIED`.

---

### 2. Audit of Preloaded Ground-Truth Hypotheses & Shortcuts

**Auditor Red Flag & Critical Finding:**
In `nomos/closed_loop/controller.py` (lines 235–275), the method `_generate_initial_hypotheses` contained string matching:
```python
if source_tag == "initial":
    if "kdv" in field.pde_name:
        # injects hyp_linear_advection_impostor
    elif "burgers" in field.pde_name:
        # injects hyp_linear_diffusion_impostor
    elif "gray_scott" in field.pde_name:
        # injects hyp_gs_diffusion_only
    elif "fitzhugh" in field.pde_name:
        # injects hyp_fhn_diffusion_only
    elif "navier_stokes" in field.pde_name:
        # injects hyp_stokes_decay_impostor
```

#### Evaluation:
1. **Is this a canned shortcut to success?**
   **NO.** These injected hypotheses are *impostor models* (competing physical degeneracies that mimic the true dynamics on uninformative observations), NOT the true governing equations!
   For example, on KdV, the impostor is linear advection ($u_t = -2 u_x$), whereas true KdV is $u_t = -u_{xxx} - 6 u u_x$.
   The presence of these impostors forces the discovery engine to design an experiment that actively falsifies them!
2. **However, does it represent benchmark-specific hardcoding?**
   **YES.** Hardcoding string matches (`if "kdv" in field.pde_name`) violates the principle of a general-purpose discovery agent. In open-ended discovery, competing hypotheses must be generated autonomously from the data (e.g., lower-order polynomial models, sparse subsets, or alternative Pareto candidates from beam search) rather than handcrafted per benchmark name.
3. **M5.1 Audit Recommendation:**
   The controller's data-driven candidate generation (WSINDy and Differential Beam Search) naturally discovers these degenerate models when fitted to uninformative data (e.g., Beam Search discovered $u_t = -1.9346 u_x$ on the single soliton without any hardcoded prior!). The handcoded impostor injection is redundant and should be recognized as an explicit limitation of the M5 benchmark scaffolding.

---

### 3. Fully Traced Adversarial Investigation (KdV Soliton vs Packet)

A live traced investigation was executed to audit the exact transition from an incorrect model to the true governing equation:
- **Step 0 (Soliton Observation):**
  - WSINDy discovered: $u_t = +10.8383 u_x - 6.3763 u_{xxx} - 38.4479 u u_x$
  - Beam Search discovered: $u_t = -1.9346 u_x - 0.0266 u_{xxx} - 0.1891 u u_x$
  - Competing prior: $u_t = -2.0000 u_x$
  - On the solitary wave, both linear advection and the beam model fit the trajectory ($\text{MSE} \approx 0.0029$).
- **Step 1 (Acquisition & Experiment):**
  - Divergence score: Shifted soliton $\mathcal{D} = 2.05$, Oscillatory wave packet $\mathcal{D} = 519.91$.
  - Agent selected: `wave_packet`.
  - Oracle simulated wave packet and returned sanitized field.
- **Step 1 (Update & Falsification):**
  - On the wave packet, linear advection weak-form residual MSE was $0.004931$.
  - Newly formulated WSINDy model on wave packet: $u_t = -0.9978 u_{xxx} - 5.9440 u u_x$ with residual MSE $= 0.000020$.
  - Falsification ratio: $\frac{0.004931}{0.000020} = 246.55 \gg 5.0$.
  - `hyp_linear_advection_impostor` and initial beam models were marked `FALSIFIED`.
  - True KdV model achieved $\text{BIC} = -632.02$ vs runner-up $\text{BIC} = -341.05$ ($\Delta \text{BIC} = 290.97 \gg 10$).
  - Auditor declared `status = IDENTIFIED` with winning equation: $u_t = -0.9978 u_{xxx} - 5.9440 u u_x$.

**Conclusion:** The closed-loop controller genuinely refits models, evaluates out-of-distribution predictive residuals, and falsifies incorrect models based entirely on empirical evidence.
