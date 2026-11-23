# Project NOMOS — Milestone M2.1
## Formal Errata & Point-by-Point Scientific Claim Corrections

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** G01 (Adversarial Auditor), I01 (Certification Lead)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Purpose of this Document

This document serves as the permanent, version-controlled errata for the **Milestone M2 Executive Report** (`audit/m2/EXECUTIVE_REPORT.md`) and associated benchmark artifacts. In accordance with the scientific integrity principles of Project NOMOS, historical claims that failed adversarial verification are formally corrected, with exact mathematical explanations and code references.

---

### 2. Systematic Claim Correction Table

| Errata ID | Milestone M2 Claim / Text | Forensic Finding & Reality | Severity | Corrective Action & Versioned Resolution |
| :---: | :--- | :--- | :---: | :--- |
| **ERR-01** | *"Exact recovery achieved on Rational Kinetics: $\dot{x} = 0.5286 / x$"* (`audit/m2/EXECUTIVE_REPORT.md` Section 3.2) | **FALSE RECOVERY.** $0.5286 / x$ is mathematically non-equivalent to $\frac{2x}{1+x} - 0.5x$. It possesses a catastrophic singularity at $x \to 0$ ($+3,571\%$ error) and reverses sign at $x=10$. The true equation requires tree depth 4, whereas search was restricted to depth 3. | **HIGH (Scientific Defect)** | Evaluator updated to `nomos/evaluation/symbolic_classifier.py`. Success predicate repaired. Discovered expression reclassified as `ROLLOUT_ONLY_MATCH`. Exact recovery rate for Rational Kinetics corrected to **0.0%**. |
| **ERR-02** | *"SINDy baseline fails completely on the Harmonic Oscillator (0.0% recovery, test RMSE = 1.726)"* (`audit/m2/EXECUTIVE_REPORT.md` Table 2) | **ILL-POSED BENCHMARK ARTIFACT.** SINDy was evaluated with a degree-3 polynomial library on a single circular energy manifold ($x^2+v^2=1$). Linear and cubic terms are collinear along this manifold, causing rank deficiency. | **HIGH (Baseline Bias)** | Collinearity mathematically proved in `HARMONIC_BASELINE_FORENSICS.md`. SINDy re-evaluated under fair multi-orbit or degree-2 conditions: achieves **100% exact symbolic recovery with 0.0000 rollout error**. |
| **ERR-03** | *"Neural guidance accelerates equation discovery by steering search toward high-gradient regions"* (`audit/m2/EXECUTIVE_REPORT.md` Section 4.1) | **NOT DEMONSTRATED.** On low-dimensional systems ($n=2$), neural guidance evaluates the same candidate trees as unguided search and achieves identical exact recovery (20.0% vs 20.0%), while adding 0.38s–0.45s of MLP training overhead, making it **$20\times$ to $30\times$ slower** in wall-clock time. | **MEDIUM (Overstated Utility)** | Neural guidance claim revised from "Accelerated Search" to **"NOT DEMONSTRATED on low-dimensional benchmarks"**. Wall-clock time breakdown explicitly reported in `NEURAL_GUIDANCE_ABLATION.md`. |
| **ERR-04** | *"Evaluator predicate: `('/' in eq0 or 'div' in eq0) and (rollout_rmse < 1.0)` certifies exact recovery"* (`experiments/m2_comparison.py`) | **UNSOUND HEURISTIC.** Any equation with a division symbol that did not diverge within a short test rollout was marked exact. This conflated local trajectory interpolation with structural law recovery. | **HIGH (Methodological Defect)** | Completely excised. Replaced with formal 8-tier symbolic classifier incorporating SymPy canonical reduction, singularity checks, domain probing, and parameter tolerance testing. |
| **ERR-05** | *"100 distinct specialist agents autonomously executed Milestone M2"* (`audit/m2/SWARM_EXECUTION_AUDIT.md`) | **REPORTING INACCURACY.** 100 specialist roles were planned and registered in `AGENT_REGISTRY.json`, but execution was conducted via structured orchestrator waves rather than 100 concurrent OS subagent processes. | **LOW (Swarm Accounting)** | Ledger updated to distinguish explicitly between *Registered Specialist Roles* (100) and *Instantiated Execution Tasks* (waves), ensuring zero inflation of multi-agent claims. |

---

### 3. Policy on Historical Records

Historical milestone reports in `audit/m1/` and `audit/m2/` remain untouched as immutable historical records of project evolution. All corrections, errata, and updated scientific findings are formally codified in `audit/m2_1/` and integrated into the primary testing harness.
