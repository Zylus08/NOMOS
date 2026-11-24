# Project NOMOS — Milestone M5.3
## Source-to-Sink Hidden Information Flow Audit

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target Codebase Baseline:** Commit `bde9b56ef2d2cd9ef324e52bf6137e8142e99473`  
**Execution Timestamp:** November 2026  

---

### 1. Executive Summary

Milestone M5.2's adversarial review detected that `nomos/closed_loop/controller.py` inspects `field.pde_name` and uses system identity strings to inject candidate hypotheses pre-populated with ground-truth simulator parameters.

This audit maps the complete discovery call graph across Project NOMOS, tracking every pathway from simulation oracles to discovery engines, controllers, portfolios, and evaluators. Each discovered flow is classified under five strict epistemological categories:
- **CRITICAL LEAKAGE:** Privileged ground-truth information (names, parameters, or pre-engineered impostors) consumed by the learner to steer model selection or experiment acquisition.
- **POTENTIAL LEAKAGE:** System metadata exposed on observation objects that could be inspected by learning algorithms even if currently unconsumed.
- **PERMITTED MATHEMATICAL PRIOR:** Disclosed generic mathematical operators, polynomial bases, derivative orders, or space-time coordinate dimensions.
- **EVALUATOR-ONLY INFORMATION:** Ground-truth labels, parameters, and error metrics accessible strictly to grading harnesses after learner execution terminates.
- **BENIGN METADATA:** Non-identifying execution counters, timestamps, or opaque run identifiers.

---

### 2. Comprehensive Source-to-Sink Information Pathways

```
+----------------------------------------------------------------------------------------------------+
|                                    GROUND TRUTH SIMULATION ORACLE                                  |
|   Simulators: KdV, Burgers, Gray-Scott, FitzHugh-Nagumo, Navier-Stokes, Brusselator, Cahn-Hilliard |
|   Variables: self.parameters = {c, nu, Du, Dv, ...}, self.pde_name = "kdv", raw clean trajectories  |
+----------------------------------------------------------------------------------------------------+
                                                  |
                          Raw SpatiotemporalField (contains pde_name, u_clean, true_parameters)
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                              nomos/pde/isolation.py: create_learner_field_observation              |
|   Strips: u_clean -> None, u_t_true -> None, true_parameters -> None                               |
|   DEFECT: pde_name is PRESERVED on learner_obs! (Leakage Vector 1)                                |
+----------------------------------------------------------------------------------------------------+
                                                  |
                           learner_obs: SpatiotemporalField (pde_name="kdv_equation")
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                         nomos/closed_loop/controller.py: ClosedLoopController                      |
|   Pathway A: Weak-Form Fitting (Generic Library) -> hyp_wsindy                                     |
|   Pathway B: Beam Search Fitting (Generic Grammar) -> hyp_beam                                     |
|   CRITICAL LEAKAGE (Vector 2): if "kdv" in field.pde_name: inject hyp_linear_advection_impostor    |
|                                with ground truth speed u_x = -2.0000!                              |
|   CRITICAL LEAKAGE (Vector 3): In 2D, candidate_library = ["lap_v", "u*v^2", "v"] (No distractors) |
+----------------------------------------------------------------------------------------------------+
                                                  |
                               HypothesisPortfolio (Contains 2-3 hypotheses)
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                  nomos/closed_loop/acquisition.py                                  |
|   Computes D(u0; M1, M2) at t=0 over candidate pool. Clean mathematical operator evaluation.       |
|   DEFECT: candidate_pool[0] is engineered degenerate; candidate_pool[1/2] is engineered separator.|
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                  nomos/closed_loop/diagnostics.py                                  |
|   Stopping Audit: Delta BIC >= 10.0 triggers IDENTIFIED.                                           |
|   Halts immediately on Query 2 because the pre-seeded impostor is falsified by the wave packet!    |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                  Winning Hypothesis & Episode Summary
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                  experiments/m5/run_m5_benchmarks.py                               |
|   Evaluator compares winning hypothesis keys against true_terms.keys().                            |
+----------------------------------------------------------------------------------------------------+
```

---

### 3. Classification of Discovered Pathways

