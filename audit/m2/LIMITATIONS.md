# NOMOS Milestone M2 — Known Failure Modes, Limitations & Epistemic Boundaries

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Auditing Specialists:** Agents A05, A07, G08, G09, I01  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Date:** November 2026  

---

## 1. Scientific Integrity Principle

A credible scientific research laboratory does not conceal limitations or selectively report flattering experimental runs. This document explicitly identifies known failure modes, theoretical boundaries, and scaling bottlenecks encountered during the development and testing of Milestone M2.

---

## 2. Identified Failure Modes & Root Causes

### 2.1 Collinear Small-Angle Degeneracy in Nonlinear Pendulums
- **Symptom:** On `nonlinear_pendulum` trajectories initialized at moderate amplitudes ($\theta_0 \le 1.2$ rad), symbolic search frequently selects the linear term $-8.125 \theta$ instead of $-9.81 \sin(\theta)$.
- **Root Cause:**
  Over the range $\theta \in [-1.2, 1.2]$, the Taylor expansion $\sin(\theta) \approx \theta - \frac{\theta^3}{6}$ deviates from linearity by at most $12\%$. A linear term has lower structural complexity ($\mathcal{C} = 3.5$) than a scaled sine term ($\mathcal{C} = 4.5$). On finite observation trajectories with noise, the Pareto score $\mathcal{L}_{\text{MSE}} + \lambda \mathcal{C}$ favors the linear model unless trajectories are initialized with extreme large-angle excitations ($\theta_0 > 2.5$ rad) near the separatrix.
- **Diagnostic Protection:** NOMOS M2 correctly flags this condition as `MULTIPLE_PLAUSIBLE_LAWS`, warning the user that observation data is collinear with a harmonic oscillator.

### 2.2 Bistable Runaway in Polynomial Duffing Oscillators
- **Symptom:** On the Duffing oscillator ($\dot{v} = -\delta v + \beta x - \alpha x^3$), under-estimated cubic stiffness coefficients cause numerical trajectories to escape the potential well during long-horizon test rollouts ($RMSE > 100$).
- **Root Cause:** The cubic term $-x^3$ governs the outer restorative potential barrier. If the coefficient $\alpha$ is under-estimated by even $10\%$, high-energy initial conditions exceed the escape energy, causing runaway trajectories to infinity.
- **Remediation for M3:** Implement Hamiltonian energy-bounded regularizers during continuous coefficient optimization.

### 2.3 Combinatorial Scaling Beyond 5 Dimensions
- **Bottleneck:** While 1D and 2D dynamical systems converge in $< 3$ seconds, grammar expansion at depth $d \ge 4$ across $n \ge 6$ state coordinates generates $> 10^5$ trees per generation.
- **Remediation for M3:** Hierarchical modular decomposition and active learning trajectory selection.

---

## 3. Epistemic Boundaries of Milestone M2

1. **Autonomous Vector Fields Only:** M2 currently discovers systems of the form $\dot{x} = f(x)$. Non-autonomous systems with explicit time-varying forcing $f(x, t)$ or stochastic Langevin terms $\sigma(x) dW_t$ require the M3 stochastic discovery extension.
2. **Derivative Quality Dependency:** If observation noise exceeds $10\%$ with sparse sampling, Savitzky-Golay derivative estimates degrade significantly, propagating noise into both the neural surrogate and symbolic residuals.
3. **Continuous Phase Space:** M2 assumes continuous phase space dynamics; discrete maps or hybrid discontinuous switching dynamics (e.g., bouncing balls with restitution) are out of scope.
