# NOMOS Milestone M2 — Neural Dynamics Surrogate & Derivative Supervision

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Neural Specialists:** Agents D07, D08  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Modules:** `nomos/neural/surrogate.py`, `nomos/neural/trainer.py`  

---

## 1. Mathematical Formulation & Architecture

The NOMOS M2 Neural Dynamics Surrogate approximates the continuous vector field governing observed state trajectories:
$$\frac{dx}{dt} = f_{\theta}(x), \quad f_{\theta}: \mathbb{R}^n \to \mathbb{R}^n$$

### 1.1 Architecture Specifications
- **Multi-Layer Perceptron (MLP):** Input dimension $n$ (state variables), $L$ hidden layers with width $d_h = 32$ or $64$, output dimension $n$.
- **Smooth Activation Function:** Employs the **SiLU (Sigmoid Linear Unit)** activation function $\sigma(z) = \frac{z}{1 + e^{-z}}$ (or smooth Tanh).
  - *Mathematical Importance:* Unlike piecewise linear activations such as ReLU (whose second derivative is zero almost everywhere and whose first derivative is discontinuous), SiLU guarantees $C^\infty$ smoothness, ensuring the continuous existence and differentiability of the state Jacobian $J(x)$.
- **Built-in Normalization Buffers:**
  Registers state mean $\mu_x$ and standard deviation $\sigma_x$ as persistent PyTorch buffers:
  $$x_{\text{norm}} = \frac{x - \mu_x}{\sigma_x + \epsilon}$$
  Ensuring numerical stability during gradient propagation across variables with differing physical units.

---

## 2. Derivative Supervision & Training Protocol

### 2.1 Trajectory Differentiation
Trajectory derivatives are estimated directly from raw time series observations using high-order Savitzky-Golay filtering or 4th-order central finite differences:
$$\dot{X}_{\text{obs}} \approx \mathcal{D}(X, t)$$

### 2.2 Training Objective & Regularization
The surrogate parameters $\theta$ are trained by minimizing the mean squared derivative prediction error:
$$\mathcal{L}(\theta) = \frac{1}{M_{\text{train}}} \sum_{k=1}^{M_{\text{train}}} \| \dot{x}_k - f_{\theta}(x_k) \|_2^2 + \lambda \|\theta\|_2^2$$
with weight decay $\lambda = 10^{-5}$ to prevent overfitting.

### 2.3 Early Stopping & Validation Protocol
- Data is strictly partitioned into disjoint train (80%) and validation (20%) sets.
- Optimization uses Adam with learning rate scheduling (`ReduceLROnPlateau`, factor $0.5$, patience $5$).
- Early stopping halts training when validation loss fails to improve for 12 consecutive epochs, preventing overfitting to observation noise.

---

## 3. Analytical State Jacobian Computation via Autograd

For any sampled phase-space point $x \in \mathbb{R}^n$, the surrogate computes the exact state Jacobian matrix:
$$J_{ij}(x) = \frac{\partial f_{\theta, i}(x)}{\partial x_j}$$
using PyTorch's functional automatic differentiation engine (`torch.autograd.functional.jacobian`).

This analytical Jacobian requires zero finite-difference approximations and provides exact, point-wise sensitivity of each dynamical coordinate with respect to all state variables across the observed manifold.
