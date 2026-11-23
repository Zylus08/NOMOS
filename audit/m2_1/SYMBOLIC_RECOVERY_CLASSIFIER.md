# Project NOMOS — Milestone M2.1
## Symbolic Recovery Evaluator & 8-Tier Classification Specification

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Component:** `nomos/evaluation/symbolic_classifier.py`  
**Auditor Roles:** A03 (Symbolic Algebra), G01 (Adversarial Auditor), I01 (Certification)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Executive Summary & Defect Elimination

In Milestone M2, candidate symbolic equations were evaluated using a loose string heuristic:
```python
# Flawed M2 predicate:
if ("/" in eq0 or "div" in eq0) and (rollout_rmse < 1.0):
    recovery_status = "EXACT_RECOVERY"
```
This naive predicate allowed the spurious expression $0.5286 / x$ to be reported as an "exact symbolic recovery" of the Michaelis-Menten equation $\dot{x} = \frac{2x}{1+x} - 0.5x$.

In Milestone M2.1, this heuristic was completely excised and replaced with the formal, mathematically verified **8-Tier Scientific Symbolic Recovery Classifier** implemented in `nomos/evaluation/symbolic_classifier.py`.

---

### 2. The 8 Classification Tiers

Every discovered candidate model is strictly classified into one of eight mutually exclusive tiers:

| Tier | Enum Value | Mathematical Definition & Criteria |
| :---: | :--- | :--- |
| **Tier 1** | `EXACT_SYMBOLIC` | The candidate expression is algebraically identical to the ground truth under canonical SymPy simplification (`sp.simplify(cand - true) == 0` or exact tree match) with exact or machine-precision coefficients ($\|c_{\text{est}} - c_{\text{true}}\| \le 10^{-4}$). |
| **Tier 2** | `ALGEBRAICALLY_EQUIVALENT` | The candidate is algebraically equivalent to the ground truth after applying mathematical expansion, trigonometric identities (`trigsimp`), common denominator consolidation, or constant re-grouping (e.g. $1.0 - x^2 \equiv -(x-1)(x+1)$ or $\frac{2x}{1+x} - 0.5x \equiv \frac{1.5x - 0.5x^2}{1+x}$). |
| **Tier 3** | `CORRECT_SUPPORT_APPROXIMATE_COEFFICIENTS` | The candidate has the exact correct functional support (identical basis terms / operator tree structure), but parameter coefficients deviate due to noise or optimization tolerance ($\epsilon_{\text{rel}} \in [10^{-4}, 0.10]$). |
| **Tier 4** | `APPROXIMATE_VECTOR_FIELD` | The candidate has incorrect mathematical structure, but its vector field numerically approximates the ground truth over the training domain ($L_2 \text{ error} \le 0.05$ and $L_\infty \text{ error} \le 0.15$), without catastrophic boundary poles. |
| **Tier 5** | `ROLLOUT_ONLY_MATCH` | The candidate produces stable or low-error test rollouts ($RMSE_{\text{rollout}} < 1.0$) despite having incorrect mathematical structure and significant vector field errors outside the training trajectory (e.g. $0.5286 / x$ on $x \in [0.9, 1.25]$). |
| **Tier 6** | `INCORRECT` | The candidate fails symbolic equivalence, has substantial vector field error, and fails held-out trajectory rollout ($RMSE_{\text{rollout}} \ge 1.0$ or divergent). |
| **Tier 7** | `UNIDENTIFIABLE` | The ground truth is provably unidentifiable from the supplied trajectory data (e.g. linear vs cubic collinearity on a single harmonic energy surface). |
| **Tier 8** | `INVALID_EXPRESSION` | The candidate expression cannot be parsed, contains undefined operators, exhibits division by zero / poles inside the physical domain, or outputs `NaN` / `Inf`. |

---

### 3. Classification Decision Logic & Verification Flow

The classifier executes the following rigorous pipeline:

