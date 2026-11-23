# Project NOMOS — Milestone M4
## Neural Guidance Ablation & Compute-Matched Performance Audit

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 7 Scientific Novelty & Ablation Closure  
**Date:** 2026-11-23  

---

### 1. Executive Summary & Scientific Mandate

In Milestone M3 and Milestone M4, a 1D/2D convolutional dynamics neural surrogate (`NeuralPDESurrogateTrainer`) was evaluated as a heuristic guidance mechanism for differential AST beam search.
Under the mandatory scientific integrity criteria of Project NOMOS:
> *"If neural guidance cannot demonstrate statistically significant recovery improvement under matched wall-clock compute budgets, its claim of algorithmic contribution must be reported as NOT DEMONSTRATED."*

This audit reports the rigorous ablation results comparing unguided symbolic search against neural-guided symbolic search across compute-matched and unconstrained evaluation budgets.

---

### 2. Empirical Performance Comparison (Compute & Recovery)

| Evaluation Condition | Search Mode | Mean Execution Time | Exact Support Recovery | Spurious Term Rate | Compute Efficiency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Fixed Time Budget ($0.02$s)** | **Pure Beam Search** | **0.0105 s** | **100% (6/6 systems)** | **0.0%** | **Baseline (1.0x)** |
| Fixed Time Budget ($0.02$s) | Neural-Guided Beam | Timeout (> 0.02s) | 0.0% (Incomplete) | N/A | Fails Budget Gate |
| **Unconstrained Budget** | Pure Beam Search | 0.0105 s | 100% (6/6 systems) | 0.0% | $17.7\times$ faster |
| Unconstrained Budget | Neural-Guided Beam | 0.1855 s | 100% (6/6 systems) | 0.0% | $17.7\times$ slower |

---

### 3. Forensic Analysis of Algorithmic Contribution

1. **Surrogate Training Overhead:**
   Training the neural dynamics surrogate takes $\approx 0.175$ seconds, which represents over $94\%$ of the total execution time of the neural-guided pipeline.
2. **Support Identification Redundancy:**
   Once scale-adaptive complexity penalty ($\text{Score} = \text{MSE}/\operatorname{Var}(u_t) + \lambda_c K$) is applied, the objective landscape of differential AST search has well-conditioned minima at the true physical equations. The Jacobian sensitivity priors supplied by the neural network alter the relative score order of suboptimal candidate branches, but **never change the globally optimal model**.
3. **Matched Compute Defeat:**
   Under equal wall-clock compute budgets (e.g. 0.02s), pure beam search completes evaluation of single, dual, and triple candidate terms exhaustively, whereas neural surrogate training does not even finish its first epoch.

---

### 4. Official Audit Determination

In compliance with the Project NOMOS forensic standards:
- **Algorithmic Contribution of Neural Guidance:** **NOT DEMONSTRATED.**
- **Primary Discovery Driver:** Scale-adaptive differential AST beam search with normalized information criteria and weak-form integral quadrature (WSINDy-2D).
- **Recommendation:** Retain neural surrogate as an optional exploratory diagnostic, but declare all M4 milestone certification based on mathematically grounded weak-form and scale-adaptive symbolic algorithms.
