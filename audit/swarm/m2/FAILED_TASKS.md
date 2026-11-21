# NOMOS Milestone M2 — Failed Tasks, Encountered Anomalies & Resolutions

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Auditing Specialists:** Agents G01, G08, H07, J03  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  

---

## 1. Encountered Technical Anomalies & Resolutions

### Anomaly 01: Dual OpenMP Runtime Conflict on Windows (`libiomp5md.dll`)
- **Encountered In:** PyTorch CPU import alongside NumPy/SciPy MKL.
- **Error:** `OMP: Error #15: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized.`
- **Root Cause:** Anaconda environment links both PyTorch's OpenMP runtime and Intel MKL's OpenMP runtime simultaneously.
- **Resolution:**
  1. Configured `os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"` at top of `nomos/__init__.py`, `nomos/neural/surrogate.py`, and `nomos/pipeline/m2_pipeline.py`.
  2. Restricted BLAS and OpenMP threads to single-threaded mode (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`) to prevent core thrashing.

### Anomaly 02: Pareto Dominance Collision in Multiple Plausible Laws Test
- **Encountered In:** `tests/m2/test_identifiability.py::test_multiple_plausible_laws_detector`.
- **Error:** `AssertionError: assert 'UNIQUE_LAW' == 'MULTIPLE_PLAUSIBLE_LAWS'`.
- **Root Cause:** In the test setup, candidate $T_1$ had MSE=0.010, complexity=2.0; candidate $T_2$ had MSE=0.0102, complexity=4.0. Because $T_1$ had both lower MSE and lower complexity, it strictly dominated $T_2$, causing $T_2$ to be pruned from the `ParetoFrontier` before reaching `audit_identifiability()`.
- **Resolution:** Adjusted candidate metrics to be mutually non-dominating ($T_1$: MSE=0.0102, complexity=2.0; $T_2$: MSE=0.0100, complexity=4.0). Both were admitted to the Pareto frontier, correctly triggering `MULTIPLE_PLAUSIBLE_LAWS`.

### Anomaly 03: Insufficient Gradient Steps in Fast Neural Guidance Unit Test
- **Encountered In:** `tests/m2/test_neural.py::test_neural_guidance_nonlinearity_detection`.
- **Error:** `AssertionError: Failed to detect periodic nonlinearity`.
- **Root Cause:** The unit test trained on 100 points with batch size 64 for 40 epochs at learning rate 0.001. With only ~40 total gradient steps, the MLP only learned the linear trend, yielding residual ratio 0.005 (below the 0.08 nonlinearity threshold).
- **Resolution:** Increased learning rate to 0.02, reduced batch size to 16, and trained for 100 epochs with patience 25. The network achieved $R^2 = 0.9999$ and residual ratio 0.402, reliably detecting the periodic nonlinearity.

### Anomaly 04: SINDy Equation String Attribute Mismatch
- **Encountered In:** `experiments/m2/run_m2_benchmarks.py`.
- **Error:** `AttributeError: 'DiscoveredEquation' object has no attribute 'expression_str'`.
- **Root Cause:** M1's `DiscoveredEquation` dataclass stores equation strings in `.raw_str` and `str(.sympy_expr)`, not `.expression_str`.
- **Resolution:** Updated benchmark logger to access `.raw_str`.

### Anomaly 05: Unary Operator Amplitude Scaling in Beam Search
- **Encountered In:** `nomos/search/beam.py` on nonlinear pendulum.
- **Error:** Beam search selected linear term $-8.125 \theta$ instead of $-9.81 \sin(\theta)$.
- **Root Cause:** Beam expansion generated $\sin(\theta)$ with implicit coefficient $1.0$. Because $\sin(\theta)$ has loss $\sim 77$ compared to $9.81 \sin(\theta)$, it was pruned before constant optimization.
- **Resolution:** Updated unary grammar expansion to generate both $u(T)$ and scaled $c \cdot u(T)$, allowing continuous parameter optimization to fit amplitude coefficients.
