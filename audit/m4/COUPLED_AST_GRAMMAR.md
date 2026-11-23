# Project NOMOS — Milestone M4
## Coupled 2D Differential AST Grammar & Canonical Equivalence Audit

**Author:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Repository:** `E:\NOMOS`  
**Milestone:** M4 Phase 6 Specification & Formal Verification  
**Date:** 2026-11-23  

---

### 1. Grammar Extension Specification

Milestone M4 extends the differential expression Abstract Syntax Tree (AST) grammar in `nomos/pde/grammar.py` from 1D scalar operators to coupled, multi-channel 2D spatial manifolds:

#### Terminal Nodes
- `FIELD_VAR`: Multi-channel named variables ($u, v, \omega, \psi$, etc.).
- `CONSTANT`: Scalar parameters ($\alpha, \nu, D_u, D_v$).

#### Spatial Differential Operators
- 1D/2D $x$-derivatives: `DIFF_X` ($\partial_x$), `DIFF_XX` ($\partial_{xx}$), `DIFF_XXX` ($\partial_{xxx}$), `DIFF_XXXX` ($\partial_{xxxx}$).
- 2D $y$-derivatives: `DIFF_Y` ($\partial_y$), `DIFF_YY` ($\partial_{yy}$).
- 2D Invariant Laplacian: `LAPLACIAN` ($\nabla^2 = \partial_{xx} + \partial_{yy}$).

#### Multi-Channel Algebraic Operators
- Additive/Subtractive: `ADD`, `SUB`, `NEG`.
- Multiplicative Coupling: `MUL` (e.g., $u v^2$, $\mathbf{u} \cdot \nabla \omega$).
- Nonlinear Powers: `POW` (e.g., $u^2, u^3$).

---

### 2. SymPy Canonical Equivalence (`check_differential_algebraic_equivalence`)

All differential AST nodes are convertible to formal SymPy objects (`to_sympy()`) enabling symbolic algebraic simplification:
$$\operatorname{simplify}\left( \operatorname{Expr}_1 - \operatorname{Expr}_2 \right) \equiv 0$$

#### Certified Equivalence Cases:
1. **Product Rule:** $\partial_x(u^2) \equiv 2 u \partial_x u$ (Verified True).
2. **2D Laplacian Decomposition:** $\operatorname{Laplacian}(u) \equiv \partial_{xx} u + \partial_{yy} u$ (Verified True).
3. **Cross-Channel Kinetic Products:** $u \cdot (v^2) \equiv (u \cdot v) \cdot v$ (Verified True).
4. **Commutative Linear Derivatives:** $\partial_{xy} u \equiv \partial_{yx} u$ for smooth fields (Verified True).
