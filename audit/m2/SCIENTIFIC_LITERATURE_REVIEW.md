# NOMOS Milestone M2 — Scientific Literature Review & Theoretical Foundations

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Division:** Division A (Scientific Theory & Mathematical Foundations)  
**Lead Theoretical Specialists:** Agents A01, A02, A03, A06, A08  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Date:** November 2026  

---

## 1. Executive Summary

Milestone M1 established sparse identification of nonlinear dynamics via Sequentially Thresholded Least Squares (STLSQ). While STLSQ is computationally efficient ($O(M \cdot P^2)$), its fundamental epistemic boundary is the **pre-specified candidate library $\Theta(X)$**: if the true governing operator (e.g., $\sin(\theta)$, $x / (1+x)$, or transcendental non-polynomials) is omitted from $\Theta(X)$, sparse regression must either fail or approximate the vector field via divergent Taylor truncations.

Milestone M2 breaks this boundary by establishing an **open-ended neural-symbolic discovery framework**. This document provides the mathematical foundations, rigorous literature review, failure mode taxonomy, and formal identifiability contracts governing M2.

---

## 2. Theoretical Foundations & Literature Taxonomy

### 2.1 Sparse Identification of Nonlinear Dynamics (SINDy)
- **Foundational Paper:** Brunton, S. L., Proctor, J. L., & Kutz, J. N. (2016). *Discovering governing equations from data by sparse identification of nonlinear dynamical systems*. PNAS, 113(15), 3932-3937.
- **Mechanism:** Solves $\dot{X} = \Theta(X)\Xi$ using $\ell_0$-penalized regression via STLSQ or SR3 (Champion et al., IEEE Access 2020).
- **Fundamental Limitations:**
  1. *Curse of Dimensionality:* Expanding polynomial and trigonometric bases up to degree $d$ in $n$ variables scales as $\binom{n+d}{d}$, resulting in severely ill-conditioned matrices.
  2. *Hypothesis Class Rigidity:* Cannot discover rational functional forms ($f(x) = \frac{p(x)}{q(x)}$) without pre-multiplying or introducing implicit formulation libraries (Mangan et al., IEEE Trans. 2016), which are notoriously prone to trivial null-space solutions.

### 2.2 Symbolic Regression via Genetic Programming
- **Foundational Papers:**
  - Koza, J. R. (1992). *Genetic Programming: On the Programming of Computers by Means of Natural Selection*. MIT Press.
  - Schmidt, M., & Lipson, H. (2009). *Distilling free-form natural laws from experimental data*. Science, 324(5923), 81-85 (Eureqa).
- **Mechanism:** Represents mathematical expressions as abstract syntax trees (ASTs). Evolves candidate populations using subtree crossover, point mutation, and Pareto selection trading off MSE against tree complexity.
- **Fundamental Limitations:**
  1. *Combinatorial Explosion:* The discrete tree search space grows as $\Omega((k+1)^{2d})$ where $k$ is operator arity and $d$ is tree depth.
  2. *Constant Optimization Bottleneck:* Genetic mutation of floating-point leaf constants is notoriously inefficient; continuous parameter optimization must be coupled via gradient methods (L-BFGS / Nelder-Mead).
  3. *Uncontrolled Bloat:* Expression trees tend to accumulate neutral introns (e.g., $x + 0$, $x \cdot 1$, $\log(\exp(x))$) that inflate complexity without improving accuracy.

### 2.3 Neural ODEs and Physics-Informed Neural Networks (PINNs)
- **Foundational Papers:**
  - Chen, R. T., Rubanova, Y., Bettencourt, J., & Duvenaud, D. K. (2018). *Neural Ordinary Differential Equations*. NeurIPS.
  - Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). *Physics-informed neural networks: A deep learning framework for solving forward and inverse problems*. Journal of Computational Physics, 378, 686-707.
- **Mechanism:** Replaces the RHS vector field with a deep neural network $f_\theta(x)$.
- **Fundamental Limitations:**
  1. *Black-Box Representation:* While $f_\theta(x)$ accurately predicts short-term trajectories, it provides zero analytical interpretability, zero symbolic insight, and cannot be symbolically audited for conservation laws or dimensional consistency.
  2. *Extrapolation Collapse:* MLPs extrapolate catastrophically outside the convex hull of training data.

### 2.4 Deep Symbolic Regression and Neural-Symbolic Hybrids
- **Foundational Papers:**
  - Petersen, B. K., et al. (2021). *Deep symbolic regression: Recovering mathematical expressions from data via risk-seeking policy gradients*. ICLR.
  - Cranmer, M., et al. (2020). *Discovering symbolic models from deep learning with inductive biases*. NeurIPS (PySR).
  - Udrescu, S. M., & Tegmark, M. (2020). *AI Feynman: A physics-inspired method for symbolic regression*. Science Advances, 6(16).
