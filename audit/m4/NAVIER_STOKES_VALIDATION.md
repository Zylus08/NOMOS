# Project NOMOS — Milestone M4
## 2D Incompressible Navier–Stokes Simulator Validation Audit

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 4 Validation  
**Date:** 2026-11-23  

---

### 1. Mathematical Formulation & Hydrodynamic Foundations

The 2D Incompressible Navier–Stokes equations model viscous Newtonian fluid dynamics:
$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla) \mathbf{u} = -\frac{1}{\rho}\nabla p + \nu \nabla^2 \mathbf{u}$$
$$\nabla \cdot \mathbf{u} = 0$$

To eliminate the elliptic pressure constraint $\nabla p$ and enforce incompressibility analytically, NOMOS employs the **vorticity–streamfunction $(\omega, \psi)$ formulation**:
1. Scalar vorticity: $\omega = \nabla \times \mathbf{u} = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}$.
2. Streamfunction: $u = \frac{\partial \psi}{\partial y}, \quad v = -\frac{\partial \psi}{\partial x}$.
3. Incompressibility is satisfied identically: $\nabla \cdot \mathbf{u} = \frac{\partial^2 \psi}{\partial x \partial y} - \frac{\partial^2 \psi}{\partial y \partial x} \equiv 0$.
4. Vorticity transport equation:
   $$\frac{\partial \omega}{\partial t} + u \frac{\partial \omega}{\partial x} + v \frac{\partial \omega}{\partial y} = \nu \nabla^2 \omega + f_\omega$$
   $$\nabla^2 \psi = -\omega$$

---

### 2. Numerical Algorithm Architecture

- **Spectral Poisson Inversion:**
  In 2D Fourier space:
  $$\hat{\psi}(\mathbf{k}) = \begin{cases} \frac{\hat{\omega}(\mathbf{k})}{k_x^2 + k_y^2}, & \mathbf{k} \neq \mathbf{0} \\ 0, & \mathbf{k} = \mathbf{0} \end{cases}$$
  Velocity components are reconstructed spectrally:
  $$\hat{u}(\mathbf{k}) = i k_y \hat{\psi}(\mathbf{k}), \quad \hat{v}(\mathbf{k}) = -i k_x \hat{\psi}(\mathbf{k})$$
- **2/3 Orszag De-Aliasing:**
  To prevent aliasing instabilities arising from quadratic advection $\mathbf{u} \cdot \nabla \omega$, spectral modes satisfying $|\mathbf{k}| > \frac{2}{3} k_{\max}$ are zeroed before physical space transformation.
- **Integrating-Factor RK4 (IF-RK4):**
  Viscous dissipation $L = -\nu (k_x^2 + k_y^2)$ is stepped analytically via the exponential integrating factor $e^{L \Delta t}$, guaranteeing unconditional linear stability.

---

### 3. Empirical Verification: Taylor–Green Analytical Decay

The exact 2D Taylor–Green vortex solution on $[0, 2\pi]^2$ is:
$$\psi(x, y, t) = \cos(x) \cos(y) e^{-2 \nu t}$$
$$u(x, y, t) = -\cos(x) \sin(y) e^{-2 \nu t}, \quad v(x, y, t) = \sin(x) \cos(y) e^{-2 \nu t}$$
$$\omega(x, y, t) = 2 \cos(x) \cos(y) e^{-2 \nu t}$$

For the Taylor–Green vortex, advection vanishes identically:
$$\mathbf{u} \cdot \nabla \omega = u \partial_x \omega + v \partial_y \omega \equiv 0$$
The vortex decays purely through viscous dissipation at rate $e^{-2 \nu t}$.

#### Benchmark Results ($32 \times 32$ grid, $\nu = 0.01$, $t \in [0, 1.0]$, 20 steps)
- **Velocity Incompressibility:**
  $$\max | \nabla \cdot \mathbf{u} | = 3.60 \times 10^{-15} \quad (\text{Machine Precision})$$
- **Taylor–Green $L_\infty$ Error at $t = 1.0$:**
  $$\| \omega_{\text{numerical}} - \omega_{\text{exact}} \|_\infty = 5.11 \times 10^{-15} \quad (\text{Machine Precision})$$
- **Monotonic Energy Dissipation:**
  Total kinetic energy $E(t) = \frac{1}{2} \int (u^2 + v^2) dx dy$ decays exponentially: $\frac{dE}{dt} < 0 \quad \forall t$.
