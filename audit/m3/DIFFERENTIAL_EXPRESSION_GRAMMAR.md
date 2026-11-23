# Project NOMOS — Milestone M3
## Open-Ended Differential Expression Grammar & AST Specification

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** E01–E05 (Differential AST Grammar)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Grammar Design & Node Types

The differential AST extends discrete symbolic regression to continuous spatiotemporal fields:
- **Terminals:** `FIELD_VAR` ($u$), `CONSTANT` ($c$).
- **Spatial Differential Primitives:** `DIFF_X` ($\partial/\partial x$), `DIFF_XX` ($\partial^2/\partial x^2$), `DIFF_XXX` ($\partial^3/\partial x^3$), `DIFF_XXXX` ($\partial^4/\partial x^4$).
- **Algebraic Primitives:** `ADD`, `SUB`, `MUL`, `NEG`, `POW`.

### 2. Semantic Differentiation & SymPy Equivalence

The grammar strictly distinguishes:
- $rac{\partial(u^2)}{\partial x}$ vs $u rac{\partial u}{\partial x}$ vs $2 u rac{\partial u}{\partial x}$.
- $rac{\partial^2 u}{\partial x^2}$ vs $\left(rac{\partial u}{\partial x}ight)^2$.

Using SymPy reduction, the evaluator proves:
$$rac{\partial(u^2)}{\partial x} \equiv 2 u rac{\partial u}{\partial x}$$
allowing open-ended search to discover advective fluxes in conservative divergence form ($\partial_x(u^2)$) or non-conservative advective form ($u u_x$) interchangeably.
