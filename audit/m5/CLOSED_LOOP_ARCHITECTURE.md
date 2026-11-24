# Project NOMOS — Milestone M5
## Autonomous Closed-Loop Scientific Controller Architecture

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M5 Phase 1 Specification  
**Date:** 2026-11-24  

---

### 1. Architectural Philosophy & Objective

Milestone M5 transforms Project NOMOS from an offline, batch model-fitting framework into a **genuinely closed-loop autonomous scientific discovery agent**.
The agent actively selects informative physical experiments to resolve structural degeneracies, falsify impostor models, and identify true physical laws under constrained observation budgets.

---

### 2. The 8-Stage Closed-Loop Cycle

```
[OBSERVE] ----> [HYPOTHESIZE] ----> [COMPARE] ----> [DESIGN]
    ^                                                   |
    |                                                   v
 [VALIDATE] <---- [UPDATE] <---- [EXPERIMENT] <---------+
    |
    v
  [STOP] (Audit Identifiability & Budget)
```

1. **OBSERVE (`nomos/closed_loop/controller.py`):**
   Ingests measured spatiotemporal trajectory fields, spatial coordinates, timestamps, and uncertainty bounds.
2. **HYPOTHESIZE (`_generate_initial_hypotheses`):**
   Formulates candidate physical governing laws using weak-form integral regression (WSINDy) and scale-adaptive differential AST beam search.
3. **COMPARE (`portfolio.compute_evidence_weights`):**
   Quantifies model uncertainty, computing relative Bayesian evidence scores ($w_i \propto \exp(-\frac{1}{2} \Delta \text{BIC}_i)$) and evaluating functional vector-field divergence.
4. **DESIGN (`acquisition.select_experiment`):**
   Selects the next experimental configuration (e.g., initial state $u_0$ or boundary excitation) maximizing expected information gain or model disagreement.
5. **EXPERIMENT (`oracle.execute_experiment`):**
   Dispatches an `ExperimentRequest` to the sandboxed `SimulationOracle`. Strictly receives sanitized observations without hidden parameters or true derivatives.
6. **UPDATE (`_update_and_validate_hypotheses`):**
   Incorporates new observations, refits parameters, updates hypothesis evidence scores, and records supporting or contradicting evidence.
7. **VALIDATE:**
   Assesses predictive performance on held-out trajectories to falsify inconsistent models ($\text{Error} > 5 \times \min(\text{Error})$).
8. **STOP (`auditor.audit_portfolio`):**
   Evaluates statistical stopping criteria: decisive evidence margin ($\Delta \text{BIC} \ge 10$), budget exhaustion, or information plateau. Ground-truth equations are never accessed.
