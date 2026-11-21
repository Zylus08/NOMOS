# SWARM FAILED TASKS & ADVERSARIAL VULNERABILITIES
**Role:** Agents G10 & J05  
**Reviewer:** Scientific Review Board  
**Investigator:** Saksham Mishra <mishrasaksham080705@gmail.com>

---

## 1. Documented Empirical Failure Cases & Mitigations

In accordance with the directive requirement ("Seek cases where the discovered equation is wrong despite achieving low training error"), the following failure cases were observed and cataloged:

### Defect 1: PySINDy 2.1.0 Differentiation Incompatibility on Windows Python 3.12
- **Issue:** PySINDy's default finite difference solver triggered `ValueError: solve: Input operand 1 does not have enough dimensions` during automated baseline fitting.
- **Root Cause:** NumPy 1.26 vs 2.x array dimensional alignment inside PySINDy 2.1.0's internal differentiator.
- **Mitigation:** In `nomos/evaluation/baselines.py`, `PySINDyAdapter` explicitly computes pre-differentiated velocities $\dot{\mathbf{X}}$ via NOMOS's validated 4th-order differentiator and passes them directly to `model.fit(..., x_dot=x_dot)`.
- **Status:** **RESOLVED & VERIFIED**.

### Defect 2: Small-Angle Collinearity Breakdown in Nonlinear Pendulum
- **Issue:** At $\sigma \ge 0.01$ observation noise, the nonlinear pendulum with composite basis (polynomial + trig) dropped from $F_1 = 1.00$ to $F_1 = 0.52$.
- **Root Cause:** Taylor series approximation $\sin\theta \approx \theta - \frac{\theta^3}{6}$. For small amplitude trajectories ($|\theta| \le 0.5$ rad), $\sin\theta$ and $\theta$ have mutual coherence $\mu > 0.98$, causing the thresholded least squares solver to split coefficient weights between $\sin\theta$ and $\theta$.
- **Scientific Limitation:** Intrinsic structural identifiability limit when candidate libraries contain near-collinear functions over restricted orbital domains.
- **Status:** **DOCUMENTED AS ACCEPTED SCIENTIFIC LIMITATION**.

### Defect 3: Dense OLS Closed-Loop Explosion
- **Issue:** Ordinary Least Squares (OLS) achieves $R^2 > 0.999$ on training derivatives, but its closed-loop rollout diverges to infinity on held-out trajectories.
- **Root Cause:** OLS fits all non-physical candidate terms with tiny coefficients. In closed loop, these unconstrained spurious terms destroy Hamiltonian conservation and cause exponential numerical explosion.
- **Mitigation:** Demonstrates the fundamental necessity of sparse parsimony (STLSQ) in Project NOMOS.
- **Status:** **FALSIFICATION CONFIRMED**.
