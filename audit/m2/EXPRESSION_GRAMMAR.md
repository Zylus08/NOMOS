# NOMOS Milestone M2 — Expression Tree Grammar & Domain Protections

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Symbolic Specialists:** Agents D01, D02, E01, E07  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Modules:** `nomos/symbolic/primitives.py`, `nomos/symbolic/trees.py`  

---

## 1. Abstract Syntax Tree (AST) Specification

The NOMOS M2 expression representation is implemented from first principles as an algebraic Abstract Syntax Tree (AST). Each node in an `ExpressionTree` is an instance of `ExpressionNode` defined by:

```python
class NodeType(Enum):
    CONSTANT = 1
    VARIABLE = 2
    ADD = 11; SUB = 12; MUL = 13; DIV = 14; POW = 15
    NEG = 4; SIN = 5; COS = 6; EXP = 7; LOG = 8; SQRT = 9
```

### 1.1 Structural Invariants
1. **Arity Constraints:**
   - Leaf nodes (`CONSTANT`, `VARIABLE`) have exactly 0 children (`arity == 0`).
   - Unary operator nodes (`NEG`, `SIN`, `COS`, `EXP`, `LOG`, `SQRT`) have exactly 1 child (`arity == 1`).
   - Binary operator nodes (`ADD`, `SUB`, `MUL`, `DIV`, `POW`) have exactly 2 children (`arity == 2`).
2. **Deterministic Evaluation:**
   - Vectorized evaluation operates over 2D NumPy arrays of shape $(M, n_{\text{vars}})$ and returns 1D arrays of shape $(M,)$.
   - All evaluation paths are pure functions with zero persistent side-effects.

---

## 2. Hypothesis Class & Domain Protections

In open-ended symbolic regression, randomly generated or mutated expression trees frequently encounter mathematical domain violations:
- Division by zero: $x / 0$
- Logarithm of non-positive values: $\log(x)$ for $x \le 0$
- Square root of negative values: $\sqrt{x}$ for $x < 0$
- Exponential runaway / overflow: $\exp(1000)$
- Non-integer powers of negative values: $(-2.5)^{1.5}$

Rather than allowing unhandled floating-point exceptions (`ZeroDivisionError`, `FloatingPointError`) or returning uninformative `NaN`/`Inf` arrays that poison gradient optimization, NOMOS M2 implements mathematically explicit, continuous domain-protected operators:

### 2.1 Protected Division ($\div_{\text{prot}}$)
$$\div_{\text{prot}}(u, v) = \begin{cases} \frac{u}{v} & \text{if } |v| > \epsilon \\ \frac{u}{\text{sign}(v) \cdot \epsilon} & \text{if } 0 < |v| \le \epsilon \\ \frac{u}{\epsilon} & \text{if } v = 0 \end{cases}$$
with $\epsilon = 10^{-6}$. This guarantees continuous, non-exploding gradients across phase space.

### 2.2 Protected Logarithm ($\log_{\text{prot}}$)
$$\log_{\text{prot}}(u) = \log(|u| + \epsilon), \quad \epsilon = 10^{-6}$$
Ensures real-valued outputs for all $u \in \mathbb{R}$, smoothly penalizing non-positive regimes without NaN propagation.

### 2.3 Protected Exponential ($\exp_{\text{prot}}$)
$$\exp_{\text{prot}}(u) = \exp(\text{clip}(u, -50.0, 50.0))$$
Clips inputs to $[-50.0, 50.0]$ before computing $\exp(u)$, preventing IEEE 754 floating-point overflow (`inf`) while preserving exact gradients in physically realistic regimes.

### 2.4 Protected Square Root ($\sqrt{\text{prot}}$)
$$\sqrt{\text{prot}}(u) = \sqrt{|u|}$$
Ensures domain safety over all real state coordinates.

---

## 3. Structural Complexity Scoring Function

To enforce Occam's razor and prevent tree bloat during search, NOMOS M2 defines a strictly monotonic structural complexity metric:

$$\mathcal{C}(T) = \sum_{v \in \text{nodes}(T)} w(\text{type}(v))$$

Where weights reflect mathematical operational cost:
- `CONSTANT`: $w = 1.0$
- `VARIABLE`: $w = 1.0$
- `ADD`, `SUB`: $w = 1.0$
- `MUL`: $w = 1.5$
- `NEG`: $w = 0.5$
- `DIV`: $w = 2.0$
- `SIN`, `COS`: $w = 2.0$
- `EXP`, `LOG`: $w = 3.0$
- `POW`: $w = 2.5$

This formulation ensures:
1. Pure linear terms ($c \cdot x$) have minimal complexity $\mathcal{C} = 3.5$.
2. Nonlinear trigonometric terms ($c \cdot \sin(x)$) have complexity $\mathcal{C} = 4.5$.
3. Rational structures ($c \cdot (x / (1 + x))$) have complexity $\mathcal{C} = 7.5$.
