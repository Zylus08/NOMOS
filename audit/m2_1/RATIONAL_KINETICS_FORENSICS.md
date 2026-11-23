# NOMOS Milestone M2.1 — Rational-Kinetics Recovery Forensics & Mathematical Analysis

**Milestone:** M2.1 — Adversarial Scientific Verification, Symbolic Recovery Repair & Neural Guidance Ablation  
**Lead Mathematical Auditors:** Agents A01, A03, E01, I01  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Target System:** `RationalKineticsSystem` (`nomos/physics/rational_system.py`)  

---

## 1. The Discrepancy Under Investigation

In the Milestone M2 Final Report (`audit/m2/M2_FINAL_REPORT.md`) and recovery log (`audit/m2/SCIENTIFIC_RECOVERY.csv` lines 50–58), the following claim was certified:
- **Reported System:** Michaelis-Menten / Hill rational kinetics.
- **Ground-Truth Equation:**
  $$\frac{dx}{dt} = \frac{V_m x}{K_m + x} - d x, \quad \frac{dy}{dt} = \alpha x - \gamma y$$
  with nominal parameters $V_m = 2.0, K_m = 1.0, d = 0.5, \alpha = 1.0, \gamma = 0.8$.
- **Discovered Equations Logged in M2:**
  $$\frac{dx}{dt} = \frac{0.5286}{x}, \quad \frac{dy}{dt} = \frac{0.7915}{x}$$
- **Reported Metric:** `success=True`, `rollout_rmse=0.4107`.

---

## 2. Mathematical Rigorous Non-Equivalence Proof

Let $f_{\text{true}}(x) = \frac{2x}{1 + x} - 0.5 x$ and $f_{\text{cand}}(x) = \frac{0.5286}{x}$.

### 2.1 Boundary & Singularity Analysis ($x \to 0^+$)
- **True System Limit:**
  $$\lim_{x \to 0^+} f_{\text{true}}(x) = \lim_{x \to 0^+} \left( \frac{2(0)}{1 + 0} - 0.5(0) \right) = 0.0$$
  At zero substrate concentration, enzyme reaction velocity is strictly zero. The origin $(0, 0)$ is an invariant physical equilibrium.
- **Candidate Expression Limit:**
  $$\lim_{x \to 0^+} f_{\text{cand}}(x) = \lim_{x \to 0^+} \frac{0.5286}{x} = +\infty$$
  The candidate expression possesses a catastrophic pole (singularity) at $x = 0$.

### 2.2 Asymptotic & Saturation Analysis ($x \to \infty$)
- **True System Asymptote:**
  $$f_{\text{true}}(x) = \frac{2x}{1 + x} - 0.5 x \approx 2.0 - 0.5 x \to -\infty$$
  As substrate becomes abundant, enzyme velocity saturates at $V_m = 2.0$, and linear decay $-0.5 x$ dominates, pulling states back into the bounded physical domain.
- **Candidate Expression Asymptote:**
  $$\lim_{x \to \infty} f_{\text{cand}}(x) = \lim_{x \to \infty} \frac{0.5286}{x} = 0.0^+$$
  The candidate fails to provide any restorative decay at large substrate concentrations.

### 2.3 Numerical Comparison Across the Physical Domain

| State Coordinate $x$ | True Velocity $f_{\text{true}}(x)$ | Candidate Velocity $f_{\text{cand}}(x)$ | Absolute Error | Relative Error | Physical Consequence |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **$x = 0.01$** | $+0.0148$ | $+52.86$ | $52.85$ | **$+3,571\%$** | **Spurious explosive runaway from zero** |
| **$x = 0.10$** | $+0.1318$ | $+5.286$ | $5.154$ | **$+3,910\%$** | **Extreme acceleration at low concentration** |
| **$x = 0.50$** | $+0.4167$ | $+1.057$ | $0.640$ | **$+154\%$** | Substantial overestimation |
| **$x = 1.00$** | $+0.5000$ | $+0.5286$ | $0.0286$ | **$+5.7\%$** | **Coincidental local intersection** |
| **$x = 2.00$** | $+0.3333$ | $+0.2643$ | $0.0690$ | **$-20.7\%$** | Moderate deviation |
| **$x = 5.00$** | $-0.8333$ | $+0.1057$ | $0.9390$ | **$-112.7\%$** | **Wrong sign (positive instead of negative)** |
| **$x = 10.00$** | $-3.1818$ | $+0.05286$ | $3.2347$ | **$-101.7\%$** | **Wrong sign (positive instead of negative)** |

### 2.4 SymPy Formal Inequivalence Verification
Evaluating in SymPy:
```python
diff = sp.simplify(cand_expr - true_expr)
# diff = -0.5*x - 2.0*x/(x + 1) + 0.5286/x
# Does not reduce to 0 under any algebraic or domain assumptions.
```

---

## 3. Root Cause Investigation

Why did the discovery engine select $0.5286 / x$, and why did the evaluation framework certify it?

### Root Cause 1: Search Depth Truncation
- The true equation $f(x) = \frac{2x}{1 + x} - 0.5 x$ requires a tree of **depth 4**:
  `SUB(DIV(MUL(2, x), ADD(1, x)), MUL(0.5, x))`.
- To bound runtime in M2, search depth was constrained to `max_depth = 3`.
- Therefore, the true functional structure was **structurally absent from the searched hypothesis space**.

### Root Cause 2: Narrow Trajectory Excitation
- The training trajectory was initialized at $x_0 = 1.0$ and stayed near the equilibrium range $x \in [0.9, 1.25]$.
- Over this narrow interval, $f_{\text{true}}(x) \approx 0.50$, and $0.5286 / x$ produces values in $[0.42, 0.58]$.
- SciPy L-BFGS-B refit the numerator constant to $0.5286$, achieving a low training MSE ($0.008$) on this specific trajectory.

### Root Cause 3: Defective Heuristic Success Predicate
- In `experiments/m2/run_m2_benchmarks.py` line 166:
  ```python
  elif sys_name == "rational_kinetics":
      functional_success = ("/" in eq0 or "div" in eq0) and (rollout_rmse < 1.0)
  ```
- Any expression containing a division symbol `/` whose test rollout RMSE was below 1.0 was automatically labeled as `functional_success: True`!
- The evaluation script never checked whether the mathematical structure matched Michaelis-Menten kinetics.

---

## 4. Reclassification & Corrected Verdict

Under the verified 8-tier classification framework (`nomos/evaluation/symbolic_classifier.py`):
- **Old M2 Classification:** `functional_success: True` (claimed rational kinetics discovery).
- **Corrected M2.1 Classification:** **`ROLLOUT_ONLY_MATCH`** (or `APPROXIMATE_VECTOR_FIELD` on local window).
- **Is Exact or Algebraically Equivalent?** **`False`**.

**Conclusion:** The M2 claim of autonomous rational-kinetics discovery was an empirical false-positive caused by a lenient evaluation heuristic and search depth truncation.
