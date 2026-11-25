# PROJECT NOMOS — MILESTONE M5.3.1 AUDIT REPORT
## Deliverable 9: Manuscript Claims & Empirical Artifact Synchronization Audit

**Date:** 2026-11-25  
**Auditor:** Independent Scientific Audit Commission & Editorial Verification Group  
**Target Document:** `paper/main.tex` and compiled `paper/main.pdf`  
**Authoritative Data Sources:** `audit/m5_3_1/CORRECTED_EPISODES.csv`, `CORRECTED_PAIRED_OUTCOMES.csv`, `ORACLE_CALL_LEDGER.csv`  

---

### Executive Summary

This audit performed an exhaustive, line-by-line verification of the research manuscript (`paper/main.tex`) against the raw empirical artifacts generated under the reconciled $B \le 4$ hard budget and SHA-256 blinding protocol. 

All overbroad claims, non-cryptographic terminology, and unverified heuristics have been corrected. The manuscript has been successfully recompiled into `paper/main.pdf` (7 pages, 451,027 bytes, 0 errors).

---

### 1. Mandatory Claim Language Standardization

Under Gate F directives, all references to the primary confirmatory discovery result have been standardized to the exact required language:

> *"Disagreement-guided active acquisition improved strict governing-law recovery relative to the tested sequential fixed schedule under specified blinded simulation benchmarks."*

This exact phrasing is now anchored in:
- Abstract (lines 29–31)
- Section 5.1 (Results: Certified Paired Statistical Testing, line 204)
- Section 7 (Conclusion, line 248)

---

### 2. Numerical Synchronization & Empirical Lineage Audit

Every numerical figure appearing in the text, tables, and abstract of `paper/main.tex` was verified against `CORRECTED_EPISODES.csv` and `CORRECTED_PAIRED_OUTCOMES.csv`:

| Manuscript Section / Item | Claimed Value in Text | Raw Data in `CORRECTED_EPISODES.csv` | Exact Verification | Audit Status |
|:---|:---:|:---:|:---:|:---:|
| **Sample Size (Primary)** | 100 matched scenario trials, 400 episodes | 100 matched quadruplets ($5 \times 4 \times 5 \times 4 = 400$) | Exactly 400 rows (`benchmark_type == PRIMARY`) | **VERIFIED** |
| **Sample Size (Held-out)** | 80 held-out replication episodes | 80 episodes ($2 \times 4 \times 5 \times 2 = 80$) | Exactly 80 rows (`benchmark_type == HELD_OUT`) | **VERIFIED** |
| **Total Benchmark Matrix** | 480 total episodes | 480 episodes total | Exactly 480 rows in `CORRECTED_EPISODES.csv` | **VERIFIED** |
| **Active Recovery Rate** | 45.0% (45 / 100) | 45 Tier 1 recoveries out of 100 episodes | 45 / 100 (`strategy == greedy_disagreement`) | **VERIFIED** |
| **Fixed Schedule Recovery Rate** | 29.0% (29 / 100) | 29 Tier 1 recoveries out of 100 episodes | 29 / 100 (`strategy == fixed`) | **VERIFIED** |
| **Random Baseline Recovery Rate** | 39.0% (39 / 100) | 39 Tier 1 recoveries out of 100 episodes | 39 / 100 (`strategy == random`) | **VERIFIED** |
| **Cost-Normalized Recovery Rate** | 45.0% (45 / 100) | 45 Tier 1 recoveries out of 100 episodes | 45 / 100 (`strategy == cost_normalized`) | **VERIFIED** |
| **Paired Gain (Active vs. Fixed)** | +16.00 percentage points | $\hat{d} = (17 - 1) / 100 = +0.1600$ | $n_{10}=17, n_{01}=1, n_{11}=28, n_{00}=54$ | **VERIFIED** |
| **Exact McNemar $p$ (Active vs. Fixed)** | $1.45 \times 10^{-4}$ | $p = 19 / 131072 = 0.00014495849609375$ | Machine precision binomial tail ($b=17, c=1$) | **VERIFIED** |
| **Holm-Adjusted $p$ (Active vs. Fixed)** | $2.90 \times 10^{-4}$ ($p < 0.001$) | $2 \times 1.44958 \times 10^{-4} = 2.89917 \times 10^{-4}$ | Step-down Holm multiplicity adjustment | **VERIFIED** |
| **Newcombe 95% CI (Active vs. Fixed)** | $[+8.3\%, +23.7\%]$ | Method 10 paired score interval | Strictly excludes zero | **VERIFIED** |
| **Paired Gain (Active vs. Random)** | +6.00 percentage points | $\hat{d} = (9 - 3) / 100 = +0.0600$ | $n_{10}=9, n_{01}=3, n_{11}=36, n_{00}=52$ | **VERIFIED** |
| **Exact McNemar $p$ (Active vs. Random)** | $0.1460$ | $p = 299 / 2048 = 0.14599609375$ | Machine precision binomial tail ($b=9, c=3$) | **VERIFIED** |
| **Newcombe 95% CI (Active vs. Random)** | $[-2.2\%, +14.0\%]$ | Method 10 paired score interval | Spans zero; confirms non-significance | **VERIFIED** |
| **Active Query Distribution** | Query 2: 73%; Query 3: 5%; Query 4: 22% | Query 2: 73; Query 3: 5; Query 4: 22 | Mean queries: $2.49 \pm 0.83$; Query 5: 0 | **VERIFIED** |
| **Maximum Trajectory Budget** | Strictly $B \le 4$ queries | Max queries in ledger = 4 | 0 queries beyond budget in 1256 calls | **VERIFIED** |

---

### 3. Terminology & Blinding Claims Audit

1. **Purging of "Cryptographic Scrubbing":**
   All claims that system identities or equations were "cryptographically scrubbed" have been purged from the manuscript. The text now accurately describes the mechanism:
   *"...operating under a verified zero-leakage Blind Discovery Contract where system observations are sanitized via deterministic SHA-256 tensor digest isolation and an explicit attribute allowlist..."*

2. **Dismantling of the "Universal 87%" Heuristic:**
   The manuscript no longer claims that 87% applies universally across all physical systems. Section 5.2 explicitly details the system-by-system combinatorics under $M = 3$ adaptive queries:
   - KdV: $78.40\%$ ($K=5, K_{\text{info}}=2$)
   - Burgers: $87.50\%$ ($K=4, K_{\text{info}}=2$)
   - Gray-Scott, FitzHugh-Nagumo, Navier-Stokes: $96.30\%$ ($K=3, K_{\text{info}}=2$)
   - Cross-system mean theoretical probability: $90.96\%$.

3. **Explicit Non-Significance Against Random:**
   The manuscript emphasizes in the Abstract, Section 5.1, and Conclusion that active acquisition is **not statistically significantly different from uniform random acquisition** ($p = 0.146$).

---

### 4. Compilation Verification

The manuscript was compiled using pdfTeX (TeX Live 2026):
```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```
- **Exit Code:** `0` (Success)
- **Output Artifact:** `paper/main.pdf`
- **Page Count:** 7 pages
- **File Size:** 451,027 bytes
- **Diagnostic Log:** 0 fatal errors, 0 undefined citations, all cross-references resolved.
