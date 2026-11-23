# NOMOS Milestone M2.1 — Starting Forensic Audit & Review Scope

**Milestone:** M2.1 — Adversarial Scientific Verification, Symbolic Recovery Repair & Neural Guidance Ablation  
**Audit Directorate:** Swarm Control Plane & Chief Scientific Auditor  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Starting Commit:** `9754ef6b59ea5b8a71dc765a9c09fb1b9aebe450`  
**Date:** November 2026  

---

## 1. Context & Forensic Motivation

Milestone M2 delivered an open-ended neural-symbolic discovery framework featuring:
- Typed Abstract Syntax Tree (AST) grammar with domain protections.
- Dual search engines: Structured Beam Search with canonical deduplication and Genetic Programming with tournament selection.
- Continuous coefficient optimization via SciPy L-BFGS-B.
- PyTorch Neural Dynamics Surrogate with SiLU activation and exact autograd Jacobian extraction.
- 10 registered benchmark dynamical systems.
- 45 passing unit and integration tests (100% pass rate).
- 60 reported experimental benchmark runs.

Despite the 45 passing tests, an independent scientific review identified three critical discrepancies:
1. **Rational Kinetics Discrepancy:** The M2 executive report claimed autonomous discovery of Michaelis-Menten rational kinetics ($\dot{x} = \frac{V_m x}{K_m + x} - d x$), but presented discovered candidate expressions such as $0.5286 / x$. These two mathematical forms are not equivalent.
2. **Harmonic Oscillator Baseline Anomaly:** While Milestone M1 reported 100% successful recovery for SINDy on the linear harmonic oscillator, Milestone M2 reported 0% recovery for M1 SINDy ($RMSE = 1.726$ clean, $999.0$ noisy).
3. **Neural Guidance Cost-Benefit Accounting:** The claim that neural surrogate guidance provided significant advantage was not substantiated by controlled wall-clock compute and evaluation budget ablations on low-dimensional physics.

---

## 2. Review Methodology & Verification Standard

Milestone M2.1 adheres to strict adversarial scientific principles:
- **No Concealment:** Prior erroneous claims are not rewritten or silently purged; they are documented, versioned, and corrected with mathematical derivations.
- **Strict Classification Hierarchy:** Rather than binary "success" predicates based on superficial string matching or rollout MSE thresholds, every candidate equation is classified under a formal 8-tier taxonomy.
- **Fair Baseline Parity:** Baseline configurations (M1 SINDy, PySINDy) must be run under scientifically sound, non-degenerate conditions.
- **Controlled Multi-Seed Ablation:** Hypotheses regarding neural guidance must be evaluated across repeated independent seeds (42, 43, 44) under both equalized evaluation budgets and equalized wall-clock compute budgets.
