# Project NOMOS — Milestone M5.3
## Hypothesis Seeding Elimination & Autonomous Candidate Generation Audit

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target Code Component:** `nomos/closed_loop/controller.py`  
**Execution Timestamp:** November 2026  

---

### 1. Elimination of Ground-Truth-Dependent Seeding

All benchmark-specific string matching and hardcoded physical impostor priors in `nomos/closed_loop/controller.py` have been **completely excised**.

#### Deleted Code Blocks (Historical M5 Defect):
```python
# REMOVED FROM nomos/closed_loop/controller.py (lines 234-275 and 295-348):
- if source_tag == "initial":
-     if "kdv" in field.pde_name:
-         h_adv = ScientificHypothesis(id="hyp_linear_advection_impostor", equation_str="u_t = -2.0000*u_x", parameters={"u_x": -2.0}, ...)
-         self.portfolio.register(h_adv)
-     elif "burgers" in field.pde_name:
-         h_diff = ScientificHypothesis(id="hyp_linear_diffusion_impostor", equation_str="u_t = +0.0500*u_xx", parameters={"u_xx": 0.05}, ...)
-         self.portfolio.register(h_diff)
-     elif "cahn_hilliard" in field.pde_name:
-         h_diff = ScientificHypothesis(id="hyp_ch_biharmonic_damping_impostor", equation_str="u_t = -0.0100*u_xxxx", parameters={"u_xxxx": -0.01}, ...)
-         self.portfolio.register(h_diff)
-     elif "gray_scott" in field.pde_name:
-         h_diff = ScientificHypothesis(id="hyp_gs_diffusion_only", equation_str="v_t = +0.0800*lap_v", parameters={"lap_v": 0.08}, ...)
-     elif "fitzhugh" in field.pde_name:
-         h_diff = ScientificHypothesis(id="hyp_fhn_diffusion_only", equation_str="u_t = +1.0000*lap_u", parameters={"lap_u": 1.0}, ...)
-     elif "navier_stokes" in field.pde_name:
-         h_stokes = ScientificHypothesis(id="hyp_stokes_decay_impostor", equation_str="omega_t = +0.0200*lap_omega", parameters={"lap_omega": 0.02}, ...)
-     elif "brusselator" in field.pde_name:
-         h_diff = ScientificHypothesis(id="hyp_brusselator_diffusion_impostor", equation_str="u_t = +0.1000*lap_u", parameters={"lap_u": 0.1}, ...)
```

---

### 2. Autonomous Data-Driven Candidate Generation Architecture

To replace hand-injected impostors with genuine scientific reasoning, NOMOS implements an **autonomous, three-tier data-driven candidate generation engine**:

```
                                  Observed Field Data u(x, t)
                                               |
                       +-----------------------+-----------------------+
                       |                                               |
                       v                                               v
       Tier 1: Multi-Threshold WSINDy                 Tier 2: Scale-Adaptive Beam Search
    Fits at lambda in {0.015, 0.045, 0.12}          Proposes independent symbolic candidates
    Yields dense vs. sparse candidate models        from grammar
                       |                                               |
                       +-----------------------+-----------------------+
                                               |
                                               v
                             Tier 3: Parsimonious Sub-Model Generation
                         For any candidate with k >= 2 operators,
                         extracts isolated single-operator and linear sub-models,
                         refitting parameters via least-squares directly on the data!
                                               |
                                               v
                                   Hypothesis Portfolio
                         Populated purely from observational data!
```

#### How Autonomous Generation Naturally Discovers Impostors:
When an observation is collected on a solitary wave:
1. Standard WSINDy ($\lambda = 0.045$) fits the full model (which on a solitary wave might capture `u*u_x` and `u_xxx`, or `u_x`).
2. Aggressive WSINDy ($\lambda = 0.12$) drops higher-order terms and retains the single most dominant term: `u_x`. Its coefficient ($\hat{c} \approx -2.0$) is **fitted directly from the regression matrix $\mathbf{G}^T \mathbf{b}$ on the observed solitary wave!**
3. Parsimonious sub-model generation isolates `u_x`, solves $\min_c \| b - c \mathbf{g}_{u_x} \|^2$, and registers $u_t = \hat{c} u_x$ as a competing hypothesis.
4. **The agent discovers the competing linear theory from the data itself!** No string matching. No knowledge of whether the simulator is KdV, Burgers, or anything else.

---

### 3. Separation of Benchmark Categories

To prevent metric conflation and uphold archival integrity, Project NOMOS strictly partitions discovery benchmarks into three distinct categories:

| Category | Benchmark Type | Specification | Admissible Claims |
| :---: | :--- | :--- | :--- |
| **Category A** | **Given-Hypothesis Model Discrimination** | A finite set of pre-specified candidate hypotheses $\{M_1, \dots, M_K\}$ is explicitly declared in advance. The agent's task is experimental design to discriminate between known models. | Claim: *"Active experiment selection discriminates between candidate physical hypotheses with $X\%$ accuracy using $Y$ queries."* **Never claim unassisted discovery.** |
| **Category B** | **Blind Equation Identification (Generic Grammar)** | The simulator identity is completely hidden. The agent is provided only coordinate grids and a declared generic operator grammar (polynomials, derivatives up to 4th order). All hypotheses must be derived from data. | Claim: *"Blind sparse regression with active experiment design recovered the governing differential operators from an overcomplete grammar in $X\%$ of trials."* |
| **Category C** | **Open-Ended Symbolic Structure Discovery** | Genetic programming or neural-symbolic expression grammar searches an unbounded functional space without a fixed candidate matrix. | Claim: *"Open-ended symbolic search discovered the mathematical structure from raw measurements."* |

**Mandatory Reporting Policy:** Results from Category A, Category B, and Category C must **never** be aggregated into a single unqualified "discovery success percentage".
