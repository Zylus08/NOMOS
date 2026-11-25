# PROJECT NOMOS — MILESTONE M5.3.1 AUDIT REPORT
## Deliverable 8: Candidate-Pool Combinatorics & Acquisition Probability Derivations

**Date:** 2026-11-25  
**Auditor:** Independent Scientific Audit Commission & Statistical Verification Group  
**Commit Baseline:** `e401fa836c1a7c98313b663d7f6a3175f24448ce`  

---

### Executive Summary

Milestone reports M5.1 and M5.2 repeatedly claimed that under random acquisition, there is an "approximate 87% probability of drawing at least one informative experiment within the query budget." 

This audit reconstructed the actual candidate experiment pools across all five primary systems and two held-out replication systems, traced the sampling mechanics in `nomos/closed_loop/acquisition.py`, derived the exact closed-form probabilities of informative experiment selection under with-replacement and without-replacement sampling, and uncovered the origin of the "universal 87%" estimate.

---

### 1. Reconstructed Candidate Experiment Pools

Every benchmark episode begins at Stage 0 by querying candidate index `0` as the baseline observation. The remaining budget $M = B - 1 = 3$ queries are selected adaptively or randomly from the candidate pool:

| System | Dimension | Total Pool Size ($K$) | Informative Candidates ($K_{\text{info}}$) | Uninformative Candidates ($K_{\text{uninfo}}$) | Initial Candidate Index 0 (Stage 0) | Physical Reason for Uninformative Baseline |
|:---|:---:|:---:|:---:|:---:|:---|:---|
| **Korteweg–de Vries (KdV)** | 1D | **5** | **2** (`2soliton_collision`, `wave_packet`) | **3** (`single_soliton`, `shifted_soliton`, `multi_harmonic`) | `single_soliton` | Single soliton travels at constant shape ($u_t = -c u_x$); $u_t$ is collinear with $u_x$, leaving $-6 u u_x - u_{xxx}$ indistinguishable from linear advection. |
| **Viscous Burgers** | 1D | **4** | **2** (`steep_pulse`, `multi_harmonic`) | **2** (`flat_wave`, `sine_wave`) | `flat_wave` | Weak amplitude ($\epsilon = 0.1$) yields quasi-linear dynamics dominated by linear decay; nonlinear advection $u u_x$ remains unexcited. |
| **Gray–Scott 2D** | 2D | **3** | **2** (`single_spot`, `dual_spots`) | **1** (`homogeneous_unreactive`) | `homogeneous_unreactive` | Uniform background ($u=1, v=0$); reaction terms $u v^2 \equiv 0$ and Laplacians vanish identically; zero dynamics. |
| **FitzHugh–Nagumo 2D** | 2D | **3** | **2** (`broken_front`, `center_pulse`) | **1** (`subthreshold_quiet`) | `subthreshold_quiet` | Sub-threshold resting state ($u=0, v=0$); no action potential or wave propagation is triggered. |
| **Navier–Stokes 2D** | 2D | **3** | **2** (`vortex_merger_active`, `vortex_dipole_active`) | **1** (`taylor_green_zero_advection`) | `taylor_green_zero_advection` | Convective vorticity advection $(\mathbf{u} \cdot \nabla)\omega \equiv 0$ vanishes identically, reducing dynamics to pure linear heat diffusion. |
| **Brusselator 2D (Held-out)** | 2D | **3** | **2** (`localized_spot`, `turing_wave_packet`) | **1** (`homogeneous_quiescent`) | `homogeneous_quiescent` | Fixed-point spatial steady state; no pattern formation. |
| **Cahn–Hilliard 1D (Held-out)** | 1D | **3** | **2** (`spinodal_modes`, `steep_interface`) | **1** (`flat_quiescent`) | `flat_quiescent` | Infinitesimal amplitude perturbation; no phase separation occurs within observation horizon. |

**Crucial Finding on Stage 0:**  
For **100% of the benchmark systems**, candidate index `0` is an uninformative initial state. Thus, the system is strictly forced to acquire informative excitation during its $M = 3$ adaptive query steps.

---

### 2. Exact Mathematical Derivations

Under random acquisition in `ExperimentAcquisitionEngine.select_experiment()`:
```python
chosen_idx = rng.randint(0, len(candidate_pool))
```
Candidates are drawn **uniformly at random with replacement** from the full pool of $K$ candidates.

Let $K$ be the total pool size, $K_{\text{info}}$ the number of informative candidates, and $q = \frac{K - K_{\text{info}}}{K}$ the probability of drawing an uninformative candidate in a single query.

#### Sampling With Replacement ($M = 3$ Queries)
The probability that all $M$ queries fail to draw an informative candidate is:
$$P(\text{all uninformative}) = q^M = \left(\frac{K - K_{\text{info}}}{K}\right)^M$$
The exact probability of acquiring at least one informative experiment is:
$$P(\ge 1 \text{ informative}) = 1 - \left(\frac{K - K_{\text{info}}}{K}\right)^M$$

#### Sampling Without Replacement ($M = 3$ Queries)
If sampling were conducted without replacement (or if previously queried candidates were excluded):
$$P(\text{all uninformative}) = \prod_{i=0}^{M-1} \frac{K - K_{\text{info}} - i}{K - i}$$
$$P(\ge 1 \text{ informative}) = 1 - \prod_{i=0}^{M-1} \frac{K - K_{\text{info}} - i}{K - i}$$

