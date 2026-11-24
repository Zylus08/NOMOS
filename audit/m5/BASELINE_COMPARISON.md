# Project NOMOS — Milestone M5
## Baseline Comparison: Active Experimentation vs Passive & Stochastic Protocols

**Principal Investigator / Git Identity:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Milestone:** M5 — Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery  

---

### 1. Comparative Performance Overview

Across 500 controlled empirical trials spanning 5 physical dynamical systems and 4 noise regimes, active closed-loop experimentation demonstrated a marked, reproducible advantage over passive fixed schedules and uniform random sampling:

| Strategy | Total Trials | Overall Recovery Rate | Mean Queries to Stop | Mean Compute Time (s) |
| :--- | :---: | :---: | :---: | :---: |
| **Active (`greedy_disagreement`)** | 100 | **63.0%** (63/100) | **2.10** | 0.3898 |
| **Active (`cost_normalized`)** | 100 | **61.0%** (61/100) | **2.07** | 0.3520 |
| **Passive (`fixed` schedule)** | 100 | 55.0% (55/100) | 2.28 | 0.3962 |
| **Stochastic (`random` selection)** | 100 | 46.0% (46/100) | 2.17 | 0.4085 |
| **Ensemble (`uncertainty_aware`)** | 100 | 20.0% (20/100) | 2.29 | 0.3876 |

---

### 2. Physical System Breakdown

#### 1. Korteweg-de Vries (KdV) Equation (1D Dispersive Nonlinear Wave)
- **Active Disagreement Recovery:** **55.0%** (11/20)
- **Cost Normalized Recovery:** **55.0%** (11/20)
- **Fixed Schedule Recovery:** **30.0%** (6/20)
- **Random Selection Recovery:** **30.0%** (6/20)
- **Analysis:** On KdV, solitary waves move at constant velocity without changing shape, rendering linear advection ($u_t = -c u_x$) indistinguishable from KdV ($u_t = -6 u u_x - u_{xxx}$). The fixed schedule queries shifted solitary waves, failing to separate advection. Active acquisition autonomously targets oscillatory wave packets and 2-soliton collisions, elevating recovery by $+25.0\%$ absolute ($+83.3\%$ relative gain).

#### 2. Gray-Scott Reaction-Diffusion (2D Coupled Morphogenesis)
- **Active Disagreement Recovery:** **85.0%** (17/20)
- **Fixed Schedule Recovery:** **75.0%** (15/20)
- **Random Selection Recovery:** **60.0%** (12/20)
- **Analysis:** Passive sampling frequently queries quiescent or homogeneous initial states where reaction kinetics vanish ($u \cdot v^2 \approx 0$). Active acquisition detects high vector-field divergence under localized perturbations, activating nonlinear reaction dynamics and improving recovery by $+25.0\%$ over random sampling.

#### 3. FitzHugh-Nagumo Reaction-Diffusion (2D Excitable Media)
- **Active Disagreement Recovery:** **100.0%** (20/20)
- **Fixed Schedule Recovery:** **100.0%** (20/20)
- **Random Selection Recovery:** **70.0%** (14/20)
- **Analysis:** Random acquisition risks querying sub-threshold quiet states where excitable fronts never ignite. Both active and structured fixed protocols consistently recover the cubic reaction terms ($u - u^3 - v$) and diffusion.

#### 4. Incompressible Navier-Stokes Equations (2D Fluid Vorticity)
- **Active Disagreement Recovery:** **40.0%** (8/20)
- **Fixed Schedule Recovery:** **40.0%** (8/20)
- **Random Selection Recovery:** **35.0%** (7/20)
- **Analysis:** In Taylor-Green vortices, nonlinear convective advection $\mathbf{u} \cdot \nabla \omega \equiv 0$ vanishes identically. Active acquisition selects vortex merger and vortex dipole initial conditions, unlocking convective advection identification. Under higher noise ($\ge 5\%$), vorticity gradient noise poses a challenge for both methods.

#### 5. Viscous Burgers' Equation (1D Shock Formation)
- **Active Disagreement Recovery:** **35.0%** (7/20)
- **Fixed Schedule Recovery:** **30.0%** (6/20)
- **Random Selection Recovery:** **35.0%** (7/20)
- **Analysis:** Small-amplitude waves exhibit quasi-linear advection-diffusion. Active experimentation favors steep localized pulses where nonlinear steepening terms dominate.

---

### 3. Summary of Baseline Findings

1. **Active vs Fixed:** Active closed-loop experimentation achieves a $+8.0\%$ absolute recovery gain across all regimes and an $+83.3\%$ relative recovery gain on dispersive systems (KdV).
2. **Active vs Random:** Active experimentation achieves a $+17.0\%$ absolute recovery gain over random exploration ($63.0\%$ vs $46.0\%$).
3. **Sample Efficiency:** Active experimentation terminates with conclusive identifiability in significantly fewer trajectory queries ($2.10$ vs $2.28$, Wilcoxon $p = 0.0202$).
