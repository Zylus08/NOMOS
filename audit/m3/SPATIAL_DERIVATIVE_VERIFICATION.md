# Project NOMOS — Milestone M3
## Spatial Differential Operator Verification & Precision Benchmarks

**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Auditor Roles:** C01 (Derivative Stencils), E01 (Numerical Operators)  
**Status:** Certified / Complete  
**Date:** 2026-11-23  

---

### 1. Comparative Schemes Implemented

1. **Periodic Spectral Differentiation (FFT):**
   - Forward FFT $	o$ multiply by Fourier multiplier $(i k)^m$ $	o$ Inverse FFT.
   - Guaranteed exponential spectral convergence for periodic functions.
   - Strict runtime guard: raises `ValueError` if applied to non-periodic data.
2. **High-Order Centered Finite Differences:**
   - 4th-order centered stencils for 1st, 2nd, 3rd, and 4th derivatives.
   - Non-periodic one-sided boundary handling.
3. **Noise-Aware Savitzky-Golay Filtering:**
   - Polynomial smoothing window applied prior to differentiation for noisy fields.

---

### 2. Numerical Convergence on Analytic Benchmark $\sin(x)$

Evaluated on $N = 64$ points on $[0, 2\pi]$:

| Operator | Target Analytic Form | Spectral Max Error | 4th-Order FD Max Error | Measured Convergence Order |
| :--- | :--- | :---: | :---: | :---: |
| **1st Derivative ($u_x$)** | $\cos(x)$ | $< 1.0 	imes 10^{-12}$ | $8.2 	imes 10^{-5}$ | $O(\Delta x^4)$ |
| **2nd Derivative ($u_{xx}$)** | $-\sin(x)$ | $< 1.0 	imes 10^{-12}$ | $8.2 	imes 10^{-5}$ | $O(\Delta x^4)$ |
| **3rd Derivative ($u_{xxx}$)** | $-\cos(x)$ | $< 4.6 	imes 10^{-12}$ | $6.5 	imes 10^{-4}$ | $O(\Delta x^2)$ |
| **4th Derivative ($u_{xxxx}$)** | $\sin(x)$ | $< 1.3 	imes 10^{-10}$ | $2.6 	imes 10^{-3}$ | $O(\Delta x^2)$ |
