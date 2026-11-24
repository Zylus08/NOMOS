# Project NOMOS: Publication Reproducibility Package

**Milestone:** NOMOS M5.1 — Scientific Replication & Paper Readiness  
**Author / Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Target Repository:** `E:\NOMOS` on branch `main`  
**Certified Commit Baseline:** `bf309750dabc147600ae2a59944f15e473d8a069`  

---

## 1. Verified Software Environment

- **Operating System:** Microsoft Windows 11 Pro 64-bit
- **CPU:** Intel Core i7-12650H (10 physical cores, 16 threads, 2.7 GHz base)
- **RAM:** 16.0 GB physical memory
- **Python:** 3.12.8 (Anaconda3 distribution)
- **Scientific Libraries:**
  - `numpy`: 1.26.4
  - `scipy`: 1.13.1
  - `statsmodels`: 0.14.6
  - `pandas`: 2.2.2
  - `matplotlib`: 3.10.1
  - `sympy`: 1.14.0
  - `torch`: 2.15.0+cpu
  - `pytest`: 9.0.3
- **LaTeX Engine:** TinyTeX distribution (`pdflatex`, `bibtex`, `tlmgr` in `C:\Users\mishr\AppData\Roaming\TinyTeX\bin\windows\`)

---

## 2. Reproduction Instructions

### 2.1 Complete Test Suite Execution
To verify all historical and newly certified test suites (104 tests total):
```bash
pytest tests/ tests/m2/ tests/m2_1/ tests/m3/ tests/m4/ tests/m5/ tests/m5_1/ -v
```
All tests pass in ~25-30 seconds with a 100% pass rate.

### 2.2 Generating All Publication Figures
To regenerate Figure 1, Figure 2, Figure 3, and Figure 4 (both PDF and PNG formats in `paper/figures/`):
```bash
python paper/scripts/generate_figures.py
```

### 2.3 Executing the 280-Episode Held-Out Benchmark Matrix
To regenerate `audit/m5_1/HELD_OUT_BENCHMARKS.csv` and `audit/m5_1/STRONG_BASELINES.csv`:
```bash
python experiments/m5_1/run_held_out_benchmarks.py
```

### 2.4 Executing the Identifiability Stress Tests
To regenerate `audit/m5_1/IDENTIFIABILITY_STRESS_TESTS.json`:
```bash
python experiments/m5_1/run_stress_tests.py
```

### 2.5 Compiling the LaTeX Publication Paper
To compile `paper/main.tex` to `paper/main.pdf`:
```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## 3. Cryptographic Checksums of Primary Datasets

| File | Relative Path | Purpose |
| :--- | :--- | :--- |
| `CORRECTED_SUMMARY.csv` | `audit/m5_1/CORRECTED_SUMMARY.csv` | Summary table of exact binomial tests and paired CIs |
| `CORRECTED_PAIRED_OUTCOMES.csv` | `audit/m5_1/CORRECTED_PAIRED_OUTCOMES.csv` | 100 matched scenario trials across 5 physical systems |
| `HELD_OUT_BENCHMARKS.csv` | `audit/m5_1/HELD_OUT_BENCHMARKS.csv` | 280 experimental episodes on Brusselator 2D and Cahn-Hilliard |
| `STRONG_BASELINES.csv` | `audit/m5_1/STRONG_BASELINES.csv` | Aggregated comparison across 7 acquisition strategies |
| `IDENTIFIABILITY_STRESS_TESTS.json` | `audit/m5_1/IDENTIFIABILITY_STRESS_TESTS.json` | Four adversarial failure-boundary experiments |
