# Project NOMOS — Milestone M5.2
## Comprehensive Catalog of Reviewer Objections & Adversarial Criticisms

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target Manuscript:** `paper/main.tex` (Milestone M5.1 Baseline)  

---

### 1. Statistical & Clustered Inference Objections (Group B & Group E)

1. **Fatal Finite-Sample Cluster Bias in GEE ($K=5$):**  
   *Objection:* Relying on asymptotic sandwich variance estimators with only 5 physical system clusters to claim an odds ratio of $2.12$ ($p = 0.0067$) is methodologically invalid. Standard econometric and biostatistical literature (Cameron & Miller 2015; Mancl & DeRouen 2001) proves sandwich standard errors are downward-biased by $30\%\text{--}50\%$ at $K=5$, producing empirical false positive rates of $20\%\text{--}50\%$ under the null. Re-estimating the model yields $p = 0.0913$, which is non-significant.  
   *Action Taken:* Retracted asymptotic GEE cross-system generalization claims. Re-centered primary statistical inference strictly on the exact, finite-sample paired binomial tests across the 100 scenario conditions.

2. **KdV Leverage & Lack of Cross-System Uniformity:**  
   *Objection:* Over $55.6\%$ of all discordant wins ($5/9$) come from a single physical equation (KdV). On the remaining four physical systems, the active advantage over fixed schedules collapses to $b=4, c=1$ across 80 pairs, yielding $p = 0.375$ (completely non-significant).  
   *Action Taken:* Added transparent system-stratified breakdown to Section 5.1 and Table 1, explicitly disclosing that the active advantage is heavily leveraged on breaking KdV solitary wave degeneracies.

3. **Survivorship Bias in Query Efficiency Reporting:**  
   *Objection:* The claimed query budget reduction from $2.38$ to $2.00$ ($p = 0.0202$) conditions strictly on the 54 mutually successful runs. Across all successful active episodes, the algorithm stopped exclusively on Query 2 ($\sigma = 0.000$). Active never recovered at Query 3 or 4. Furthermore, active suffered a $35.1\%$ false identification rate.  
   *Action Taken:* Disclosed the Query 2 stopping mechanics, reported unconditional query distributions across all episodes, and prominently displayed the $35.1\%$ false identification rate.

4. **BIC Weights Mischaracterized as Bayesian Posteriors:**  
   *Objection:* In post-selection thresholded regression (STLSQ), standard Laplace approximations fail. Labeling $\tilde{w}_k$ as "temperature-calibrated posterior probabilities" and citing Kass & Raftery Bayes factor thresholds conflates an empirical softmax heuristic with true integrated marginal likelihoods.  
   *Action Taken:* Replaced "Bayesian posterior weighting" with "empirical softmax heuristic over autocorrelation-penalized residuals".

---

### 2. Operator Theory & Applied Mathematics Objections (Group A)

1. **Variational Ill-Posedness of Continuous $\mathcal{D}(u_0)$ (UV Blowup):**  
   *Objection:* For differential operators of order $m$ ($m=3$ for KdV, $m=4$ for Cahn–Hilliard), the functional divergence $\mathcal{D}(u_0)$ scales as $k^{2m}$ in Fourier space ($k^6$ for KdV, $k^8$ for Cahn–Hilliard). Continuous maximization over $L^2$-bounded initial states is ill-posed and blows up at the grid Nyquist frequency. The algorithm works solely because it is restricted to a small discrete candidate pool of smooth states.  
   *Action Taken:* Added formal Sobolev space definition $u_0 \in \mathcal{U}_{\text{ad}} \subset H^m(\Omega)$, proved the short-time asymptotic connection between $\mathcal{D}(u_0)$ and $L^2$ trajectory divergence, and acknowledged that unconstrained continuous optimization requires high-order Sobolev regularization.

2. **Boundary Invisibility of Compact Weak Form:**  
   *Objection:* Restricting spacetime polynomial test functions to the domain interior eliminates boundary terms analytically, but renders the algorithm completely blind to boundary conditions (Dirichlet, Neumann, wall shear).  
   *Action Taken:* Added explicit boundary limitation remarks in Section 3.1 and Section 6.

3. **Non-Divergence / Gradient-Product Nonlinearity Limits:**  
   *Objection:* Integration by parts eliminates derivatives of noisy state fields only for divergence-form terms (e.g., $(u^2)_x, (u^3)_{xx}, \nabla \cdot (\omega \mathbf{u})$ with $\nabla \cdot \mathbf{u} = 0$). For non-conservative terms (e.g. $u v_x$ or $(\nabla u)^2$), field derivatives cannot be eliminated.  
   *Action Taken:* Delineated the exact class of divergence-form PDEs supported by derivative-free weak form in Section 3.1.

