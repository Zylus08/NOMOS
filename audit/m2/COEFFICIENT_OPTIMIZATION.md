# NOMOS Milestone M2 — Continuous Coefficient Optimization

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Optimization Specialists:** Agents D04, D06, E03  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Module:** `nomos/search/optimizer.py`  

---

## 1. Problem Formulation & Hybrid Optimization Separation

In symbolic regression over expression trees, there exists a fundamental division between:
1. **Discrete Structure Discovery:** Determining the topological layout of operators and variable bindings (e.g., $c_1 \cdot \sin(c_2 \cdot \theta) + c_3 \cdot \omega$).
2. **Continuous Parameter Estimation:** Estimating real-valued scalar constants $\mathbf{c} = [c_1, c_2, \dots, c_p] \in \mathbb{R}^p$.

Treating continuous constants as discrete nodes in genetic mutation or grammar expansion results in severe combinatorial drag (random floating-point drift). NOMOS M2 explicitly separates discrete structure generation from continuous parameter estimation via dedicated non-linear numerical optimization.

---

## 2. Optimization Algorithm & Objective

Given an expression tree $T$ containing $p$ constant leaf nodes $\mathbf{c} = [c_1, \dots, c_p]$, the optimal parameter vector $\mathbf{c}^*$ is obtained by solving:

$$\mathbf{c}^* = \arg\min_{\mathbf{c} \in \mathbb{R}^p} \mathcal{L}(\mathbf{c}) = \frac{1}{M} \sum_{k=1}^M \left( y_k - f_T(x_k; \mathbf{c}) \right)^2$$

### 2.1 Optimization Engines
- **Primary Engine:** SciPy `L-BFGS-B` (Limited-memory Broyden–Fletcher–Goldfarb–Shanno with Box constraints).
  - Approximates inverse Hessian matrices using gradient histories.
  - Convergence criteria: gradient tolerance $\le 10^{-5}$, max iterations $\le 20$.
- **Fallback Engine:** Nelder-Mead simplex direct search.
  - Utilized if gradient evaluations fail due to discontinuous operator boundaries.

### 2.2 Gradient Numerical Stability
- Protected operators ensure that loss function values $\mathcal{L}(\mathbf{c})$ remain finite real numbers across all intermediate trial steps.
- If parameter proposals produce non-finite evaluations, a penalty loss of $10^9$ is returned, guiding the line search back to valid parameter manifolds.
