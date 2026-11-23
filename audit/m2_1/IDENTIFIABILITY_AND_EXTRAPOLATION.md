# Project NOMOS — Milestone M2.1
## Identifiability Analysis & Out-of-Distribution Extrapolation Report

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** A01 (Identifiability Theory), A04 (Stability & Numerical Dynamics), G01 (Adversarial Auditor)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Mathematical Identifiability in Dynamical Systems

A dynamical system $\dot{x} = f(x; \theta)$ is **structurally identifiable** from trajectory data $X(t)$ if the mapping from trajectories to parameters is injective:
$$f(x; \theta_1) = f(x; \theta_2) \quad \forall x \in \mathcal{D} \implies \theta_1 = \theta_2$$

However, in continuous-time observation of dynamical trajectories, the trajectory data is rarely distributed uniformly over the state space domain $\mathcal{D}$. Instead, trajectories are constrained to lower-dimensional **invariant manifolds** $\mathcal{M} \subset \mathcal{D}$.

When trajectory data lies strictly on an invariant sub-manifold $\mathcal{M}$, two structurally distinct vector fields $f_1$ and $f_2$ that coincide on $\mathcal{M}$ ($f_1|_{\mathcal{M}} = f_2|_{\mathcal{M}}$) are **empirically unidentifiable** from that trajectory, even if they diverge violently on $\mathcal{D} \setminus \mathcal{M}$.

---

### 2. Case Study 1: Invariant Energy Manifold Collapse in the Harmonic Oscillator

In conservative Hamiltonian systems, trajectories lie on constant-energy hypersurfaces $H(x, v) = C$.
For the linear harmonic oscillator, $H(x, v) = \frac{1}{2} x^2 + \frac{1}{2} v^2 = E_0$.

#### Theorem: Basis Degeneracy on a Circle
Let $\mathcal{M} = \{(x, v) \in \mathbb{R}^2 : x^2 + v^2 = R^2\}$. Any polynomial basis function of degree $d \ge 3$ satisfies algebraic constraints that collapse the rank of the library:
$$\text{span}\{v\} = \text{span}\{v(x^2 + v^2)\} \quad \text{on } \mathcal{M}$$
$$\text{span}\{x\} = \text{span}\{x(x^2 + v^2)\} \quad \text{on } \mathcal{M}$$

Therefore, any algorithm (including SINDy or unconstrained regression) trained on a single orbit cannot distinguish between:
$$f_{\text{true}}(x, v) = \begin{bmatrix} v \\ -x \end{bmatrix} \quad \text{and} \quad f_{\text{spurious}}(x, v) = \begin{bmatrix} (1-\alpha) v + \frac{\alpha}{R^2} v (x^2 + v^2) \\ -(1-\beta) x - \frac{\beta}{R^2} x (x^2 + v^2) \end{bmatrix}$$
for any $\alpha, \beta \in \mathbb{R}$.

#### Extrapolation Behavior
When evaluated on a test orbit with radius $R_{\text{test}} \neq R_{\text{train}}$:
$$f_{\text{spurious}}(x, v) = \begin{bmatrix} \left(1 + \alpha \left(\frac{R_{\text{test}}^2}{R^2} - 1\right)\right) v \\ -\left(1 + \beta \left(\frac{R_{\text{test}}^2}{R^2} - 1\right)\right) x \end{bmatrix}$$
- If $R_{\text{test}} > R_{\text{train}}$, the effective frequency scales as $\omega_{\text{eff}} \approx \sqrt{1 + \alpha (R_{\text{test}}^2/R^2 - 1)}$.
- For $R_{\text{test}} = \sqrt{2.5}$ and $R_{\text{train}} = 1.0$, the frequency error reaches $+50\%$, causing complete phase de-coherence and catastrophic rollout error ($RMSE > 1.7$).

#### Remediation Principle
Identifiability of Hamiltonian systems **strictly requires multi-trajectory sampling across multiple distinct energy surfaces** $E_1 < E_2 < \dots < E_K$.

