# Project NOMOS — Milestone M5.2
## Comprehensive Paper Revision Diff & Tracking Ledger

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Baseline Frozen File:** `paper/main_m5_1_original.tex`  
**Revised Publication Target:** `paper/main.tex`  
**Compiled Artifact:** `paper/main.pdf`  

---

### 1. High-Level Summary of Structural Revisions

Following adversarial pre-submission peer review by five specialized review groups (Applied Math, Statistics, Scientific ML, Numerical PDE, and Research Integrity), the manuscript underwent a comprehensive scientific and editorial overhaul. The core thesis was refocused from unconstrained "autonomous discovery of physical laws" to **disagreement-guided experiment selection for reducing false identification on degenerate dynamical manifolds**.

All statistical, physical, and methodological overstatements identified during the red-team audit were formally corrected, qualified, or retracted in `paper/main.tex`.

---

### 2. Line-by-Line Section Revision Ledger

| Section | Original Milestone M5.1 Baseline (`main_m5_1_original.tex`) | Revised Publication Version (`main.tex`) | Scientific Justification & Audit Finding |
| :--- | :--- | :--- | :--- |
| **Title** | `Autonomous Discovery of Physical Governing Laws via Weak-Form Active Experimentation and Falsification Portfolios` | `Disagreement-Guided Experimental Design for Reducing False Identification in Nonlinear Dynamical-System Discovery` | Corrects overstatement: the algorithm selects from discrete candidate pools to break identifiability traps; it does not synthesize arbitrary physical laws. |
| **Abstract** | Claimed $63.0\%$ "exact recovery", asserted GEE "confirms a $2.12\times$ odds ratio ($p=0.0067$)", claimed Cahn–Hilliard recovered with "$<1\%$ parameter error", and claimed query budget cut from $2.38$ to $2.00$ ($p=0.0202$). | Reports $63.0\%$ **support recovery** ($p=0.0215$); discloses that under Tier~1 exact parameters, Fixed beats Active ($21\%$ vs $13\%$); retrained GEE claims due to $K=5$ sandwich bias ($p=0.0913$); reclassified Cahn–Hilliard as Tier~3 partial flux recovery; qualified query efficiency with survivorship bias. | Aligns abstract with empirical data from `RAW_EPISODES.csv` and mathematical reality of small-cluster GEE and 4th-order operator pruning. |
| **Sec. 1: Introduction** | Asserted active agent "actively selects perturbations that force maximum physical disagreement" without qualification. | Added exact algebraic proof of KdV soliton identity; clarified that initial conditions are selected from discrete pools of smooth waveforms. | Grounds the KdV identifiability trap in exact mathematical analysis and scopes the candidate selection space. |
| **Sec. 3.1: Weak Form** | Claimed universal derivative elimination and boundary term elimination. | Added **Domain of Validity**: clarified that derivative elimination holds strictly for **divergence-form terms** ($\nabla \cdot \mathbf{u} = 0$), and acknowledged total blindness to boundary conditions. | Resolves Applied Math (Group A) objection regarding non-divergence nonlinearities and boundary invisibility. |
| **Sec. 3.2: Divergence** | Formulated $\mathcal{D}(u_0)$ without functional constraints. | Added **Short-Time Asymptotics** proving $\lim_{t \to 0^+} \frac{\|u_1 - u_2\|^2}{t^2} = \|\Omega\| \mathcal{D}(u_0)$; proved **Sobolev UV catastrophe** ($k^{2m}$ scaling); defined admissible set $u_0 \in \mathcal{U}_{\text{ad}} \subset H^m(\Omega)$. | Provides rigorous operator-theoretic foundation for instantaneous divergence and explains why candidate pools must be smooth. |
| **Sec. 3.3: $N_{\text{eff}}$ & BIC** | Claimed weights $\tilde{w}_k$ are "temperature-calibrated posterior probabilities" and cited Kass--Raftery Bayes factors. | Reclassified $\tilde{w}_k$ as an **empirical penalized-residual softmax heuristic**, noting that post-selection thresholding breaks Laplace approximations. | Resolves Statistics (Group B) critique on Bayesian posterior mischaracterization. |
| **Table 1** | Reported only Support Recovery ($63\%$ vs $55\%$, $+8.0\%$). | Expanded Table 1 to report **both Support Recovery (Tiers 1, 3, 4)** and **Tier 1 Exact Recovery ($\le 10\%$ error)** with exact binomial $p$-values and Newcombe score CIs. | Resolves Scientific ML (Group C) objection regarding metric conflation. |
| **Sec. 5.1: Paired Tests** | Reported only pooled $p = 0.0215$. | Added **System Stratification & KdV Leverage**: disclosed that $55.6\%$ of discordant wins ($5/9$) come from KdV solitary waves ($b=5, c=0$). | Fully discloses that active gains are concentrated in dispersive wave mechanics. |
| **Sec. 5.2: Clustered GEE** | Claimed GEE "confirms generalizability" ($\beta = 0.7514, p = 0.0067, \text{OR} = 2.12$). | Retracted claim; reported re-estimated model ($\beta = 0.4119, p = 0.0913, \text{OR} = 1.51$); detailed $K=5$ sandwich bias (Cameron \& Miller 2015); centered confirmatory inference on exact paired binomial tests. | Resolves fatal statistical objection regarding small-cluster sandwich covariance bias. |
| **Sec. 5.3: False IDs** | Highlighted passive failure rates without stating Active false ID baseline. | Prominently reported Active's own **$35.1\%$ false identification rate** (34/97 terminating episodes). | Eliminates asymmetric reporting bias. |
| **Sec. 5.4: Query Forensics** | Claimed adaptive query budget reduction ($2.38$ to $2.00$, $p=0.0202$). | Disclosed the **Query 2 stopping invariant** ($\sigma = 0.000$); disclosed survivorship bias in conditional Wilcoxon test; reported unconditional distribution ($2.10$ vs $2.28$, $p=0.0543$); acknowledged KdV candidate pool ordering bias. | Resolves Integrity (Group E) and Statistics (Group B) objections. |
| **Sec. 5.5: Held-Out Systems** | Claimed $50\%$ recovery on Brusselator and "<1% parameter error" on Cahn–Hilliard. | Disclosed that **all 7 strategies tied at 50% on Brusselator**; corrected Turing pattern terminology; reclassified Cahn–Hilliard as **Tier 3 Partial Support**; detailed $100\%$ omission error of 4th-order biharmonic operator and resulting Hadamard instability. | Resolves Numerical PDE (Group D) and Integrity (Group E) objections. |
| **Sec. 6: Limitations** | Omitted explicit boundary limitations section. | Added dedicated **Failure Modes & Boundary Limitations** enumerating discrete pool constraints, impostor seeding, library scaling, and uncertainty-aware failure. | Meets highest archival peer-review transparency standards. |

---

### 3. Verification of LaTeX & PDF Build
- **Source File:** `paper/main.tex`
- **Compiled Target:** `paper/main.pdf`
- **Page Count:** 7 pages (including references and 4 full-width figures)
- **Compilation Status:** **CLEAN (Exit Code 0)**, zero overfull `\hbox`, zero missing citations.
