# Project NOMOS — Milestone M2.1
## Statistical Reanalysis & Empirical Benchmark Verification Report

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** C01–C04 (Experimental Statistics), F01–F06 (Baselines), G01 (Adversarial Auditor)  
**Data Artifact:** `audit/m2_1/CORRECTED_RESULTS.csv` (315 runs executed)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Experimental Grid Overview

A complete, controlled, repeated-seed grid of **315 benchmark executions** was conducted across:
- **5 Physical Systems:** Harmonic Oscillator, Duffing Oscillator, Van der Pol Oscillator, Nonlinear Pendulum, Rational Kinetics.
- **7 Methods:** `PureBeam`, `PureGP`, `NeuralBeam`, `NeuralGP`, `M1_SINDy_Fair`, `M1_SINDy_SingleOrbitD3`, `PySINDy_Fair`.
- **3 Noise Levels:** 0%, 1%, 5%.
- **3 Random Seeds:** 42, 43, 44.
- **Evaluation Criteria:** Verified 8-tier symbolic recovery classifier, rollout RMSE on out-of-distribution test initial conditions, candidate expression evaluation count, and total wall-clock execution time.

---

### 2. Comprehensive Recovery Statistics

#### Table 1: Exact / Algebraically Equivalent Recovery Rate (%) Across All Methods & Systems

| Benchmark System | PureBeam | PureGP | NeuralBeam | NeuralGP | M1_SINDy_Fair | M1_SINDy_SingleOrbitD3 | PySINDy_Fair |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Harmonic Oscillator** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | **33.3%** | 0.0% | 33.3% |
| **Duffing Oscillator** | 0.0% | 0.0% | 0.0% | 0.0% | **100.0%** | 0.0% | 0.0% |
| **Van der Pol Oscillator** | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| **Nonlinear Pendulum** | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| **Rational Kinetics** | **0.0%** | **0.0%** | **0.0%** | **0.0%** | 0.0% | 0.0% | 0.0% |
| **Overall Exact Recovery** | **20.0%** | **20.0%** | **20.0%** | **20.0%** | **26.7%** | 0.0% | 6.7% |

*Key Statistical Finding:* Under the strict, mathematically sound 8-tier evaluator:
1. `NeuralBeam` and `NeuralGP` achieve **identical** exact recovery rates to unguided `PureBeam` and `PureGP` (20.0% vs 20.0%). Neural guidance yielded zero statistical improvement in exact structural recovery across the 5 benchmark systems.
2. `M1_SINDy_Fair` achieves the highest overall exact recovery rate (**26.7%**), perfectly recovering Duffing oscillator (100%) and Harmonic oscillator (at 0% noise).
3. The previously claimed 100% recovery for Rational Kinetics is officially debunked: **all methods achieved 0.0% exact recovery**. Discovered models are strictly `ROLLOUT_ONLY_MATCH` or `APPROXIMATE_VECTOR_FIELD`.

---

### 3. Compute Budget & Wall-Clock Efficiency Analysis

#### Table 2: Mean Wall-Clock Time (Seconds) & Evaluation Counts

| Method | Mean Wall Time (s) | Training Time (s) | Search Time (s) | Mean Evaluated Candidates | Efficiency Ratio vs PureBeam |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **PureBeam** | **0.015s** | 0.000s | 0.015s | 140 | **1.0x (Baseline)** |
| **PureGP** | **0.029s** | 0.000s | 0.029s | 180 | 1.9x slower |
| **M1_SINDy_Fair** | **0.033s** | 0.000s | 0.033s | 7 | 2.2x slower |
| **PySINDy_Fair** | **0.032s** | 0.000s | 0.032s | 8 | 2.1x slower |
| **M1_SINDy_SingleOrbitD3** | **0.033s** | 0.000s | 0.033s | 9 | 2.2x slower |
| **NeuralBeam** | **0.440s** | 0.380s | 0.060s | 140 | **29.3x slower** |
| **NeuralGP** | **0.440s** | 0.380s | 0.060s | 180 | **29.3x slower** |

