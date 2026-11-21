# NOMOS Milestone M2 — Neural Guidance & Structural Prior Extraction

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Guidance Specialists:** Agents D09, D10  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Module:** `nomos/neural/guidance.py`  

---

## 1. Motivation: Overcoming the Combinatorial Bottleneck

In unguided symbolic regression, candidate expression space grows exponentially with tree depth. For a system with $n$ variables and operator set $\mathcal{O}$, exploring trees of depth $d$ requires evaluating $\Omega((|\mathcal{O}| + n)^{2^d - 1})$ expressions. When many variables are uncoupled in a particular differential equation coordinate (e.g., $\dot{x}_1$ depends only on $x_2$ in an oscillator), unguided search wastes $> 90\%$ of its evaluation budget proposing candidate subtrees containing irrelevant coordinates.

NOMOS M2 resolves this fundamental bottleneck via the **Neural Guidance Engine**: it interrogates the trained neural dynamics surrogate using exact autograd to extract structural priors that guide symbolic search.

---

## 2. Jacobian Sensitivity Analysis

Given the surrogate Jacobian $J_{ij}(x_k) = \frac{\partial f_i(x_k)}{\partial x_j}$ evaluated across $M$ phase-space points $\{x_k\}_{k=1}^M$, the **mean absolute sensitivity** of target coordinate $i$ with respect to state coordinate $j$ is computed as:

$$S_{ij} = \frac{1}{M} \sum_{k=1}^M \left| \frac{\partial f_i(x_k)}{\partial x_j} \right|$$

Normalizing across all state variables yields the **State Importance Distribution**:

$$p_i(x_j) = \frac{S_{ij}}{\sum_{l=1}^n S_{il} + \epsilon}$$

### Impact on Search:
1. **Beam Search:** Terminal variables $x_j$ are sorted by $p_i(x_j)$; variables with $p_i(x_j) < 0.05$ are pruned from initial terminal expansion.
2. **Genetic Programming:** Variable leaf mutations sample state coordinates proportionally to $p_i(x_j)$ rather than uniformly.

---

## 3. Curvature & Nonlinearity Spectrum

To determine whether the target vector field requires nonlinear or transcendental primitives (e.g., $\sin, \cos, \div$), the guidance engine evaluates the **Linear Fit Residual Ratio**:

1. Fit optimal linear hyperplane to surrogate predictions:
   $$w^* = \arg\min_w \sum_{k=1}^M \left( \hat{f}_i(x_k) - (w_0 + w^T x_k) \right)^2$$
2. Compute residual variance ratio:
   $$\eta_{nonlin} = \frac{\frac{1}{M} \sum_{k=1}^M \left( \hat{f}_i(x_k) - (w_0 + {w^*}^T x_k) \right)^2}{\text{Var}(\hat{f}_i) + \epsilon}$$

### Prior Weight Adjustment:
- **Linear Regime ($\eta_{nonlin} \le 0.08$):**
  Trigonometric and transcendental operators are assigned low sampling weights ($w = 0.3$), preventing unneeded search in transcendental space.
- **Strongly Nonlinear Regime ($\eta_{nonlin} > 0.08$):**
  Trigonometric operators (`sin`, `cos`) are promoted to high priority ($w = 1.5$).
- **Rational / Asymptote Signature:**
  If the standard deviation of Jacobian gradients $\text{Std}_k(\nabla \hat{f}_i(x_k))$ exceeds $2 \times$ the mean, indicating steep gradients near poles or saturation, the division operator (`div`) is promoted ($w = 1.2$).
