# Project NOMOS — Milestone M5.3
# Manuscript Revision & Peer Review Reconciliation

**Date:** 2026-11-25  
**Manuscript:** [`paper/main.tex`](file:///e:/NOMOS/paper/main.tex) $\to$ [`paper/main.pdf`](file:///e:/NOMOS/paper/main.pdf) (6 pages)  
**Author & Git Identity:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditors:** Reviewer Groups B & E

---

## 1. Summary of Manuscript Revisions

In response to the pre-submission adversarial review in Milestone M5.2 and the M5.3 zero-leakage replication benchmarks, the six-page manuscript was completely updated and recompiled.

| Section | Baseline Content (M5.1 / M5.2) | Revised Content (M5.3 Zero-Leakage) | Rationale & Reviewer Alignment |
| :--- | :--- | :--- | :--- |
| **Abstract** | Conflated support recovery (+8.0%) with exact Tier 1 recovery; cited K=5 GEE odds ratio ($1.51$). | Replaced with certified Tier 1 exact parametric recovery: **Active 45.0% vs Fixed 29.0% ($+16.00\%, p = 1.45 \times 10^{-4}$)**. Transparently disclosed Active vs Random parity ($45.0\%$ vs $39.0\%, p = 0.146$). Retracted Query 2 invariant. | Complies with Reviewer Group B & E requirements to anchor confirmatory inference on exact finite-sample tests. |
| **Section 1 (Introduction)** | Claimed unassisted autonomous discovery without noting impostor initialization. | Explicitly defines the Blind Discovery Contract: system identities scrubbed, hypotheses generated autonomously via multi-threshold WSINDy + parsimonious sub-models. | Eliminates hidden information flow; aligns text with zero-leakage code implementation. |
| **Section 4.1 & 4.2 (Methodology)** | Evaluated minimal candidate bases (e.g. 3 true terms for Gray-Scott). | Evaluates **overcomplete dictionaries containing distractor terms** for all 5 primary systems and 2 held-out systems. | Demonstrates true operator selection and dictionary sparsity under Category B Blind Identification. |
| **Table 1 (`tab:paired_stats`)** | Old numbers from leaked impostor run ($13\%$ vs $21\%$). | **Certified zero-leakage paired contingency statistics**: Active vs Fixed: $+16.00\%$ ($p = 1.45 \times 10^{-4}$, 95\% CI: $[+8.3\%, +23.7\%]$); Active vs Random: $+6.00\%$ ($p = 0.146$, 95\% CI: $[-0.7\%, +12.7\%]$). | 100% matched pair verification by independent statistical reviewer. |
| **Section 5.1 (Paired Testing)** | Claimed KdV was 55% of discordant wins; questioned generalizability. | Documents KdV gain ($60\%$ vs $0\%$), Navier-Stokes gain ($75\%$ vs $60\%$), Burgers ($35\%$ vs $30\%$). Discloses lack of net losses across all systems ($c \le 1$). | Confirms active advantage is structurally genuine across multiple physical regimes. |
| **Section 5.2 (Small-Pool Theory)** | Claimed active should vastly outperform random. | Formulates **combinatorial hit rate in finite candidate pools**: in 5-item pools, 4 random draws select separating perturbations with 87.0% probability. Active provides step-1 determinism and a 21.6% reduction in false discoveries. | Theoretical reconciliation of why Random performs competitively in small discrete pools. |
| **Section 5.3 (False Identification)** | False identification was $35.1\%$ vs $43.9\%$. | Certified false identification rates: Active 29.0\%, Cost-Normalized 25.0\%, Random 37.0\%, Fixed 46.0\%. Active reduces false discovery by $37.0\%$. | Demonstrates clear practical safety advantage of active exploration. |
| **Section 5.4 (Query Dynamics)** | Claimed "identically 2.000 queries" was a universal law invariant. | **Formally retracted the Query 2 invariant**. Disclosed empirical distribution ($2.70 \pm 1.25$ queries: Query 2 in 73\%, Query 3 in 5\%, Query 4 in 1\%, Query 5 in 21\%). | Fully resolves M5.2 red-team finding that Query 2 was an impostor seeding artifact. |
| **Section 5.5 (Held-Out Benchmarks)** | Brusselator 50% recovery claimed on unreactive states. | Evaluated Brusselator with distractor terms: isolated core terms but parameter error and distractor retention yielded Tier 6. Cahn-Hilliard failed Tier 1 due to 4th-order biharmonic stiffness. | Completely candid reporting of held-out boundary limitations. |
| **Section 6 (Failure Modes)** | Noted "Pre-Seeded Impostors" as open defect. | Updated to record that **M5.3 eradicated impostor seeding and implemented autonomous parsimonious generation**. | Documents the milestone resolution. |

---

## 2. Compilation Verification

Compilation command executed:
```powershell
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```
Output:
- Format: Two-column, A4 paper, standard 10pt article class.
- Page Count: Exactly 6 pages (440,546 bytes).
- PDF file: [`paper/main.pdf`](file:///e:/NOMOS/paper/main.pdf)
- Zero syntax errors, zero missing references, zero overflow pages.
