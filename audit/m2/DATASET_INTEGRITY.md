# NOMOS Milestone M2 — Dataset Integrity & Anti-Leakage Sandboxing

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Integrity Specialists:** Agents C01, C04, C08, C09, C11, C12  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Modules:** `nomos/data/schema.py`, `nomos/data/isolation.py`  

---

## 1. Information-Theoretic Anti-Leakage Sandbox

In scientific equation discovery, the most insidious vulnerability is **subconscious data leakage**: exposing ground-truth parameter values, equation strings, or test trajectories to the learner during fitting or hyperparameter selection.

NOMOS M2 enforces absolute isolation via the `IsolatedLearnerDataset` abstraction:
1. **Physical Separation of Contracts:**
   - The learner engine (`M2DiscoveryEngine`, `StructuredBeamSearch`, `GeneticProgrammingSearch`) receives strictly an `IsolatedLearnerDataset`.
   - `IsolatedLearnerDataset` contains ONLY:
     - Numerical trajectory coordinates: $t \in \mathbb{R}^M$, $X_{\text{obs}} \in \mathbb{R}^{M \times n}$.
     - Variable names: `['x', 'v']` or `['theta', 'omega']`.
   - **ZERO Ground-Truth Access:** Ground-truth ODE functions ($f_{\text{true}}$), analytical solutions, parameter values ($\alpha, \beta, \gamma$), and true clean trajectories ($X_{\text{clean}}$) are strictly inaccessible to the learner.
2. **Adversarial Leakage Audit:**
   The test suite `tests/test_data.py::test_metadata_isolation_sandbox` and `tests/test_adversarial.py::test_adversarial_data_leakage_attack` verify that any attempt by discovery algorithms to access hidden system attributes raises an `AttributeError` or security boundary violation.

---

## 2. Trajectory-Disjoint Data Splitting

NOMOS M2 enforces **trajectory-disjoint splitting**:
- Training trajectories and validation trajectories are generated from completely independent initial conditions $x_0^{(\text{train})} \neq x_0^{(\text{val})}$.
- Out-of-distribution test trajectories are integrated over extended time horizons ($t \in [0, 10.0]$ vs $t \in [0, 8.0]$) from perturbed initial conditions outside the convex hull of training data:
  $$x_0^{(\text{test})} = 1.3 \cdot x_0^{(\text{train})}$$
- This guarantees that discovered models cannot achieve low rollout error through memorization or temporal interpolation.

---

## 3. Cryptographic Provenance & Dataset Hashing

Every dataset generated within Project NOMOS computes an immutable SHA-256 cryptographic checksum:
$$\mathcal{H}_{\text{data}} = \text{SHA256}(\text{system\_name} \parallel \text{variable\_names} \parallel t.\text{tobytes}() \parallel X.\text{tobytes}())$$
This hash is logged in `audit/m2/SCIENTIFIC_RECOVERY.csv` to ensure 100% bitwise reproducibility of all experimental benchmarks.
