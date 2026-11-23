# Project NOMOS — Milestone M4
## Multi-Agent Worktree & Workspace Ownership Isolation Matrix

| Division | Domain | Worktree / Workspace | Exclusive Owned Artifacts |
| :--- | :--- | :--- | :--- |
| **Division A** | Coupled PDE Theory & Search Failure | `m4_workspace_a` | `audit/m4/ACTIVE_EXPERIMENT_DESIGN.md`, `audit/m4/NONLINEAR_SEARCH_FAILURE.md` |
| **Division B** | 2D Coupled Simulators | `m4_workspace_b` | `nomos/pde/simulators/`, `audit/m4/2D_SOLVER_VALIDATION.md` |
| **Division C** | 2D Spatial & Spectral Operators | `m4_workspace_c` | `nomos/pde/operators.py`, `audit/m4/NAVIER_STOKES_VALIDATION.md` |
| **Division D** | 2D Multichannel Weak-Form | `m4_workspace_d` | `nomos/pde/weak_form_2d.py`, `audit/m4/MULTICHANNEL_WEAK_FORM.md` |
| **Division E** | Coupled Differential Grammar | `m4_workspace_e` | `nomos/pde/grammar.py`, `audit/m4/COUPLED_AST_GRAMMAR.md` |
| **Division F** | Controlled Benchmark Matrix | `m4_workspace_f` | `experiments/m4/`, `audit/m4/BASELINE_COMPARISON.md`, `audit/m4/RAW_EXPERIMENTS.csv` |
| **Division G** | Neural Guidance Ablation | `m4_workspace_g` | `nomos/pde/symbolic_search.py`, `audit/m4/NEURAL_GUIDANCE_ABLATION.md` |
| **Division H** | Active Experiment Selection | `m4_workspace_h` | `nomos/pde/active_identifiability.py`, `audit/m4/ACTIVE_EXPERIMENT_DESIGN.md` |
| **Division I** | Statistical Forensics & Review | `m4_workspace_i` | `audit/m4/STATISTICAL_ANALYSIS.md`, `audit/m4/LIMITATIONS.md`, `audit/m4/SCIENTIFIC_NOVELTY.md` |
| **Division J** | Integration & Final Certification | `m4_workspace_j` | `audit/m4/M4_FINAL_REPORT.md`, `audit/m4/TEST_RESULTS.txt` |
