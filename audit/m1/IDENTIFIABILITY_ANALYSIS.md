# M1 IDENTIFIABILITY & COHERENCE ANALYSIS
**Role:** Agent A01 & G08  
**Reviewer:** I01 — Mathematics Reviewer  
**Investigator:** Saksham Mishra <mishrasaksham080705@gmail.com>

---

## 1. Identifiability in Sparse Dynamics Discovery

Let the true dynamical system be $\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x}) = \mathbf{\Theta}(\mathbf{x})\boldsymbol{\Xi}^*$.
For the discovery engine to recover $\boldsymbol{\Xi}^*$ uniquely:
1. **Column Rank Condition:** For the active support $S \subset \{1, \dots, P\}$ where $\boldsymbol{\Xi}_{j}^* \neq 0$, the submatrix $\mathbf{\Theta}_S(\mathbf{X})$ must have full column rank:
   $$\text{rank}(\mathbf{\Theta}_S(\mathbf{X})) = |S|$$
2. **Nullspace Property:** No non-trivial vector $\mathbf{v} \in \text{null}(\mathbf{\Theta}(\mathbf{X}))$ can have $\|\mathbf{v}\|_0 \le 2s$.
3. **Condition Number of Active Submatrix:**
   $$\kappa(\mathbf{\Theta}_S(\mathbf{X})) = \frac{\sigma_{\max}(\mathbf{\Theta}_S)}{\sigma_{\min}(\mathbf{\Theta}_S)} < \infty$$
   If $\kappa(\mathbf{\Theta}_S) > 10^4$, standard least squares without regularization experiences severe numerical instability.

---

## 2. Identifiability Counterexamples & Edge Cases (Division G Audit)

### 2.1 The Harmonic Identity Degeneracy
If a candidate library includes both $\sin^2(x), \cos^2(x)$ and $1$:
$$\sin^2(x) + \cos^2(x) - 1 = 0 \quad \forall x$$
Then $\mathbf{\Theta}(\mathbf{X})$ has a deterministic zero singular value:
$$\mathbf{\Theta} [1, -1, -1, 0, \dots]^T = \mathbf{0}$$
Sparse regression can substitute $1$ for $\sin^2(x) + \cos^2(x)$, yielding non-unique equations with identical training error.  
*Mitigation in NOMOS:* Linearly dependent basis terms are pruned or detected via SVD tolerance before fitting.

### 2.2 Insufficient Phase Space Coverage
If a linear oscillator is observed for only a fraction of a cycle ($t \in [0, 0.05 T]$), the state $x$ and velocity $v$ are nearly linearly correlated, causing ill-conditioned regression matrices.  
*Mitigation in NOMOS:* Sampling protocols require minimum duration $T_{\text{sim}} \ge 3 T_{\text{char}}$ and multi-trajectory Latin Hypercube initializations.