```
                  Candidate Equation f_hat & Ground Truth f_true
                                        |
                                        v
                            [1. Parse to SymPy Tree]
                                        |
                          +-------------+-------------+
                          |                           |
                     Fails Parse                 Parse Success
                          |                           |
                          v                           v
                  INVALID_EXPRESSION         [2. Domain Singularity Check]
                                                      |
                                        +-------------+-------------+
                                        |                           |
                                   Poles in Domain             No Poles in Domain
                                        |                           |
                                        v                           v
                                INVALID_EXPRESSION          [3. Symbolic Difference]
                                                            diff = simplify(f_hat - f_true)
                                                                    |
                                                      +-------------+-------------+
                                                      |                           |
                                                  diff == 0                   diff != 0
                                                      |                           |
                                                      v                           v
                                               EXACT_SYMBOLIC             [4. Algebraic Equiv]
                                           (or ALGEBRAICALLY_EQUIV)        expand, trigsimp,
                                                                           rational simplifications
                                                                                  |
                                                                    +-------------+-------------+
                                                                    |                           |
                                                                Equiv Match                 Not Equiv
                                                                    |                           |
                                                                    v                           v
                                                          ALGEBRAICALLY_EQUIV         [5. Support Comparison]
                                                                                  Basis terms match?
                                                                                                |
                                                                                  +-------------+-------------+
                                                                                  |                           |
                                                                               Yes (Diff Coeffs)              No
                                                                                  |                           |
                                                                                  v                           v
                                                                           CORRECT_SUPPORT_          [6. Numerical Vector Field]
                                                                           APPROX_COEFFS             Grid L2, L_inf error
                                                                                                              |
                                                                                                +-------------+-------------+
                                                                                                |                           |
                                                                                              L2 < 0.05                   L2 >= 0.05
                                                                                                |                           |
                                                                                                v                           v
                                                                                         APPROX_VECTOR_FIELD         [7. Rollout Check]
                                                                                                                     Test rollout RMSE
                                                                                                                            |
                                                                                                              +-------------+-------------+
                                                                                                              |                           |
                                                                                                         RMSE < 1.0                  RMSE >= 1.0
                                                                                                              |                           |
                                                                                                              v                           v
                                                                                                      ROLLOUT_ONLY_MATCH              INCORRECT
```

---

### 4. Implementation Highlights in `nomos/evaluation/symbolic_classifier.py`

#### 4.1 Safe Domain Evaluation & Singularity Detection
```python
def check_singularities(expr_sp, state_vars, domain_bounds):
    """Detect poles or division-by-zero inside or on the boundary of the physical domain."""
    for denom in expr_sp.as_numer_denom()[1:]:
        # Check roots within domain bounds
        roots = sp.solve(denom, state_vars)
        for r in roots:
            if is_inside_domain(r, domain_bounds):
                return True
    return False
```

#### 4.2 Exact Algebraic Simplification
The evaluator invokes multiple SymPy simplifiers:
1. `sp.simplify(cand_sp - true_sp)`
2. `sp.trigsimp(sp.expand(cand_sp) - sp.expand(true_sp))`
3. `sp.cancel(sp.together(cand_sp - true_sp))`
4. Canonical coefficient rounding: `sp.nsimplify(cand_sp, tolerance=1e-4) == sp.nsimplify(true_sp, tolerance=1e-4)`.

---

### 5. Validation Test Suite Coverage

The classifier was rigorously validated against 8 comprehensive test cases in `tests/m2_1/test_symbolic_classifier.py`:
1. `test_exact_symbolic`: Linear and polynomial identical forms $\to$ `EXACT_SYMBOLIC`.
2. `test_algebraically_equivalent_rational`: Common denominator Michaelis-Menten $\frac{1.5x - 0.5x^2}{1+x} \to$ `ALGEBRAICALLY_EQUIVALENT`.
3. `test_algebraically_equivalent_trig`: $\cos(x)^2 - \sin(x)^2$ vs $\cos(2x) \to$ `ALGEBRAICALLY_EQUIVALENT`.
4. `test_correct_support_approximate_coeffs`: Harmonic with 5% coefficient noise $\to$ `CORRECT_SUPPORT_APPROXIMATE_COEFFICIENTS`.
5. `test_rational_kinetics_spurious_not_exact`: **Adversarial verification**: $0.5286 / x$ is strictly categorized as `APPROXIMATE_VECTOR_FIELD` or `ROLLOUT_ONLY_MATCH`, and **NEVER** `EXACT_SYMBOLIC`.
6. `test_approximate_vector_field`: Taylor expansion of $\sin(x) \approx x - x^3/6 \to$ `APPROXIMATE_VECTOR_FIELD`.
7. `test_rollout_only_match`: Spurious local fit matching rollout within $[0.9, 1.25] \to$ `ROLLOUT_ONLY_MATCH`.
8. `test_invalid_expression`: Syntax error or undefined functions $\to$ `INVALID_EXPRESSION`.

All 8 tests pass with 100% compliance.
