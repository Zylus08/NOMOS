# Project NOMOS — Milestone M5
## Empirical Noise Robustness & Signal Degradation Analysis

**Principal Investigator / Git Identity:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Milestone:** M5 — Closed-Loop Autonomous Scientific Experimentation & Falsifiable Physical-Law Discovery  

---

### 1. Empirical Noise Evaluation Framework

Observation noise is a fundamental challenge in scientific discovery. Differentiating noisy spatio-temporal data amplifies high-frequency noise proportionally to $k^n$ where $n$ is the derivative order.

In Milestone M5, we evaluate noise robustness across 4 controlled noise levels:
$$\sigma \in \{0.00, 0.01, 0.05, 0.10\}$$
corresponding to $0\%$, $1\%$, $5\%$, and $10\%$ additive uncorrelated Gaussian noise $\mathcal{N}(0, \sigma^2 \cdot \text{Var}(u))$.

---

### 2. Empirical Results Across Noise Regimes

Aggregated across 25 independent trials per noise level (5 physical systems $\times$ 5 seeds):

| Strategy | Noise Level ($\sigma$) | Total Trials | Exact Recovery Rate | Mean Queries to Stop |
| :--- | :---: | :---: | :---: | :---: |
| **Active (`greedy_disagreement`)** | $0.00$ ($0\%$) | 25 | **84.0%** (21/25) | 2.00 |
| **Active (`greedy_disagreement`)** | $0.01$ ($1\%$) | 25 | **80.0%** (20/25) | 2.00 |
| **Active (`greedy_disagreement`)** | $0.05$ ($5\%$) | 25 | **56.0%** (14/25) | 2.00 |
| **Active (`greedy_disagreement`)** | $0.10$ ($10\%$) | 25 | **32.0%** (8/25) | 2.40 |
| **Active (`cost_normalized`)** | $0.00$ ($0\%$) | 25 | **84.0%** (21/25) | 2.00 |
| **Active (`cost_normalized`)** | $0.01$ ($1\%$) | 25 | **80.0%** (20/25) | 2.00 |
| **Active (`cost_normalized`)** | $0.05$ ($5\%$) | 25 | **56.0%** (14/25) | 2.00 |
| **Active (`cost_normalized`)** | $0.10$ ($10\%$) | 25 | **24.0%** (6/25) | 2.28 |
| **Passive (`fixed` schedule)** | $0.00$ ($0\%$) | 25 | 84.0% (21/25) | 2.80 |
| **Passive (`fixed` schedule)** | $0.01$ ($1\%$) | 25 | 64.0% (16/25) | 2.08 |
| **Passive (`fixed` schedule)** | $0.05$ ($5\%$) | 25 | 52.0% (13/25) | 2.00 |
| **Passive (`fixed` schedule)** | $0.10$ ($10\%$) | 25 | 20.0% (5/25) | 2.24 |
| **Stochastic (`random`)** | $0.00$ ($0\%$) | 25 | 76.0% (19/25) | 2.36 |
| **Stochastic (`random`)** | $0.01$ ($1\%$) | 25 | 52.0% (13/25) | 2.08 |
| **Stochastic (`random`)** | $0.05$ ($5\%$) | 25 | 36.0% (9/25) | 2.00 |
| **Stochastic (`random`)** | $0.10$ ($10\%$) | 25 | 20.0% (5/25) | 2.24 |

---

### 3. Key Observations & Findings

1. **Noise Graceful Degradation:** Active disagreement degrades gracefully from $84.0\%$ at $\sigma = 0.0$ to $80.0\%$ at $\sigma = 0.01$, $56.0\%$ at $\sigma = 0.05$, and $32.0\%$ at $\sigma = 0.10$.
2. **Superior Robustness at Moderate & High Noise:** At $1\%$ noise, Active achieves $80.0\%$ recovery, significantly outperforming Fixed ($64.0\%$) and Random ($52.0\%$). At $10\%$ noise, Active achieves $32.0\%$ recovery compared to $20.0\%$ for Fixed and Random.
3. **Weak-Form Space-Time Integration Shield:** By integrating candidate operators against smooth space-time test functions $\phi(x, y, t)$, the weak-form formulation avoids numerical finite-difference amplification of noise, preserving identifiability under realistic experimental noise.
