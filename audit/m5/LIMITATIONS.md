# Project NOMOS — Milestone M5
## Known Limitations, Boundaries & Open Scientific Problems

**Principal Investigator / Git Identity:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Milestone:** M5 — Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery  

---

### 1. High Noise Boundaries ($\ge 10\%$)

- **Phenomenon:** At $10\%$ additive observation noise, recovery rate for all methods drops significantly (Active: $32.0\%$, Passive: $20.0\%$).
- **Mechanism:** For high-order spatial derivatives (e.g., $u_{xxx}$ in KdV, or $\nabla^2 \omega$ in Navier-Stokes), high noise inflates the variance of weak-form projection integrals when test functions have compact support.
- **Boundary:** While weak-form projection offers substantial noise shielding compared to finite differences, recovering third- and fourth-order operators under $> 10\%$ unstructured noise remains an open challenge requiring adaptive test-function scale optimization.

---

### 2. Candidate Pool Discretization

- **Phenomenon:** In the current implementation, candidate initial conditions are drawn from a discrete pool of physically meaningful configurations (e.g., solitary waves, collisions, harmonic packets, localized pulses).
- **Mechanism:** Continuous functional optimization over $u_0(x) \in \mathcal{H}^s(\Omega)$ via variational adjoint methods or gradient-based trajectory optimization was not evaluated in M5 due to compute constraints.
- **Boundary:** If the candidate pool does not contain an initial condition capable of breaking a specific degeneracy, active selection cannot synthesize new functional forms from scratch.

---

### 3. Boundary Condition Assumptions

- **Phenomenon:** Solvers and spatial derivative operators assume periodic boundary conditions.
- **Mechanism:** Spectral differentiation via FFT requires periodicity to avoid Gibbs phenomena. For non-periodic Dirichlet or Neumann domains, Chebyshev pseudo-spectral or high-order compact finite difference schemes must be substituted.
- **Boundary:** Physical laws operating on irregular or non-periodic bounded domains require extension of the weak-form boundary integration terms $\oint_{\partial \Omega} (\cdot) dS$.

---

### 4. Computational Overhead of Multi-Model Rollouts

- **Phenomenon:** Evaluating pairwise functional divergence requires computing candidate model vector fields $f_h(u_0)$ for all active hypotheses.
- **Mechanism:** For large portfolios ($> 50$ candidate equations) in 3D geometries, evaluating vector fields across large candidate pools scales as $\mathcal{O}(|\mathcal{H}| \cdot |\mathcal{P}| \cdot N)$.
- **Boundary:** Hierarchical pruning or surrogate-based acquisition evaluation is recommended for large-scale multi-field problems.
