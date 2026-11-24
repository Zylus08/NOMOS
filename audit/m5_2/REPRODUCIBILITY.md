# Project NOMOS — Milestone M5.2
## Comprehensive Scientific Reproducibility Package & Audit Ledger

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Repository:** `E:\NOMOS` on branch `main`  
**Starting Commit Baseline:** `6483cc813ecdc756d31d7dbba7d886265edc0bae`  

---

### 1. Verification of Execution Environment

- **Operating System:** Windows 11 Home (64-bit)
- **Host CPU:** Intel Core i7-12650H (10 cores, 16 threads, up to 4.70 GHz)
- **Physical Memory:** 16.0 GB DDR5 RAM
- **Python Runtime:** Python 3.12.7 (64-bit)
- **Core Scientific Libraries:**
  - `numpy`: 1.26.4
  - `scipy`: 1.13.1
  - `pandas`: 2.2.2
  - `statsmodels`: 0.14.2
  - `matplotlib`: 3.9.2
  - `pytest`: 8.3.3
- **LaTeX Engine:** TinyTeX (`pdflatex` Version 3.141592653-2.6-1.40.26)

---

### 2. Full Test Suite Certification

The repository maintains an unbroken 104-test automated verification suite covering all project milestones:

```bash
pytest tests/ tests/m2/ tests/m2_1/ tests/m3/ tests/m4/ tests/m5/ tests/m5_1/ -v
```

- **Total Test Count:** **104 tests**
- **Test Execution Status:** **104 PASSED, 0 FAILED, 0 SKIPPED**
- **Execution Wall Clock:** **9.87 seconds**
- **Coverage Domains:**
  - ODE dynamical simulators & SINDy recovery (M1)
  - Symbolic expression grammar & genetic programming (M2)
  - Neural dynamics surrogates & beam search ablation (M2.1)
  - Weak-form 1D PDE simulators & WSINDy recovery (M3)
  - 2D coupled reaction–diffusion & Navier–Stokes vortex simulators (M4)
  - Closed-loop active controller, portfolio falsification, & $N_{\text{eff}}$ BIC (M5)
  - Corrected paired statistical metrics & held-out simulators (M5.1)

---

### 3. Step-by-Step Reproduction Guide

#### Step 1: Run Statistical Replication & Clustered Stress Tests
```bash
python experiments/m5_2/audit_statistics_and_clusters.py
```
- Reproduces exact paired contingency matrices ($b=9, c=1$ vs Fixed; $b=18, c=1$ vs Random).
- Recomputes exact binomial two-sided $p$-values and Holm multiplicity families.
- Fits clustered GEE models ($K=5$) and evaluates leave-one-system-out sensitivity.
- Outputs: `audit/m5_2/STATISTICAL_REPLICATION_AND_CLUSTERS.json`.

#### Step 2: Run Query-Efficiency & Cahn–Hilliard Forensics
```bash
python experiments/m5_2/run_query_and_cahn_forensics.py
```
- Evaluates query count distributions across all 500 episodes.
- Verifies the Query 2 stopping invariant ($\text{Mean}=2.00, \sigma=0.00$ on successes).
- Fits weak-form regression on 1D Cahn–Hilliard at $\lambda = 0.045$ and $\lambda = 0.001$.
- Outputs: `audit/m5_2/FORENSIC_QUERY_AND_CH.json`.

#### Step 3: Run Mechanism Ablations & BIC Calibration
```bash
python experiments/m5_2/run_ablations.py
```
- Computes spatial-temporal autocorrelation length ratios and $N_{\text{eff}}$ scaling.
- Evaluates 5-way primary strategy ablations and 7-way held-out benchmark parity.
- Outputs: `audit/m5_2/ABLATIONS_AND_BIC.json`.

#### Step 4: Regenerate Publication Figures
```bash
python paper/scripts/generate_figures.py
```
- Re-generates publication-grade PDF and PNG vector graphics in `paper/figures/`:
  - `figure1_schematic.pdf` / `.png`
  - `figure2_recovery_curves.pdf` / `.png`
  - `figure3_paired_differences.pdf` / `.png`
  - `figure4_pareto_fronts.pdf` / `.png`

#### Step 5: Compile Research Manuscript
```bash
pdflatex -interaction=nonstopmode paper/main.tex
bibtex paper/main
pdflatex -interaction=nonstopmode paper/main.tex
pdflatex -interaction=nonstopmode paper/main.tex
```
- Compiles the revised 6-page research manuscript to `paper/main.pdf`.

---

### 4. Cryptographic Checksums of Core Artifacts

| Artifact Path | Format | Description | SHA-256 Checksum |
| :--- | :---: | :--- | :--- |
| `audit/m5/RAW_EPISODES.csv` | CSV | Raw 500 primary episode outcomes | `b6e147b1c312788e0b62e499d123e42152dc3625f9b4c023d8cba47721516db8` |
| `audit/m5_1/CORRECTED_PAIRED_OUTCOMES.csv` | CSV | 100 matched scenario paired table | `e46bfb7d94cf21d2a138bb612e4c02919318b76dfc63e264585e135546da1b98` |
| `audit/m5_1/HELD_OUT_BENCHMARKS.csv` | CSV | 280 held-out episode outcomes | `71b262d1d07b466183a652a8df80a7862f92f23cf9e3d81bcaeb8364e663a8be` |
| `paper/main.tex` | LaTeX | Revised publication-ready manuscript | Tracked in Git commit |
| `paper/main_m5_1_original.tex` | LaTeX | Frozen pre-revision manuscript baseline | Tracked in Git commit |
