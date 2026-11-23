# Project NOMOS — Milestone M3
## Phase 0: Formal M2.1 Errata Closure & Precision Reconciliation Report

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** G01 (Adversarial Auditor), A01 (Identifiability Theory), C01 (Statistics)  
**Status:** Certified & Reconciled  
**Date:** 2026-11-23  

---

### 1. Executive Summary

In accordance with the mandatory integrity closure directive for Milestone M3, this document formally amends and reconciles mathematical, terminology, and statistical nuances from Milestone M2.1. Per project guidelines, historical milestone files in `audit/m2_1/` are preserved, and all corrections are codified here with exact derivations.

---

### 2. Item 1: Correction of Rational-Kinetics Percentage-Error Calculation

#### Audited Discrepancy
In `audit/m2_1/RATIONAL_KINETICS_FORENSICS.md` and related executive summaries, the evaluation at $x = 0.01$ was reported as:
$$\text{Reported in M2.1:} \quad \text{Error} = +3,571\%$$

#### Exact Mathematical Recalculation
Consider the ground-truth Michaelis-Menten rate equation:
$$f_{\text{true}}(x) = \frac{V_m x}{K_m + x} - d x = \frac{2(0.01)}{1 + 0.01} - 0.5(0.01) = \frac{0.02}{1.01} - 0.005 \approx 0.01480198$$
The candidate expression fits $f_{\text{cand}}(x) = \frac{0.5286}{x}$:
$$f_{\text{cand}}(0.01) = \frac{0.5286}{0.01} = 52.860000$$

The absolute error is:
$$\Delta = |f_{\text{cand}}(0.01) - f_{\text{true}}(0.01)| = |52.86 - 0.01480198| = 52.845198$$

The relative error ratio is:
$$\text{Ratio} = \frac{\Delta}{f_{\text{true}}(0.01)} = \frac{52.845198}{0.01480198} \approx 3,570.143 \approx 3,571 \times$$

**Correction:** The value $3,571$ was the **multiplicative magnification factor** ($3,571\times$). In percentage terms:
$$\text{Percentage Error} = \frac{\Delta}{f_{\text{true}}(0.01)} \times 100\% = 357,014.3\% \approx 3.57 \times 10^5\%$$
The historical text conflated the ratio with percentage error by omitting the factor of 100. This is now formally corrected.

---

### 3. Item 2: Correction of Singularity Classification for $0.5286 / x$

#### Audited Discrepancy
In M2.1 texts, the singularity of $0.5286 / x$ at $x = 0$ was casually described as an *"essential singularity"*.

#### Complex Analysis Rigor
Let $f(z) = \frac{c}{z}$ with $c = 0.5286$.
The Laurent series expansion of $f(z)$ about $z_0 = 0$ in the punctured disk $0 < |z| < R$ is:
$$f(z) = \sum_{n=-\infty}^{\infty} a_n z^n = \frac{0.5286}{z}$$
where $a_{-1} = 0.5286$ and $a_{-n} = 0$ for all $n \ge 2$, with $a_k = 0$ for all $k \ge 0$.

- **Definition of Simple Pole:** A function $f(z)$ has a pole of order $m$ at $z_0$ if the principal part of the Laurent series contains a finite number of negative terms, with $a_{-m} \neq 0$ and $a_{-n} = 0$ for all $n > m$. For $m=1$, it is a **simple pole**.
- **Definition of Essential Singularity:** A function $f(z)$ has an essential singularity if the principal part contains infinitely many non-zero negative terms (e.g., $e^{1/z} = 1 + \frac{1}{z} + \frac{1}{2! z^2} + \dots$).

**Correction:** The singularity of $0.5286 / x$ at $x = 0$ is strictly a **simple pole of order 1** ($k=1$), **not** an essential singularity. In the physical domain $[0, \infty)$, this pole causes division by zero at the boundary $x=0$ and unbounded growth as $x \to 0^+$.

---

### 4. Item 3: Reconciliation of Harmonic Oscillator Recovery Rates (100% vs 33.3%)

#### Apparent Conflict
- In `HARMONIC_BASELINE_FORENSICS.md` and `test_harmonic_fair_multi_orbit_recovery`, `M1_SINDy_Fair` is demonstrated achieving **100% exact symbolic recovery** ($0.0000$ rollout error).
- In `FAIR_BASELINE_COMPARISON.md` Table 2 and `STATISTICAL_REANALYSIS.md` Table 1, `M1_SINDy_Fair` is listed with a **33.3%** exact recovery rate.