| ID | Source Component | Sink Component | Transmitted Data | Epistemological Classification | Severity |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **IF-01** | `nomos/pde/schema.py` | `controller.py:236-274, 296-348` | `field.pde_name` (`"kdv"`, `"burgers"`, `"gray_scott"`, etc.) | **CRITICAL LEAKAGE** | **FATAL** |
| **IF-02** | `controller.py:239-272` | `HypothesisPortfolio` | Hardcoded ground-truth parameters (`u_x: -2.0`, `u_xx: 0.05`, `lap_v: 0.08`, `lap_u: 1.0`, `lap_omega: 0.02`, `lap_u: 0.1`) | **CRITICAL LEAKAGE** | **FATAL** |
| **IF-03** | Benchmark Scripts (`run_m5_benchmarks.py`) | `controller.py:279` \& `weak_form_2d.py` | Minimalist candidate library matching exact ground-truth support without distractor features | **CRITICAL LEAKAGE** | **FATAL** |
| **IF-04** | `SimulationOracle` | `ClosedLoopController` | In-process Python object reference `self._simulator` in memory | **POTENTIAL LEAKAGE** | HIGH |
| **IF-05** | `nomos/pde/isolation.py:22` | `SpatiotemporalField` | `pde_name` preserved on learner observation object | **POTENTIAL LEAKAGE** | HIGH |
| **IF-06** | `nomos/data/isolation.py:22` | `TrajectoryDataset` | `system_name` exposed on ODE dataset wrapper | **POTENTIAL LEAKAGE** | MEDIUM |
| **IF-07** | `WeakFormPDEDiscovery` | `controller.py` | Disclosed generic 1D operator grammar (`["u", "u_x", "u_xx", "u_xxx", "u_xxxx", "u*u_x", "u^2", "u^3", "(u^3)_xx"]`) | **PERMITTED MATHEMATICAL PRIOR** | NONE |
| **IF-08** | Coordinate Grids (`Grid1D`, `Grid2D`, `TimeGrid`) | Learner \& Acquisition | Spatial dimensions, grid spacings ($dx, dy, dt$), coordinates ($x, y, t$), periodic boundary declarations | **PERMITTED MATHEMATICAL PRIOR** | NONE |
| **IF-09** | Evaluator Harness (`run_m5_benchmarks.py`) | Benchmark CSV Logs | `true_terms`, `true_keys`, parameter error computation, 6-tier recovery classification | **EVALUATOR-ONLY INFORMATION** | NONE |
| **IF-10** | `ExperimentResponse` | Controller Memory | `experiment_id`, resource costs, execution wall-clock time | **BENIGN METADATA** | NONE |

---

### 4. Detailed Forensic Breakdown of Critical Leakages

#### 4.1 Leakage Vector 1 & 2: `field.pde_name` and Ground-Truth Impostor Injection
In `nomos/closed_loop/controller.py` lines 234–275 and lines 294–348:
```python
# 1D Competing physical priors for active discrimination
if source_tag == "initial":
    if "kdv" in field.pde_name:
        h_adv = ScientificHypothesis(
            id="hyp_linear_advection_impostor",
            equation_str="u_t = -2.0000*u_x",
            features=["u_x"],
            parameters={"u_x": -2.0},  # Exactly c = 2.0!
            ...
        )
        self.portfolio.register(h_adv)
```
- **Why This Is Fatal:** The agent is claiming to perform "autonomous discovery of physical laws from observations". However, instead of discovering competing theories from the initial data, the controller inspects the hidden simulator's name (`field.pde_name`) and injects the exact degenerate mathematical competitor with calibrated physical parameters.
- **The Query 2 Artifact Explained:** At Query 1, the agent observes the solitary wave. Because `hyp_linear_advection_impostor` has $c = 2.0$, its residual on the solitary wave is $0.001$ ($\text{BIC} = 0.0$). At Query 2, the agent queries the wave packet, on which advection produces huge residual ($\text{MSE} = 4.82$). The true KdV model (discovered by WSINDy) fits the wave packet with low error, triggering $\Delta\text{BIC} \ge 10.0$ instantly.
- The entire "active discovery" loop was reduced to an engineered two-hypothesis discrimination game where both candidates were pre-cooked!

#### 4.2 Leakage Vector 3: 2D Minimalist Candidate Libraries
In `experiments/m5/run_m5_benchmarks.py` lines 145–160:
```python
("gray_scott_2d", sim_gs, g2d_gs, pool_gs, 2, "v", ["lap_v", "u*v^2", "v"], ...)
("fitzhugh_nagumo_2d", sim_fhn, g2d_fhn, pool_fhn, 2, "u", ["lap_u", "u", "u^3", "v"], ...)
("navier_stokes_2d", sim_ns, g2d_ns, pool_ns, 2, "omega", ["lap_omega", "(u*grad)omega"], ...)
```
- The candidate library passed to the 2D weak-form discovery engine was strictly restricted to the true terms. The sparse regression solver was never required to prune distractor terms (e.g. $u, v, u^2, \nabla^2 u$, cross-derivatives, etc.).

---

### 5. Mandated Remedies for Milestone M5.3

1. **Opaque Observation Protocol:** `SpatiotemporalField` visible to the learner must have `pde_name = "blind_system_<hash>"` or be completely absent.
2. **Autonomous Candidate Generation:** Remove all branching on `field.pde_name` or system names. The portfolio must be initialized exclusively by data-driven discovery engines:
   - WSINDy fit on observed data.
   - Scale-Adaptive Beam Search fit on observed data.
   - Self-supervised residual proposals (e.g. fitting models with different sparsification thresholds $\lambda \in [0.005, 0.10]$).
3. **Generic Overcomplete 2D Library:** Replace custom candidate libraries with a standard 2D polynomial and differential operator grammar containing at least 8 to 12 candidate basis functions, forcing genuine sparse feature selection.
4. **Independent Adversarial Tests:** Verify that renaming, shuffling, or changing simulator classes produces identical learner behavior.
