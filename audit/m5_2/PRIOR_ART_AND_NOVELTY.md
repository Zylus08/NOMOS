# Project NOMOS — Milestone M5.2
## Prior-Art Survey, Comparative Novelty Matrix & Boundary Limitations

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target Manuscript Section:** Section 2 (Related Work) & Section 6 (Discussion)  
**Evaluated Literature:** SINDy, PySINDy, WSINDy, Active SINDy, Bayesian Experimental Design, Symbolic Regression  

---

### 1. Systematic Prior-Art Comparison

| Research Paradigm | Key References | Identification Formulation | Closed-Loop Active Selection? | Acquisition Objective & Cost | Noise Handling Mechanism | Statistical Stopping Criteria |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **Classical SINDy** | Brunton et al. (PNAS 2016) | Strong-form differential ODE/PDE | **NO** (Passive, open-loop) | None (User provides fixed trajectory data) | Finite differences or TVD (Highly noise-sensitive, fails $>1\%$) | Fixed threshold $\lambda$ or heuristic Pareto |
| **PySINDy Package** | de Silva et al. (JOSS 2020), Kaptanoglu (2022) | Strong-form, SR3 regularizer, constrained | **NO** (Passive, open-loop) | None (Requires pre-existing training data) | Smoothed spline / spectral differentiation | Cross-validation / CV score |
| **Weak-Form SINDy (WSINDy)** | Messenger & Bortz (JCP 2021) | Weak-form integral projection via test functions | **NO** (Passive, open-loop) | None (Evaluates single large spatiotemporal dataset) | Integration by parts against smooth test functions (Robust to $>10\%$ noise) | Fixed threshold STLSQ or MSTLS |
| **Active SINDy** | Bakarji et al. (2023) | Strong-form ODE / low-dim dynamics | **YES** (Sequential IC selection) | Trajectory ensemble variance: **$O(|\mathcal{P}| \cdot K)$ forward numerical integrations** | Strong-form smoothing | Heuristic threshold convergence |
| **Bayesian Experimental Design (BED)** | Huan & Marzouk (JCP 2013), Ryan et al. (2016) | Parametric Bayesian posterior | **YES** (Optimal experimental design) | Expected Information Gain / Mutual Information: **MCMC / nested sampling (Prohibitive for PDEs)** | Explicit Gaussian likelihood | Posterior entropy threshold |
| **Symbolic Regression (GP/EQL)** | Schmidt & Lipson (2009), Udrescu & Tegmark (2020) | Free-form expression trees / neural symbolic | **NO** (Passive point-cloud regression) | None (Evolutionary search over candidate topologies) | Regularized MSE loss | Pareto complexity frontier |
| **Project NOMOS (This Work)** | Mishra (2026, Current Manuscript) | **Weak-form spatiotemporal integral WSINDy** | **YES** (Closed-loop portfolio falsification) | **Instantaneous functional vector-field divergence at $t=0$: $O(1)$ spatial operator evaluations ($<1$ ms CPU)** | **Space-time polynomial test functions eliminating all field derivatives** | **Autocorrelation-calibrated Bayes factors ($\text{BIC}_{\text{eff}}$)** |

---

### 2. Delineation of Genuine Methodological Novelty

Project NOMOS advances beyond the state of the art in three specific, defensible dimensions:

1. **Instantaneous Spatial Vector-Field Divergence ($t=0$):**  
   Prior active learning methods for dynamical systems (e.g., Bakarji et al., 2023; Huan & Marzouk, 2013) evaluate candidate queries by integrating forward trajectory rollouts across all candidate models. For continuous spatiotemporal PDEs, simulating $K$ candidate equations across $|\mathcal{P}|$ candidate initial conditions over $[0, T]$ incurs an untenable $O(|\mathcal{P}| \cdot K)$ PDE integration cost. NOMOS resolves this bottleneck by evaluating divergence strictly on spatial differential operators applied to the proposed initial condition slice $u_0(x)$ at $t=0$. This reduces acquisition time to $< 1$ millisecond on a standard CPU, enabling real-time closed-loop decision making without solving forward PDEs.

2. **Integration of Weak-Form PDE Discovery into Active Experimentation:**  
   While WSINDy (Messenger & Bortz, 2021) demonstrated that test-function integration by parts achieves extreme noise robustness on fixed datasets, WSINDy has remained an open-loop, passive identification framework. NOMOS is the first system to couple weak-form integral PDE regression with closed-loop experimental design and hypothesis portfolio maintenance.

3. **Spatiotemporal Autocorrelation Degrees-of-Freedom Calibration ($N_{\text{eff}}$):**  
   Treating every spatiotemporal grid point $(x_i, t_m)$ as an independent observation represents rampant pseudoreplication in continuous field regression, artificially inflating sample sizes by $200\times\text{--}1000\times$ and driving asymptotic criteria (BIC) into overconfident model selection. NOMOS grounds the effective degrees of freedom $N_{\text{eff}} = \frac{L_x T}{4 \xi_x \tau_t}$ in spatial statistics, preventing premature stopping on correlated empirical noise.

---

### 3. Boundary Limitations Honestly Acknowledged

To maintain scientific integrity and withstand peer review, the manuscript must explicitly delineate what NOMOS does **not** do:

1. **Discrete Candidate Pool vs. Continuous Synthesis:**  
   NOMOS does *not* synthesize or optimize continuous initial condition functions from an unconstrained Sobolev space. It selects the optimal index from a human-curated discrete candidate pool of 3 to 5 smooth waveforms.
2. **Hardcoded Impostor Hypotheses:**  
   In the experimental evaluation, competing hypotheses (such as linear advection for KdV or linear diffusion for Burgers) were pre-seeded into the portfolio with calibrated parameters. In unassisted autonomous discovery, these competing models must be discovered directly from initial data.
3. **Incomplete Candidate Libraries:**  
   The candidate feature dictionaries passed to the regression engines contained only 2 to 4 terms matching the true physical operators. Evaluating the framework on overcomplete libraries with extensive spurious distractor terms remains open work.
4. **Boundary Invisibility:**  
   Because compact test functions vanish identically near the boundaries, the weak-form identification engine is blind to boundary conditions (Dirichlet, Neumann, Robin, dynamic flux).
5. **Scale Invariance Barrier:**  
   Uniform-threshold STLSQ cannot identify operators with physical coefficients smaller than the threshold ($\lambda = 0.045 > 0.0025$ in Cahn–Hilliard), requiring multi-scale or column-normalized regularization.
