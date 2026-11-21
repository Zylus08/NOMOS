# NOMOS Milestone M2 — Generalization & Closed-Loop ODE Rollout Protocol

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Validation Specialists:** Agents F02, F03, G06  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Modules:** `nomos/evaluation/rollout_m2.py`, `nomos/evaluation/rollout.py`  

---

## 1. Why Derivative Loss is Insufficient

In scientific machine learning, fitting errors on derivatives ($\| \dot{X}_{\text{obs}} - \hat{f}(X) \|^2$) are notoriously deceptive:
1. A candidate equation may fit training derivatives with $R^2 > 0.99$, yet possess unphysical positive eigenvalues or spurious high-order poles ($+x^3$) that explode to infinity within $0.1$ seconds when integrated forward in time.
2. Conversely, a structurally correct physical equation may exhibit modest derivative $R^2$ under noisy observations, yet integrate stably over infinite horizons, capturing the true physical attractor.

Therefore, the **Generalization Gate** mandates that every discovered equation must be evaluated via **closed-loop numerical ODE integration (Rollout RMSE)** on unseen test trajectories.

---

## 2. Closed-Loop Numerical Integration Protocol

Given discovered symbolic expression trees $\hat{f}_1, \dots, \hat{f}_n$:
1. Initialize the system at out-of-distribution initial state $x_0^{(\text{test})} \notin \mathcal{D}_{\text{train}}$.
2. Integrate forward over horizon $t \in [0, T_{\text{test}}]$ using adaptive Dormand-Prince (`RK45` or `DOP853`) numerical integration:
   $$\frac{dx_i}{dt} = \hat{f}_i(x_1(t), \dots, x_n(t)), \quad x(0) = x_0^{(\text{test})}$$
3. Protect against numerical overflow: if $\max |x(t)| > 10^4$ or step size collapses below $10^{-12}$, the rollout is terminated and flagged as `UNSTABLE_EXPLODED`.

---

## 3. Generalization Metric Formulation

The **Rollout RMSE** is computed against the ground-truth high-precision test trajectory $x_{\text{true}}(t)$:

$$\text{Rollout RMSE} = \sqrt{ \frac{1}{M_{\text{test}}} \sum_{k=1}^{M_{\text{test}}} \| x_{\text{sim}}(t_k) - x_{\text{true}}(t_k) \|_2^2 }$$

And the **Relative Rollout Error**:
$$\text{Relative RMSE} = \frac{\text{Rollout RMSE}}{\sqrt{\frac{1}{M_{\text{test}}} \sum_{k=1}^{M_{\text{test}}} \| x_{\text{true}}(t_k) \|_2^2 }}$$

### Acceptance Thresholds:
- **Periodic / Conservative Systems (Harmonic, Pendulum, Van der Pol):** Relative RMSE $\le 0.15$ over 5 oscillation periods.
- **Damped / Kinetic Systems (Rational Kinetics):** Relative RMSE $\le 0.10$ over steady-state convergence.
- **Runaway Divergence:** Relative RMSE $> 1.0$ or numerical overflow fails the Generalization Gate.
