# M1 PHYSICAL BENCHMARK SPECIFICATIONS
**Role:** Agent B12 — Physical Benchmark Suite Integration  
**Reviewer:** I03 — Experimental Design Reviewer  
**Investigator:** Saksham Mishra <mishrasaksham080705@gmail.com>

---

## 1. Benchmark Suite Overview

The NOMOS M1 suite consists of 5 canonical physical dynamical systems spanning linear, nonlinear, coupled, conservative, dissipative, and chaotic regimes.

| ID | System Name | Dimension | Active Terms / Eq | Conserved Quantity | Dynamics Class |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B01** | Harmonic Oscillator | 2 | 1, 1 | Total Energy $E = \frac{1}{2}\dot{x}^2 + \frac{1}{2}\omega^2 x^2$ | Linear Conservative |
| **B02** | Damped Oscillator | 2 | 1, 2 | Monotonic Energy Dissipation | Linear Dissipative |
| **B03** | Nonlinear Pendulum | 2 | 1, 1 ($\sin\theta$) | Hamiltonian $H = \frac{1}{2}p^2 - \frac{g}{L}\cos\theta$ | Nonlinear Conservative |
| **B05** | Lotka-Volterra | 2 | 2, 2 | Invariant $V = \delta x - \gamma \ln x + \beta y - \alpha \ln y$ | Coupled Nonlinear |
| **B06** | Lorenz-63 | 3 | 2, 3, 2 | Bounded Strange Attractor (Volume Contraction $\text{div} = -(\sigma+1+\beta)$) | Deterministic Chaos |

---

## 2. Canonical Governing Equations & Parameters

### 2.1 Harmonic Oscillator (Linear)
$$\dot{x} = v, \quad \dot{v} = -\omega_0^2 x$$
- Default parameters: $\omega_0 = 1.0 \implies \dot{v} = -1.0 x$.
- State: $[x, v]^T$.
- Candidate Library: Polynomials up to degree 2 or 3.

### 2.2 Damped Harmonic Oscillator
$$\dot{x} = v, \quad \dot{v} = -\omega_0^2 x - 2\zeta\omega_0 v$$
- Default parameters: $\omega_0 = 1.0, \zeta = 0.1 \implies \dot{v} = -1.0 x - 0.2 v$.
- State: $[x, v]^T$.
- Candidate Library: Polynomials up to degree 2.

### 2.3 Simple Nonlinear Pendulum
$$\dot{\theta} = \omega, \quad \dot{\omega} = -\frac{g}{L}\sin(\theta)$$
- Default parameters: $g=9.81, L=1.0 \implies \frac{g}{L} = 9.81$.
- State: $[\theta, \omega]^T$.
- Candidate Library: Polynomials + Trigonometric basis $\{\sin(k\theta), \cos(k\theta)\}$.
- Note: Polynomial-only libraries must be tested to demonstrate failure on trigonometric nonlinearities.

### 2.4 Lotka-Volterra (Predator-Prey)
$$\dot{x} = \alpha x - \beta x y, \quad \dot{y} = \delta x y - \gamma y$$
- Default parameters: $\alpha = 1.5, \beta = 1.0, \gamma = 3.0, \delta = 1.0$.
- State: $[x, y]^T$ (prey, predator).
- Candidate Library: Polynomials up to degree 2.

### 2.5 Lorenz-63 (Deterministic Chaos)
$$\dot{x} = \sigma (y - x), \quad \dot{y} = x (\rho - z) - y, \quad \dot{z} = x y - \beta z$$
- Standard Saltzman/Lorenz parameters: $\sigma = 10.0, \rho = 28.0, \beta = \frac{8}{3} \approx 2.6667$.
- Active expansion:
  - $\dot{x} = -10 x + 10 y$
  - $\dot{y} = 28 x - y - x z$
  - $\dot{z} = -2.6667 z + x y$
- State: $[x, y, z]^T$.
- Candidate Library: Polynomials up to degree 2 or 3 (up to 10 or 20 terms).

---

## 3. Ground-Truth Solver Verification Standards
- Solver: SciPy `solve_ivp` with `DOP853` (8th-order Runge-Kutta Dormand-Prince) or `RK45`.
- Absolute tolerance: $\text{atol} \le 10^{-10}$.
- Relative tolerance: $\text{rtol} \le 10^{-10}$.
- Sampling frequency: $\Delta t = 0.01$ or $0.005$ to guarantee Nyquist sampling of fastest dynamics.
