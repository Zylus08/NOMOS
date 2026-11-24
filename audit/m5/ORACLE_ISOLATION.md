# Project NOMOS — Milestone M5
## Simulation Oracle Quarantining & Data Leakage Prevention Audit

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M5 Security & Physical Isolation Specification  
**Date:** 2026-11-24  

---

### 1. The Physical Quarantine Boundary

In closed-loop scientific experimentation, the discovery agent must interact with nature (or simulation oracles) exclusively through **sanitized experimental interfaces**.
`SimulationOracle` (`nomos/closed_loop/oracle.py`) establishes an unbreachable quarantine:

```
+---------------------------------------------------------------+
|                      Discovery Agent                          |
|  - Hypothesis Portfolio (Memory)                              |
|  - Acquisition Engine (Disagreement / Variance)               |
|  - Stopping Auditor (Delta BIC / Bayes Factor)                |
+---------------------------------------------------------------+
                               |
                   ExperimentRequest(u0, t_span, noise)
                               v
==================== QUARANTINE BOUNDARY ========================
                               ^
                   ExperimentResponse(learner_obs, cost)
                               |
+---------------------------------------------------------------+
|                      Simulation Oracle                        |
|  - True Simulator Internals (Hidden)                          |
|  - Analytical Derivations & Parameters (Hidden)               |
|  - Data Sanitization Sandbox (`nomos/pde/isolation.py`)       |
+---------------------------------------------------------------+
```

---

### 2. Information Sanitization Checklist

1. **`u_clean` Purged:** The agent receives noisy observations `u`; the noiseless truth is stripped.
2. **`u_t_true` Purged:** Exact temporal analytical derivatives are withheld; the agent must compute numerical rates or weak-form integrals.
3. **`true_parameters` Purged:** Physical constants ($D_u, D_v, \nu, c$) are completely inaccessible.
4. **Acquisition Isolation:** Acquisition functions evaluate *learned surrogate functions*, never querying the simulator during candidate scoring.
5. **Stopping Isolation:** Stopping audits depend strictly on observable validation residuals and evidence margins, never on distance to hidden truth.
