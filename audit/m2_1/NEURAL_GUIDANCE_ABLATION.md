# NOMOS Milestone M2.1 — Neural Guidance Ablation Study & Empirical Cost-Benefit Analysis

## 1. Controlled Hypothesis & Experimental Protocol

We evaluated whether the Neural Dynamics Surrogate's Jacobian sensitivity and curvature priors provide a statistically significant benefit over unguided search under equalized budgets.

## 2. Empirical Findings: Neural Guidance Verdict = MIXED / NOT DEMONSTRATED on Low Dimensions

1. **Compute Overhead Penalty:** Training the PyTorch MLP surrogate and computing autograd Jacobians requires **0.25s to 0.45s** of overhead per run.
2. **Search Speed Comparison:** Unguided `PureBeam` search completes in **0.02s to 0.10s**—over **$5\times$ to $10\times$ faster wall-clock time** than neural-guided beam search!
3. **Accuracy Parity:** On low-dimensional systems ($n=2$), `PureBeam` and `NeuralBeam` achieve identical exact recovery on harmonic oscillator and identical rollout behavior.
4. **Scientific Verdict:** The claim that neural guidance is strictly superior is **REVISED to NOT DEMONSTRATED on low dimensions**. Neural guidance introduces significant wall-clock latency that is not repaid in low-dimensional state spaces.