- **NOMOS M2 Novel Contribution:**
  Instead of utilizing RL policy gradients (which require millions of sample episodes) or brute-force dimensional recursion, NOMOS M2 introduces a **Physics-Informed Neural Dynamics Surrogate with Automatic Jacobian Guidance**:
  1. Trains a smooth MLP surrogate $\hat{f}(x)$ on estimated trajectory derivatives.
  2. Computes the analytical state Jacobian $J_{ij}(x) = \frac{\partial \hat{f}_i}{\partial x_j}$ via exact autograd across phase space.
  3. Projects Jacobian sensitivity and curvature metrics into structural priors that dynamically guide structured beam search and genetic programming.
  4. Optimizes continuous constants via SciPy L-BFGS-B on non-dominated Pareto frontiers.

---

## 3. Mathematical Contracts & Problem Formulation

### 3.1 Dynamical System Formulation
Consider an autonomous continuous-time nonlinear dynamical system:
$$\frac{dx}{dt} = f^*(x(t)), \quad x(0) = x_0 \in \Omega \subset \mathbb{R}^n$$
where $f^*: \mathbb{R}^n \to \mathbb{R}^n$ is an unknown, smooth (or piecewise meromorphic) vector field.

We observe a finite set of $K$ discrete, noisy trajectories sampled at times $\{t_k\}_{k=0}^M$:
$$y_k^{(j)} = x^{(j)}(t_k) + \epsilon_k^{(j)}, \quad \epsilon_k^{(j)} \sim \mathcal{N}(0, \sigma^2 I_n)$$

### 3.2 Hypothesis Space $\mathcal{H}_{tree}$
Let $\mathcal{H}_{tree}$ denote the space of typed abstract syntax trees formed from:
- **Terminals:** State variables $\{x_1, \dots, x_n\}$, real constants $c \in \mathbb{R}$.
- **Unary Operators:** $\mathcal{O}_1 = \{-, \sin, \cos, \exp, \log_{\text{prot}}, \sqrt{\text{prot}}\}$.
- **Binary Operators:** $\mathcal{O}_2 = \{+, -, \times, \div_{\text{prot}}, \text{pow}_{\text{prot}}\}$.

### 3.3 Multi-Objective Pareto Optimization Contract
For each coordinate $i \in \{1, \dots, n\}$, find candidate expression tree $\hat{f}_i \in \mathcal{H}_{tree}$ minimizing the multi-objective loss:
$$\min_{\hat{f}_i \in \mathcal{H}_{tree}} \left( \mathcal{L}_{MSE}(\hat{f}_i; X, \dot{X}_i), \; \mathcal{C}(\hat{f}_i) \right)$$
subject to:
$$\mathcal{L}_{MSE}(\hat{f}_i) = \frac{1}{M} \sum_{k=1}^M \left( \dot{x}_{i}(t_k) - \hat{f}_i(x(t_k); \mathbf{c}^*) \right)^2$$
$$\mathbf{c}^* = \arg\min_{\mathbf{c} \in \mathbb{R}^p} \frac{1}{M} \sum_{k=1}^M \left( \dot{x}_{i}(t_k) - \hat{f}_i(x(t_k); \mathbf{c}) \right)^2$$
$$\mathcal{C}(\hat{f}_i) = \sum_{v \in V(\hat{f}_i)} w(\text{type}(v))$$

---

## 4. Identifiability & Epistemic Uncertainty

### 4.1 Trajectory Excitation Condition
Identifiability requires that the phase-space trajectory $\{x(t)\}_{t \ge 0}$ sufficiently excites all active degrees of freedom. Let $S = \text{SVD}(\tilde{X})$ where $\tilde{X} = X - \bar{X}$.
The **Manifold Excitation Ratio** is defined as:
$$\rho_{exc} = \frac{\sigma_{\min}(\tilde{X})}{\sigma_{\max}(\tilde{X})}$$
If $\rho_{exc} < 10^{-4}$ or $\sigma_{\max} < 0.01$, the trajectory is deemed trapped on a low-dimensional attractor or fixed point, triggering `INSUFFICIENT_EVIDENCE`.

### 4.2 Multiplicity of Plausible Laws
In finite, noisy observation windows, multiple non-equivalent symbolic expressions can produce nearly identical residuals:
$$\frac{|\mathcal{L}(\hat{f}^{(1)}) - \mathcal{L}(\hat{f}^{(2)})|}{\min(\mathcal{L}_1, \mathcal{L}_2)} \le \delta_{tol}$$
When this condition holds between non-dominated Pareto candidates, NOMOS M2 explicitly reports `MULTIPLE_PLAUSIBLE_LAWS`, preventing unwarranted claims of unique discovery.

---

## 5. Summary of Theoretical Contracts

| Category | Requirement | Implementation Module |
| :--- | :--- | :--- |
| **Expression Safety** | All operators must be domain-protected | `nomos/symbolic/primitives.py` |
| **Algebraic Exactness** | Trees must parse to/from SymPy losslessly | `nomos/symbolic/trees.py` |
| **Search Guidance** | Neural surrogate Jacobians must inform prior weights | `nomos/neural/guidance.py` |
| **Continuous Refit** | Constants must be optimized via gradient descent | `nomos/search/optimizer.py` |
| **Uncertainty Audit** | Bootstrap residual resampling must quantify parameter variance | `nomos/evaluation/identifiability.py` |
