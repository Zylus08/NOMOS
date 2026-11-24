# Project NOMOS — Milestone M5.3
## Root-Cause Analysis: Ground-Truth Impostor Seeding Defect

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target File:** `nomos/closed_loop/controller.py` (lines 234–275, 294–348)  
**Execution Timestamp:** November 2026  

---

### 1. Root-Cause Autopsy

#### 1.1 Developmental Context & Origin of Defect
During Milestone M4 and early Milestone M5 development, the engineering objective was to construct a proof-of-concept showing that instantaneous functional vector-field divergence ($\mathcal{D}(u_0)$) could break the rank-deficiency of the KdV solitary wave manifold.

To test this mechanism in unit tests (`test_controller.py`), the author needed two competing hypotheses in the hypothesis portfolio:
1. Candidate 1: The true KdV equation ($\partial_t u = -6 u u_x - u_{xxx}$).
2. Candidate 2: The degenerate linear advection competitor ($\partial_t u = -c u_x$).

Instead of implementing an autonomous multi-hypothesis generation routine (such as fitting weak-form models across a spectrum of sparsification thresholds $\lambda \in [0.005, 0.10]$ or generating parsimonious sub-models), the author hardcoded an `if "kdv" in field.pde_name:` branch in `ClosedLoopController._generate_candidate_hypotheses`. This branch directly registered `hyp_linear_advection_impostor` with parameter `u_x: -2.0` (matching the simulator's exact phase speed $c = 2.0$).

When the project progressed from unit testing to large-scale benchmark evaluation (500 episodes in M5 and 280 episodes in M5.1), **this diagnostic test fixture was never removed from `controller.py`**. Furthermore, matching impostors with exact simulator parameters were added for Burgers ($\nu = 0.05$), Gray–Scott ($D_v = 0.08$), FitzHugh–Nagumo ($D_u = 1.0$), Navier–Stokes ($\nu = 0.02$), Brusselator ($D_u = 0.1$), and Cahn–Hilliard ($\gamma \epsilon^2 = 0.01$).

---

### 2. Forensic Code Evidence

In `nomos/closed_loop/controller.py`:
```python
# Lines 234-275 (1D Impostors)
if source_tag == "initial":
    if "kdv" in field.pde_name:
        h_adv = ScientificHypothesis(
            id="hyp_linear_advection_impostor",
            equation_str="u_t = -2.0000*u_x",
            features=["u_x"],
            parameters={"u_x": -2.0},              # Ground-truth speed c = 2.0
            complexity=2,
            origin="competing_physical_prior",
            train_mse=0.001,
            val_mse=0.001,
            bic=0.0,
        )
        self.portfolio.register(h_adv)
    elif "burgers" in field.pde_name:
        h_diff = ScientificHypothesis(
            id="hyp_linear_diffusion_impostor",
            equation_str="u_t = +0.0500*u_xx",
            features=["u_xx"],
            parameters={"u_xx": 0.05},              # Ground-truth viscosity nu = 0.05
            complexity=2,
            origin="competing_physical_prior",
            train_mse=0.001,
            val_mse=0.001,
            bic=0.0,
        )
        self.portfolio.register(h_diff)
    elif "cahn_hilliard" in field.pde_name:
        h_diff = ScientificHypothesis(
            id="hyp_ch_biharmonic_damping_impostor",
            equation_str="u_t = -0.0100*u_xxxx",
            features=["u_xxxx"],
            parameters={"u_xxxx": -0.01},           # Ground-truth parameter scale
            complexity=2,
            origin="competing_physical_prior",
            train_mse=0.001,
            val_mse=0.001,
            bic=0.0,
        )
        self.portfolio.register(h_diff)

# Lines 295-348 (2D Impostors)
if source_tag == "initial":
    if "gray_scott" in field.pde_name:
        h_diff = ScientificHypothesis(
            id="hyp_gs_diffusion_only",
            equation_str="v_t = +0.0800*lap_v",
            features=["lap_v"],
            parameters={"lap_v": 0.08},             # Ground-truth Dv = 0.08
            ...
        )
    elif "fitzhugh" in field.pde_name:
        h_diff = ScientificHypothesis(
            id="hyp_fhn_diffusion_only",
            equation_str="u_t = +1.0000*lap_u",
            parameters={"lap_u": 1.0},              # Ground-truth Du = 1.0
            ...
        )
    elif "navier_stokes" in field.pde_name:
        h_stokes = ScientificHypothesis(
            id="hyp_stokes_decay_impostor",
            equation_str="omega_t = +0.0200*lap_omega",
            parameters={"lap_omega": 0.02},         # Ground-truth nu = 0.02
            ...
        )
    elif "brusselator" in field.pde_name:
        h_diff = ScientificHypothesis(
            id="hyp_brusselator_diffusion_impostor",
            equation_str="u_t = +0.1000*lap_u",
            parameters={"lap_u": 0.1},              # Ground-truth Du = 0.1
            ...
        )
```

---

### 3. Impact Analysis on Prior Experimental Claims

The presence of this defect fundamentally undermined three central claims made in Milestones M5 and M5.1:

1. **The Claim of Autonomous Discovery:**  
   The system did not discover competing physical theories from data. It was handed the exact mathematical degenerate impostor pre-populated with calibrated coefficients. Discovery was reduced to choosing between Candidate A (discovered by WSINDy) and Candidate B (hand-injected ground-truth impostor).
2. **The "Query 2" Efficiency Invariant:**  
   Because the injected impostor was physically calibrated to match the degenerate initial state (Query 1), its initial residual was tiny ($\text{MSE} = 0.001, \text{BIC} = 0.0$). At Query 2, the actively queried wave packet broke the degeneracy, causing the impostor's error to spike. WSINDy fitted the true equation, causing $\Delta\text{BIC} \ge 10.0$ to be triggered instantly at Query 2 in $100\%$ of successful episodes.
3. **Generalization Claims:**  
   Because the controller branched on specific system names (`"kdv"`, `"burgers"`, `"gray_scott"`, `"fitzhugh"`, `"navier_stokes"`, `"brusselator"`, `"cahn_hilliard"`), the controller was incapable of operating on an unknown physical system whose name was not present in the `if/elif` chain.

---

### 4. Corrective Strategy for Milestone M5.3

To achieve certified scientific validity, Milestone M5.3 executes the following refactoring:
1. **Complete Deletion of String Branching:** Purge all `if "<name>" in field.pde_name` blocks from `nomos/closed_loop/controller.py`.
2. **Opaque Observation Interface:** Sanitize `SpatiotemporalField` so that `pde_name` is scrubbed or replaced with an opaque random hash (`blind_obs_<uuid>`).
3. **Autonomous Data-Driven Portfolio Generation:** Generate alternative candidate hypotheses purely from observations using:
   - Weak-form sparse identification at multiple sparsification thresholds (e.g. $\lambda_{\text{loose}} = 0.01$, $\lambda_{\text{standard}} = 0.045$, $\lambda_{\text{tight}} = 0.10$).
   - Hierarchical sub-model extraction (parsimonious subsets of the full WSINDy fit).
   - Scale-adaptive symbolic beam search.
4. **Separation of Benchmark Categories:** Maintain strict separation between:
   - **Category A:** Given-Hypothesis Model Discrimination (where competing hypotheses are declared in advance).
   - **Category B:** Blind Equation Identification with a declared generic grammar (no given hypotheses, no system names).
   - **Category C:** Open-Ended Symbolic Discovery.
