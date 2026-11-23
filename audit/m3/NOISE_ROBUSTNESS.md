# Project NOMOS — Milestone M3
## Noise Robustness & Error Propagation Analysis

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** C01 (Noise Audit)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### Noise Degradation Analysis

Evaluated under relative Gaussian measurement noise $\eta \in [0\%, 1\%, 5\%, 10\%]$:
- **Strong-form methods** experience noise amplification proportional to $(1/\Delta x)^m$ for derivative order $m$. At 4th order, noise amplification factor exceeds $10^5$, completely corrupting Strong SINDy.
- **Weak-form integral methods (WSINDy)** transfer derivatives onto smooth test functions, providing natural $L_2$ smoothing. WSINDy maintains exact support recovery on Burgers up to 10% noise.
