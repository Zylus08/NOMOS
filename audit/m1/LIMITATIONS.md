# M1 LIMITATIONS, FALSIFICATION & ADVERSARIAL AUDIT
**Roles:** Agents A07, G09, G10  
**Reviewer:** I06 — Research-Novelty Reviewer  
**Investigator:** Saksham Mishra <mishrasaksham080705@gmail.com>

---

## 1. Adversarial Falsification Findings (Division G Red Team)

The scientific objective of Division G is to aggressively attempt to falsify reported discovery results.

### Critical Vulnerabilities Uncovered:
1. **The Inadequate Hypothesis Class Trap:**
   When the nonlinear pendulum is fed to a polynomial-only library, the discovery algorithm fits a Taylor expansion: $\ddot{\theta} \approx -9.81 \theta + 1.63 \theta^3$. Training derivative error is low ($R^2 > 0.99$), but the discovered law violates the true physical restoring force and blows up outside $[-\pi, \pi]$.  
   *Audit Finding:* Low training residual does NOT imply correct physical discovery.
2. **Harmonic Degeneracy in Redundant Dictionaries:**
   If a library includes both $\sin^2(x) + \cos^2(x)$ and $1$, the mutual coherence $\mu = 1.0$. STLSQ arbitrarily selects either representation depending on initial numerical noise.
3. **Phase Space Trajectory Confinement:**
   If training data is restricted to a small region near an equilibrium point, non-identifiability occurs. Multi-trajectory Latin Hypercube sampling is mandatory.

---

## 2. Boundaries of M1 Scientific Claims

1. **No Claim of Unconstrained Symbolic Discovery:** M1 is strictly a candidate library-based sparse recovery system ($\dot{\mathbf{X}} = \mathbf{\Theta}(\mathbf{X})\boldsymbol{\Xi}$). Unconstrained symbolic regression (genetic programming / transformer autoregression) is explicitly deferred to Milestone 2 (M2).
2. **No Claim of Methodological Superiority Over SINDy:** NOMOS M1 establishes the foundational engineering implementation and rigorous multi-agent verification framework; it does not claim to have invented sparse dynamical system identification.
3. **Stiffness & High-Frequency Noise Limitations:** Derivative estimation via Savitzky-Golay breaks down when observation noise exceeds $15\%$ or when sampling intervals violate the Nyquist criterion for the system's highest Lyapunov exponent.