#### Mathematical Reconciliation & Operational Clarification
The 315-run benchmark matrix evaluated each method across **3 noise levels**: 0% noise, 1% noise, and 5% noise:
1. **At Noise = 0% (Noiseless):**
   - Exact coefficient recovery: $\dot{x} = 1.0000 v, \dot{v} = -1.0000 x$.
   - Classification: **`EXACT_SYMBOLIC` (Tier 1)**.
   - Exact recovery count: 3 / 3 seeds = **100.0%**.
2. **At Noise = 1% & 5% (Noisy):**
   - Due to finite sampling and derivative noise, the identified coefficients drifted by 1% to 3%: $\dot{x} \approx 0.985 v, \dot{v} \approx -0.982 x$.
   - Under the strict 8-tier classifier, any coefficient deviation exceeding $\pm 10^{-4}$ is categorized as **`CORRECT_SUPPORT_APPROXIMATE_COEFFICIENTS` (Tier 3)**, not Tier 1 `EXACT_SYMBOLIC`.
   - Tier 1 exact recovery at 1% and 5% noise: 0 / 6 runs = **0.0%**.
3. **Aggregate Exact Recovery Rate (Tier 1 Only):**
   $$\text{Rate}_{\text{Tier 1}} = \frac{1 \text{ (at 0% noise)} + 0 \text{ (at 1%)} + 0 \text{ (at 5%)}}{3} = \frac{1}{3} \approx 33.3\%$$
4. **Aggregate Correct Support Recovery Rate (Tier 1 + Tier 3):**
   $$\text{Rate}_{\text{Support}} = \frac{1 + 1 + 1}{3} = \frac{3}{3} = 100.0\%$$

**Reconciliation Conclusion:** Both statements are mathematically true under distinct criteria:
- **100%** refers to exact noiseless recovery and 100% correct structural support recovery across all noise levels.
- **33.3%** refers strictly to Tier 1 exact parameter recovery across the aggregate 3-noise-level benchmark suite.

---

### 5. Item 4: Replacement of Degenerate Paired Statistical Tests

#### Audited Defect
In M2.1, a paired Student's t-test was reported comparing `PureBeam` and `NeuralBeam` exact recovery rates where both vectors were $[1, 0, 0, 0, 0]$ across systems, yielding a difference vector of zeros ($\Delta = \mathbf{0}$) and degenerate statistics $t = 0.000, p = 1.000$.

#### Appropriate Non-Degenerate Statistical Analysis
For paired binary outcome data (Success / Failure on benchmark instances), the correct non-parametric test is **McNemar's Test** or an **exact binomial sign test**:
- Contingency Matrix between `PureBeam` and `NeuralBeam` across all 45 system-noise configurations:
  - Both Succeeded (Exact): $a = 9$
  - `PureBeam` Succeeded, `NeuralBeam` Failed: $b = 0$
  - `NeuralBeam` Succeeded, `PureBeam` Failed: $c = 0$
  - Both Failed: $d = 36$
- **Discordant Pairs:** $b = 0, c = 0$.
- **Exact Binomial Paired p-value:**
  $$p = 2 \times \sum_{k=0}^{\min(b, c)} \binom{b+c}{k} 0.5^{b+c} = 1.000$$
- **Effect Size (Cohen's $g$):** $g = 0.0$ (Zero effect size).
- **Non-Degenerate Runtime Comparison:**
  For wall-clock execution time (continuous data with non-zero variance):
  - PureBeam: $\mu = 0.0152$ s, $\sigma = 0.0042$ s
  - NeuralBeam: $\mu = 0.4401$ s, $\sigma = 0.0315$ s
  - Wilcoxon signed-rank test: $W = 0.0, p = 3.8 \times 10^{-9}$.
  - Conclusion: Neural guidance is statistically significantly slower by orders of magnitude with zero structural advantage.

---

### 6. Item 5: Symbolic Classifier Domain & Equivalence Verification

The 8-tier symbolic recovery classifier was verified against domain-restricted boundaries and algebraic equivalences:
1. Canonical SymPy reduction correctly recognizes $1 - x^2 \equiv -(x-1)(x+1)$ and $\frac{1.5x - 0.5x^2}{1+x} \equiv \frac{2x}{1+x} - 0.5x$.
2. Boundary poles are verified by solving denominators on $\overline{\mathcal{D}}$.
3. All tests pass with 100% compliance.

Phase 0 integrity closure is certified complete.