---

### 3. Scientific ML & Evaluation Standards Objections (Group C)

1. **The Exact Recovery Conflation (Tier 1 vs. Support):**  
   *Objection:* The paper claimed a 63% exact recovery rate. Code audit reveals the evaluator checked only feature key presence without checking parameter errors. Under true Tier 1 exact recovery (parameter errors $\le 10\%$), Fixed schedules beat Active experimentation by 21% to 13%! The 63% figure represents support / dominant operator identification (Tiers 1, 3, 4).  
   *Action Taken:* Retitled paper and refocused thesis on *reducing false identification and resolving identifiability traps*. Fully reported the 6-tier hierarchy, distinguishing Tier 1 exact parametric recovery from composite support recovery.

2. **Discrete Candidate Pool vs. Autonomous Discovery:**  
   *Objection:* The agent does not design continuous experiments; it evaluates an argmax over 3 to 5 hand-crafted waveforms.  
   *Action Taken:* Changed paper title from "Autonomous Discovery of Physical Governing Laws..." to *"Disagreement-Guided Experimental Design for Reducing False Identification in Nonlinear Dynamical-System Discovery"*, and clearly documented discrete candidate pool boundaries.

3. **Catastrophic Failure of Uncertainty-Aware Baseline:**  
   *Objection:* The paper failed to explain why the standard active learning baseline (`uncertainty_aware` / Max Variance) collapsed to $20.0\%$ recovery rate.  
   *Action Taken:* Added comprehensive forensic explanation in Section 4.2 detailing how weight collapse ($\tilde{w}_1 \tilde{w}_2 \to 0$) and fringe model distortions destroy predictive variance in small portfolios.

---

### 4. Numerical PDE & Physical Consistency Objections (Group D)

1. **Deceptive Cahn–Hilliard Parameter Error Claim:**  
   *Objection:* Claiming "<1% parameter error" on Cahn–Hilliard is egregious cherry-picking: it applies only to the cubic flux, while linear diffusion has $6.45\%$ error and the 4th-order biharmonic operator was completely omitted ($100\%$ error).  
   *Action Taken:* Retracted "<1% parameter error" claim. Reclassified Cahn–Hilliard as Tier 3 Partial Support.

2. **Hadamard Ill-Posedness of Truncated Cahn–Hilliard Model:**  
   *Objection:* Omitting $-0.0025 u_{xxxx}$ leaves an ill-posed backward parabolic equation with Hadamard instability in the spinodal interval ($|u| < 1/\sqrt{3}$). The discovered model blows up in forward simulation.  
   *Action Taken:* Added thorough physical analysis in Section 5.5 explaining why uniform STLSQ thresholding failed on the biharmonic term and discussing the resulting Hadamard instability.

3. **De-Aliasing Violations in Simulators:**  
   *Objection:* Orszag 2/3 mask was applied to cubic terms in Cahn–Hilliard (violating the 1/2 rule), and zero de-aliasing was used in 2D Brusselator.  
   *Action Taken:* Documented numerical discretization limitations in Section 4.1.

4. **Brusselator Turing Myth:**  
   *Objection:* Parameters $D_u = 0.1, D_v = 0.05$ have $D_u > D_v$, mathematically precluding Turing spatial patterns. Calling perturbations "Turing-spot drivers" is incorrect.  
   *Action Taken:* Corrected physical descriptions to "autocatalytic limit-cycle reaction dynamics".

---

### 5. Integrity & Leakage Objections (Group E)

1. **System Identity Inspection & Ground-Truth Parameter Leakage:**  
   *Objection:* In `controller.py`, the code checked `field.pde_name` and injected competing impostor hypotheses containing the simulator's exact ground-truth parameters ($c=2.0, \nu=0.05, D_v=0.08, \text{etc.}$).  
   *Action Taken:* Fully disclosed in Section 4.1 and Section 6 as an engineered experimental benchmark evaluating active discrimination between specific competing physical theories, rather than unassisted open-world discovery.

2. **Candidate Pool Ordering Handicap on Fixed Schedules:**  
   *Objection:* In KdV, index 0 and index 1 were both degenerate solitary waves, artificially delaying fixed schedules to 2.38 queries.  
   *Action Taken:* Acknowledged candidate ordering bias in Section 5.4.

3. **Concealment of Baseline Parity on Held-Out Systems:**  
   *Objection:* On 2D Brusselator, all seven strategies achieved identical 50.0% recovery in 2.0 queries, but this parity was omitted from the narrative in Section 5.5.  
   *Action Taken:* Fully reported the 7-way parity on Brusselator in Section 5.5.
