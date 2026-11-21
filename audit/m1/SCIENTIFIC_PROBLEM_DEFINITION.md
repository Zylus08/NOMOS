# M1 SCIENTIFIC PROBLEM DEFINITION & IDENTIFIABILITY
**Role:** Agent A01 — Mathematical Problem Formulation & Identifiability  
**Reviewer:** I01 — Mathematics Reviewer  
**Investigator:** Saksham Mishra <mishrasaksham080705@gmail.com>

---

## 1. Problem Statement

Let an autonomous continuous dynamical system be governed by a set of ordinary differential equations (ODEs):
$$\frac{d\mathbf{x}}{dt} = \mathbf{f}(\mathbf{x}(t); \boldsymbol{\mu}), \quad \mathbf{x}(t_0) = \mathbf{x}_0$$
where:
- $\mathbf{x}(t) = [x_1(t), x_2(t), \dots, x_n(t)]^T \in \mathcal{D} \subseteq \mathbb{R}^n$ is the state vector.
- $\boldsymbol{\mu} \in \mathbb{R}^p$ is an unknown parameter vector.
- $\mathbf{f}: \mathbb{R}^n \to \mathbb{R}^n$ is a smooth (or piecewise analytic) vector field.

We do not have access to $\mathbf{f}$ or $\boldsymbol{\mu}$. Instead, we are given a sequence of noisy or discrete temporal observations across $K$ distinct trajectories:
$$\mathbf{Y}^{(k)}(t_j) = \mathbf{x}^{(k)}(t_j) + \boldsymbol{\epsilon}_{k,j}, \quad j = 1, \dots, M_k, \quad k = 1, \dots, K$$
where $\boldsymbol{\epsilon}_{k,j} \sim \mathcal{N}(\mathbf{0}, \boldsymbol{\Sigma}_\epsilon)$ represents measurement uncertainty.

The scientific objective of **NOMOS M1** is:
1. Reconstruct numerical derivatives $\dot{\mathbf{X}} \approx \frac{d\mathbf{x}}{dt}$ from $\mathbf{Y}$.
2. Construct a candidate function library $\mathbf{\Theta}(\mathbf{X}) \in \mathbb{R}^{M \times P}$.
3. Solve the sparse linear regression problem $\dot{\mathbf{X}} = \mathbf{\Theta}(\mathbf{X}) \boldsymbol{\Xi}$ such that $\boldsymbol{\Xi}$ is parsimonious ($\|\boldsymbol{\Xi}\|_0 \ll P$).
4. Convert $\boldsymbol{\Xi}$ into human-interpretable symbolic differential equations.
5. Guarantee generalization to unseen initial conditions $\mathbf{x}_0 \notin \mathcal{X}_{\text{train}}$ and parameter regimes.

---

## 2. Mathematical Identifiability & Exact Recovery Conditions

The dynamical system is identifiable on the dictionary $\mathbf{\Theta}(\mathbf{X})$ if and only if there exists a unique sparse matrix $\boldsymbol{\Xi}^*$ satisfying:
$$\dot{\mathbf{X}} = \mathbf{\Theta}(\mathbf{X}) \boldsymbol{\Xi}^*$$

### 2.1 Restricted Isometry & Coherence
Let $\mathbf{a}_i$ be the $i$-th column of $\mathbf{\Theta}(\mathbf{X})$ normalized such that $\|\mathbf{a}_i\|_2 = 1$. The mutual coherence $\mu(\mathbf{\Theta})$ is defined as:
$$\mu(\mathbf{\Theta}) = \max_{i \neq j} |\mathbf{a}_i^T \mathbf{a}_j|$$

**Theorem (Unique Sparse Support):**  
If the true sparsity of equation $k$ is $s_k = \|\boldsymbol{\xi}_k^*\|_0$, and the mutual coherence satisfies:
$$s_k < \frac{1}{2} \left(1 + \frac{1}{\mu(\mathbf{\Theta})}\right)$$
then $\boldsymbol{\xi}_k^*$ is the unique sparsest solution to $\dot{\mathbf{x}}_k = \mathbf{\Theta}(\mathbf{X})\boldsymbol{\xi}_k$.

### 2.2 Known Identifiability Failure Modes
1. **Collinear Features:** When library includes both $\sin^2(x) + \cos^2(x)$ and $1$, or collinear monomials in narrow regions of phase space.
2. **Insufficient Excitation:** When trajectories remain confined to a lower-dimensional attractor or manifold (e.g. fixed point), preventing excitation of orthogonal candidate terms.
3. **Severe Derivative Error:** When observation noise variance $\sigma^2$ exceeds the signal threshold, inducing biased derivative estimates that select spurious terms.
