# Project NOMOS — Milestone M5
## Persistent Scientific Hypothesis Portfolio & Memory Engine

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M5 Phase 2 Specification  
**Date:** 2026-11-24  

---

### 1. Scientific Memory Design Principles

In human scientific discovery, falsified theories (e.g., caloric theory of heat, luminiferous aether) are not deleted from historical records; their contradiction is documented to prevent recurring false discoveries.
`HypothesisPortfolio` (`nomos/closed_loop/portfolio.py`) enforces:
1. **Immutability & Lineage Tracking:** Hypotheses are never silently overwritten. Revisions increment version numbers and append lineage notes.
2. **Explicit Contradiction Ledger:** Hypotheses record every experiment that supported or contradicted their predictions (`supporting_experiments`, `contradicting_experiments`).
3. **Revisitation:** Hypotheses marked `SUSPENDED` can be re-evaluated if new data invalidates the premises of their initial rejection.

---

### 2. Data Structure Schema (`ScientificHypothesis`)

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Unique hypothesis identifier (e.g. `hyp_wsindy_kdv_equation`). |
| `equation_str` | `str` | Human- and machine-readable canonical expression. |
| `features` | `List[str]` | Differential features present in the law. |
| `parameters` | `Dict[str, float]` | Continuous physical parameter estimates. |
| `complexity` | `int` | AST node count or structural complexity metric. |
| `origin` | `str` | Originating engine (`wsindy`, `beam_search`, `prior`). |
| `train_mse` / `val_mse` | `float` | In-sample fit and out-of-sample predictive residual. |
| `bic` | `float` | Bayesian Information Criterion: $N \ln(\text{MSE}) + K \ln(N)$. |
| `evidence_score` | `float` | Normalized posterior evidence probability $\in [0, 1]$. |
| `supporting_count` | `int` | Count of confirming experimental episodes. |
| `contradicting_count` | `int` | Count of contradicting experimental episodes. |
| `status` | `Enum` | `ACTIVE`, `SUPPORTED`, `FALSIFIED`, `SUSPENDED`. |
| `rejection_reason` | `Optional[str]` | Physical or statistical justification for falsification. |
| `version` | `int` | Version counter preserving historical revisions. |
