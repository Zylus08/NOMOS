# Project NOMOS — Milestone M5
## Generalization & Held-Out Physical System Evaluation

**Principal Investigator / Git Identity:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Milestone:** M5 — Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery  

---

### 1. Generalization Framework

To verify that the closed-loop experimentation framework generalizes across physical mechanisms and spatial dimensions, we evaluate the system across 5 diverse physical model classes:
1. **Dispersive Nonlinear Waves (KdV):** Third-order spatial derivative $u_{xxx}$ and convective transport $u u_x$.
2. **Advective-Diffusive Shocks (Viscous Burgers):** Second-order dissipation $u_{xx}$ and quadratic nonlinearity $u u_x$.
3. **Coupled Turing Morphogenesis (Gray-Scott 2D):** Two coupled parabolic equations with nonlinear cubic consumption $u v^2$ and linear replenishment.
4. **Excitable Neural Systems (FitzHugh-Nagumo 2D):** Coupled reaction-diffusion with cubic activation $u - u^3$ and slow recovery variable $v$.
5. **Incompressible Fluid Dynamics (2D Navier-Stokes):** Streamfunction Poisson inversion, nonlinear convective vorticity transport $\mathbf{u} \cdot \nabla \omega$, and viscosity $\nu \nabla^2 \omega$.

---

### 2. Empirical Performance by Physical System

Across 20 trials per system per strategy (4 noise levels $\times$ 5 seeds):

| Physical System | Dimension | Active (`greedy`) Recovery | Fixed Schedule Recovery | Random Sampling Recovery |
| :--- | :---: | :---: | :---: | :---: |
| **FitzHugh-Nagumo 2D** | 2D Coupled | **100.0%** (20/20) | 100.0% (20/20) | 70.0% (14/20) |
| **Gray-Scott 2D** | 2D Coupled | **85.0%** (17/20) | 75.0% (15/20) | 60.0% (12/20) |
| **KdV Equation** | 1D Dispersive | **55.0%** (11/20) | 30.0% (6/20) | 30.0% (6/20) |
| **Navier-Stokes 2D** | 2D Fluid | **40.0%** (8/20) | 40.0% (8/20) | 35.0% (7/20) |
| **Viscous Burgers** | 1D Shock | **35.0%** (7/20) | 30.0% (6/20) | 35.0% (7/20) |

---

### 3. Cross-Domain Scientific Discoveries

1. **Dimensional Scaling:** The closed-loop controller seamlessly operates across 1D and 2D spatial geometries without architectural modification.
2. **Multi-Channel Coupled Dynamics:** For coupled systems (Gray-Scott and FitzHugh-Nagumo), active experiment acquisition specifically excites regions in state space where both species interact strongly, preventing models from degenerating into uncoupled diffusion equations.
3. **Hydrodynamic Convection Resolution:** In 2D Navier-Stokes, active experiment selection circumvents degenerate initial states like the Taylor-Green vortex (where $\mathbf{u} \cdot \nabla \omega \equiv 0$) by prioritizing interacting vortex pairs (dipoles and mergers), thereby unlocking convective transport discovery.
