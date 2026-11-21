# NOMOS Milestone M2 — Structured Enumeration & Beam Search Engine

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Search Specialists:** Agents D03, D05, D12, D14  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Module:** `nomos/search/beam.py`  

---

## 1. Algorithmic Architecture

The NOMOS M2 `StructuredBeamSearch` engine provides a rigorous, deterministic alternative to stochastic genetic programming. It explores candidate expression space level-by-level across tree depth using grammar-guided expansion, strict algebraic deduplication, and continuous parameter optimization.

### 1.1 Search Process
```
Depth 1 (Terminals):
  - Constants: {1.0, -1.0, 0.5}
  - Variables: {x_1, ..., x_n}
  - Scaled Variables: {c * x_1, ..., c * x_n}

Depth d -> d + 1 (Grammar Expansion):
  - Unary Expansion: uop(T), c * uop(T) for T in Beam
  - Binary Expansion: bop(T_1, T_2) for T_1, T_2 in Beam
  - Deduplication: Canonical string and SymPy equivalence hashing
  - Pruning: Domain safety and invalidity checks
  - Scoring: Multi-objective score = MSE + lambda * Complexity
  - Selection: Retain top-K beam candidates
  - Pareto Update: Optimize continuous constants on top candidates via L-BFGS-B
```

---

## 2. Canonical Deduplication & Symmetry Pruning

In unconstrained tree enumeration, mathematically redundant expressions quickly overwhelm the beam width (e.g., $x + y \equiv y + x$, $x \times y \equiv y \times x$, $x - x \equiv 0$, $x / x \equiv 1$).

To maximize beam diversity within bounded memory, NOMOS M2 implements:
1. **Commutative Sorting:** For commutative operators (`ADD`, `MUL`), children are lexicographically ordered by their subtree string representations.
2. **Signature Hashing:** Each candidate expression is converted to a canonical prefix string signature; duplicates are pruned in $O(1)$ time before numerical evaluation.
3. **Neutral Operator Pruning:** Trivial identities ($0 + T$, $1 \times T$, $-(-T)$) are discarded at generation time.

---

## 3. Continuous Parameter Optimization Coupling

Continuous numerical constants in expression trees (e.g., the restoring constant in $-9.81 \sin(\theta)$ or damping coefficient $\gamma$) cannot be effectively discovered by discrete enumeration alone.

NOMOS M2 couples discrete structural beam search with continuous parameter optimization:
- On each beam depth, the top non-dominated candidates containing constant nodes are refit using SciPy's `L-BFGS-B` algorithm (`nomos/search/optimizer.py`).
- Objective function:
  $$\min_{\mathbf{c}} \frac{1}{M} \sum_{k=1}^M \left( y_k - f(x_k; \mathbf{c}) \right)^2$$
- Bounded gradients prevent runaway constants.
- The optimized tree replaces the unoptimized template in the global `ParetoFrontier`.
