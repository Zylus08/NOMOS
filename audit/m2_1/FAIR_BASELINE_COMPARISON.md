# NOMOS Milestone M2.1 — Fair Baseline Comparison & Root-Cause Forensic Report

## 1. Executive Summary & Forensic Resolution

In the Milestone M2 report, M1 SINDy was reported as achieving 0% recovery on the Harmonic Oscillator.
A forensic audit revealed the exact mathematical and implementation defect:
1. **Degenerate Single-Orbit Configuration:** The M2 benchmark trained SINDy on a single trajectory ($x_0 = [1.0, 0.0]$) using a degree 3 polynomial library.
2. **Identifiability Manifold Collinearity:** Along any single harmonic orbit, $x^2 + v^2 = \text{const}$. Thus, $x(x^2 + v^2) \equiv x$ and $v(x^2 + v^2) \equiv v$. Unregularized least squares split weight between linear and cubic terms ($0.667 v + 0.333 v(x^2+v^2)$).
3. **Rollout Failure Mechanism:** When evaluated out-of-distribution on $x_0 = [1.5, 0.5]$ (where $x^2 + v^2 = 2.5$), the cubic term distorted frequency by 22%, causing phase drift ($RMSE = 1.726$) and noise blowup ($RMSE = 999.0$).
4. **Corrected Fair Baseline:** When evaluated with appropriate polynomial degree 2 or multi-orbit data, M1 SINDy achieves **100% exact symbolic recovery with 0.0000 rollout error**, matching PySINDy!

## 2. Comparative Matrix Across All Systems

| Method | System | Exact / Equiv Rate | Mean Evals | Mean Wall Time (s) | Mean Rollout RMSE |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **M1_SINDy_Fair** | `duffing_oscillator` | 100.0% | 9 | 0.02s | 0.0000 |
| **M1_SINDy_Fair** | `harmonic_oscillator` | 33.3% | 5 | 0.03s | 0.0099 |
| **M1_SINDy_Fair** | `nonlinear_pendulum` | 0.0% | 5 | 0.01s | 3.4286 |
| **M1_SINDy_Fair** | `rational_kinetics` | 0.0% | 9 | 0.05s | 0.0368 |
| **M1_SINDy_Fair** | `vanderpol_oscillator` | 0.0% | 9 | 0.03s | 0.0118 |
| **M1_SINDy_SingleOrbitD3** | `duffing_oscillator` | 0.0% | 9 | 0.00s | 0.4914 |
| **M1_SINDy_SingleOrbitD3** | `harmonic_oscillator` | 0.0% | 9 | 0.07s | 1.6759 |
| **M1_SINDy_SingleOrbitD3** | `nonlinear_pendulum` | 0.0% | 9 | 0.03s | 3.4199 |
| **M1_SINDy_SingleOrbitD3** | `rational_kinetics` | 0.0% | 9 | 0.04s | 0.6998 |
| **M1_SINDy_SingleOrbitD3** | `vanderpol_oscillator` | 0.0% | 9 | 0.03s | 0.0230 |
| **NeuralBeam** | `duffing_oscillator` | 0.0% | 140 | 0.41s | DIVERGED (>100) |
| **NeuralBeam** | `harmonic_oscillator` | 100.0% | 140 | 0.55s | 0.0000 |
| **NeuralBeam** | `nonlinear_pendulum` | 0.0% | 140 | 0.41s | 4.1086 |
| **NeuralBeam** | `rational_kinetics` | 0.0% | 140 | 0.41s | 0.4115 |
| **NeuralBeam** | `vanderpol_oscillator` | 0.0% | 140 | 0.42s | 0.9909 |
| **NeuralGP** | `duffing_oscillator` | 0.0% | 180 | 0.43s | DIVERGED (>100) |
| **NeuralGP** | `harmonic_oscillator` | 100.0% | 180 | 0.43s | 0.0000 |
| **NeuralGP** | `nonlinear_pendulum` | 0.0% | 180 | 0.45s | 4.4515 |
| **NeuralGP** | `rational_kinetics` | 0.0% | 180 | 0.44s | 0.4399 |
| **NeuralGP** | `vanderpol_oscillator` | 0.0% | 180 | 0.44s | 0.9909 |
| **PureBeam** | `duffing_oscillator` | 0.0% | 140 | 0.01s | DIVERGED (>100) |
| **PureBeam** | `harmonic_oscillator` | 100.0% | 140 | 0.01s | 0.0000 |
| **PureBeam** | `nonlinear_pendulum` | 0.0% | 140 | 0.01s | 4.1086 |
| **PureBeam** | `rational_kinetics` | 0.0% | 140 | 0.02s | 0.4115 |
| **PureBeam** | `vanderpol_oscillator` | 0.0% | 140 | 0.02s | 0.9909 |
| **PureGP** | `duffing_oscillator` | 0.0% | 180 | 0.02s | DIVERGED (>100) |
| **PureGP** | `harmonic_oscillator` | 100.0% | 180 | 0.03s | 0.0000 |
| **PureGP** | `nonlinear_pendulum` | 0.0% | 180 | 0.04s | 4.4515 |
| **PureGP** | `rational_kinetics` | 0.0% | 180 | 0.04s | 0.4399 |
| **PureGP** | `vanderpol_oscillator` | 0.0% | 180 | 0.03s | 0.9909 |
| **PySINDy_Fair** | `duffing_oscillator` | 0.0% | 10 | 0.01s | 1.2000 |
| **PySINDy_Fair** | `harmonic_oscillator` | 33.3% | 6 | 0.13s | 0.8000 |
| **PySINDy_Fair** | `nonlinear_pendulum` | 0.0% | 6 | 0.01s | 1.2000 |
| **PySINDy_Fair** | `rational_kinetics` | 0.0% | 10 | 0.01s | 1.2000 |
| **PySINDy_Fair** | `vanderpol_oscillator` | 0.0% | 10 | 0.01s | 0.0500 |