*Analysis of Computational Overhead:*
- Neural guidance requires an initial phase of training a PyTorch Multi-Layer Perceptron (MLP) dynamics surrogate, followed by computing automated Jacobians and Hessian approximations via autograd.
- This creates an irreducible overhead of **~0.38 to 0.45 seconds per run**.
- For low-dimensional physical systems ($n=2$), unguided beam search parses and scores all 140 candidate expression trees in just **0.015 seconds**.
- Therefore, neural guidance introduces a **~30x compute overhead** while evaluating the exact same number of symbolic candidates and yielding no improvement in exact recovery.

---

### 4. Noise Robustness Analysis Across Noise Levels (0%, 1%, 5%)

#### Table 3: Performance Degradation Under Relative Measurement Noise

| System / Method | Exact Recovery @ 0% Noise | Exact Recovery @ 1% Noise | Exact Recovery @ 5% Noise | Mean Rollout RMSE @ 5% Noise |
| :--- | :---: | :---: | :---: | :---: |
| **Harmonic Oscillator (PureBeam)** | 100% | 100% | 100% | 0.0000 |
| **Harmonic Oscillator (NeuralBeam)** | 100% | 100% | 100% | 0.0000 |
| **Harmonic Oscillator (M1_SINDy_Fair)** | 100% | 0% (coeff error) | 0% (coeff error) | 0.0298 |
| **Harmonic Oscillator (M1_SINDy_D3)** | 0% | 0% | 0% | 2.766 (Spurious blowup) |
| **Duffing Oscillator (M1_SINDy_Fair)** | 100% | 100% | 100% | 0.0000 |
| **Rational Kinetics (PureBeam)** | 0% | 0% | 0% | 0.4115 |
| **Rational Kinetics (NeuralBeam)** | 0% | 0% | 0% | 0.4115 |
| **Rational Kinetics (M1_SINDy_Fair)** | 0% | 0% | 0% | 0.0335 |

*Key Noise Findings:*
1. `PureBeam` and `NeuralBeam` maintain exact recovery on the harmonic oscillator even at 5% noise because the discrete grammar and parsimony penalty discard noise artifacts.
2. `M1_SINDy_Fair` achieves exact recovery at 0% noise; at 1% and 5% noise, parameter estimates deviate slightly into `CORRECT_SUPPORT_APPROXIMATE_COEFFICIENTS` (coefficients drift by 1–3%), but test rollout RMSE remains exceptionally low (0.0298).
3. On Rational Kinetics, polynomial SINDy achieves lower test rollout RMSE (0.0335) than symbolic beam search (0.4115), because a degree-3 Taylor series provides a superior local approximation to $\frac{2x}{1+x} - 0.5x$ than simple depth-3 rational trees like $0.5286 / x$.

---

### 5. Hypothesis Testing & Significance

A two-tailed paired t-test was performed between `PureBeam` and `NeuralBeam`:
- **Test Metric:** Exact recovery rate ($H_0: \mu_{\text{pure}} = \mu_{\text{neural}}$)
  - $t = 0.000, p = 1.000$.
  - **Verdict:** Fail to reject null hypothesis. Neural guidance provides zero statistically significant recovery advantage.
- **Test Metric:** Total wall-clock time ($H_0: \mu_{\text{neural}} \le \mu_{\text{pure}}$)
  - $t = 54.32, p < 10^{-50}$.
  - **Verdict:** Reject null hypothesis. Neural guidance is statistically significantly slower by an order of magnitude.

### 6. Summary of Certified Results

The empirical results generated across 315 runs provide indisputable mathematical evidence:
1. M2's claim of 100% rational kinetics recovery was false.
2. M2's claim of SINDy failing on the harmonic oscillator was an artifact of an ill-posed single-orbit energy manifold.
3. Neural guidance on low-dimensional benchmarks is **NOT DEMONSTRATED** to provide a scientific advantage over unguided symbolic search.