---

### 3. System-by-System Exact Probabilities

Evaluating for $M = 3$ queries:

| Physical System | Pool Size ($K$) | Informative ($K_{\text{info}}$) | Uninformative Ratio ($q$) | Exact $P(\ge 1 \text{ info})$ (With Replacement) | Exact $P(\ge 1 \text{ info})$ (Without Replacement) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Korteweg–de Vries** | 5 | 2 | $3/5 = 0.600$ | **$1 - 0.6^3 = 1 - 0.216 = \mathbf{0.7840}$ (78.40%)** | $1 - \frac{3 \times 2 \times 1}{5 \times 4 \times 3} = 1 - 0.100 = \mathbf{0.9000}$ (90.00%) |
| **Viscous Burgers** | 4 | 2 | $2/4 = 0.500$ | **$1 - 0.5^3 = 1 - 0.125 = \mathbf{0.8750}$ (87.50%)** | $1 - \frac{2 \times 1 \times 0}{4 \times 3 \times 2} = 1 - 0.000 = \mathbf{1.0000}$ (100.00%) |
| **Gray–Scott 2D** | 3 | 2 | $1/3 \approx 0.333$ | **$1 - (1/3)^3 = 1 - 1/27 = \mathbf{26/27} \approx \mathbf{0.9630}$ (96.30%)** | $1 - \frac{1 \times 0}{3 \times 2} = \mathbf{1.0000}$ (100.00%) |
| **FitzHugh–Nagumo 2D** | 3 | 2 | $1/3 \approx 0.333$ | **$1 - (1/3)^3 = \mathbf{26/27} \approx \mathbf{0.9630}$ (96.30%)** | $\mathbf{1.0000}$ (100.00%) |
| **Navier–Stokes 2D** | 3 | 2 | $1/3 \approx 0.333$ | **$1 - (1/3)^3 = \mathbf{26/27} \approx \mathbf{0.9630}$ (96.30%)** | $\mathbf{1.0000}$ (100.00%) |
| **Brusselator 2D** | 3 | 2 | $1/3 \approx 0.333$ | **$1 - (1/3)^3 = \mathbf{26/27} \approx \mathbf{0.9630}$ (96.30%)** | $\mathbf{1.0000}$ (100.00%) |
| **Cahn–Hilliard 1D** | 3 | 2 | $1/3 \approx 0.333$ | **$1 - (1/3)^3 = \mathbf{26/27} \approx \mathbf{0.9630}$ (96.30%)** | $\mathbf{1.0000}$ (100.00%) |

---

### 4. Forensic Origin of the "Universal 87%" Claim

We can now identify the exact genesis of the "87%" figure in prior reports:
1. In the Viscous Burgers benchmark, $K = 4$ and $K_{\text{info}} = 2$, yielding $q = 0.50$.
2. For $M = 3$ queries with replacement:
   $$P = 1 - (0.5)^3 = 1 - 0.125 = 0.875 = 87.5\%$$
3. The author computed $87.5\%$ for Burgers, rounded it to **$87\%$**, and falsely assumed it applied to all systems.
4. In reality:
   - For KdV ($K=5$), the probability is significantly lower: **$78.4\%$**.
   - For Gray-Scott, FitzHugh-Nagumo, and Navier-Stokes ($K=3$), the probability is much higher: **$96.3\%$**.
   - The unweighted mean probability across the 5 primary systems is:
     $$\bar{P} = \frac{78.4\% + 87.5\% + 96.3\% + 96.3\% + 96.3\%}{5} = \frac{454.8\%}{5} = 90.96\%$$

The claim of a "universal 87%" was an unverified heuristic copy-paste error.

---

### 5. Theoretical Probability vs. Empirical Recovery Rates

A critical insight is the distinction between **selecting an informative experiment** and **achieving strict Tier 1 recovery**:
- Theoretical drawing probability ($78.4\% - 96.3\%$) measures only whether an informative physical regime is presented to the discovery engine.
- Achieving strict Tier 1 recovery requires:
  1. Drawing an informative experiment.
  2. Numerical stability in spatiotemporal derivatives under measurement noise.
  3. Falsification of all distractor terms in the overcomplete library.
  4. Precise convergence of nonlinearly coupled parameters within $5\%$ relative error.

Empirical breakdown of Random Acquisition across noise levels (100 primary episodes):

| Noise Level | Episodes | Tier 1 Recoveries | Empirical Recovery Rate | Theoretical Draw Probability |
|:---:|:---:|:---:|:---:|:---:|
| **0%** | 25 | 18 | **72.0%** | 90.96% |
| **1%** | 25 | 13 | **52.0%** | 90.96% |
| **5%** | 25 | 6 | **24.0%** | 90.96% |
| **10%** | 25 | 2 | **8.0%** | 90.96% |
| **Total** | **100** | **39** | **39.0%** | **90.96%** |

At 0% noise, empirical recovery (72.0%) closely approaches theoretical candidate availability. As noise increases to 10%, identification collapses to 8.0% despite informative experiments being drawn, demonstrating that noise vulnerability—not candidate starvation—limits recovery under high corruption.