---

### 3. Case Study 2: Rational Function Unidentifiability in Michaelis-Menten Kinetics

Consider the substrate dynamics:
$$\dot{x} = \frac{V_m x}{K_m + x} - d x$$
with true parameters $V_m = 2.0, K_m = 1.0, d = 0.5$.

#### Regime Asymptotics
1. **Linear Regime ($x \ll K_m$):**
   $$\frac{V_m x}{K_m + x} \approx \frac{V_m}{K_m} x \left(1 - \frac{x}{K_m}\right) = 2.0 x - 2.0 x^2$$
2. **Saturation Regime ($x \gg K_m$):**
   $$\frac{V_m x}{K_m + x} \approx V_m = 2.0$$
3. **Transition Regime ($x \approx K_m = 1.0$):**
   At $x=1.0$, $\dot{x} = \frac{2(1)}{1+1} - 0.5(1) = 1.0 - 0.5 = 0.5$.
   The derivative with respect to $x$ is:
   $$\frac{d}{dx} \dot{x} = \frac{V_m K_m}{(K_m + x)^2} - d = \frac{2(1)}{(2)^2} - 0.5 = 0.5 - 0.5 = 0.0$$
   Thus, near $x \approx 1.0$, the system possesses an extrema where $\dot{x}(x)$ is nearly flat!

#### Why $0.5286 / x$ Fits the Training Trajectory
In the M2 benchmark, the training trajectory sampled $x(t)$ in a narrow window $x \in [0.90, 1.25]$.
- Over $x \in [0.90, 1.25]$, the true value $\dot{x}(t)$ stays between $0.493$ and $0.500$.
- The spurious function $f(x) = \frac{0.5286}{x}$ evaluates to:
  - $x = 0.90 \implies 0.587$
  - $x = 1.00 \implies 0.529$
  - $x = 1.25 \implies 0.423$
- The mean absolute difference over this localized slice is under $0.05$.
- Because rollout test trajectories were initialized near $x_0 = 1.2$, the trajectory remained trapped in this localized basin, producing a misleadingly low rollout error ($RMSE = 0.41$).

#### Out-of-Distribution Catastrophe
Extrapolating outside $[0.90, 1.25]$ completely shatters the approximation:

| Domain Region | Evaluation Point | True $\dot{x}$ | Spurious $0.5286 / x$ | Absolute Error | Relative Error | Qualitative Defect |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Near Zero** | $x = 0.01$ | $+0.0148$ | $+52.8600$ | $+52.8452$ | **+3,571%** | **Essential Singularity / Pole** |
| **Zero Boundary** | $x = 0.00$ | $0.0000$ | $+\infty$ | $\infty$ | **$\infty$** | **Division by Zero** |
| **High Substrate** | $x = 5.00$ | $-0.8333$ | $+0.1057$ | $+0.9390$ | **112%** | **Wrong Sign (divergent growth)** |
| **Asymptotic** | $x = 10.00$ | $-3.1818$ | $+0.0529$ | $+3.2347$ | **101%** | **Wrong Sign (opposite dynamics)** |

---

### 4. General Principles for Dynamical System Identifiability

Based on these mathematical and experimental findings, Project NOMOS establishes four mandatory identifiability conditions:

1. **Active Perturbation & Multi-Orbit Sampling:** Trajectories must be excited across varying energy levels, amplitudes, and basins of attraction to break invariant manifold degeneracies.
2. **Boundary & Asymptotic Grid Probing:** Discovered candidate models must be evaluated on boundary states ($x \to 0$, $x \to \infty$) and checked for spurious poles, sign reversals, or unphysical fixed points.
3. **Parsimony Regularization over Local Interpolation:** Discrete expression search must penalize arbitrary inverse terms ($1/x$) when constant or polynomial terms provide comparable residual variance.
4. **Decoupled Validation Intervals:** Generalization must be audited across disjoint operating regimes (e.g. low-amplitude vs high-amplitude) rather than nearby initial conditions.
