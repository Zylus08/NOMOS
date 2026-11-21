# M1 SPARSE IDENTIFICATION ALGORITHM (STLSQ)
**Roles:** Agents D01, D02, D03, D04, D05, D06, D07  
**Reviewer:** I01 — Mathematics Reviewer  
**Investigator:** Saksham Mishra <mishrasaksham080705@gmail.com>

---

## 1. Algorithm Derivation & Active Set Refitting

The NOMOS STLSQ engine solves:
$$\min_{\boldsymbol{\Xi}} \|\dot{\mathbf{X}} - \mathbf{\Theta}(\mathbf{X})\boldsymbol{\Xi}\|_F^2 + \alpha \|\boldsymbol{\Xi}\|_F^2 \quad \text{s.t.} \quad |\boldsymbol{\xi}_{j,k}| \ge \lambda \text{ or } \boldsymbol{\xi}_{j,k} = 0$$

### Algorithm Steps:
1. **Column Normalization:** Columns of $\mathbf{\Theta}(\mathbf{X})$ are normalized by their L2 norm $s_j = \|\boldsymbol{\theta}_j\|_2$, forming $\tilde{\mathbf{\Theta}} = \mathbf{\Theta} \mathbf{D}^{-1}$.
2. **Initial Regularized Least Squares:**
   $$\tilde{\boldsymbol{\Xi}}^{(0)} = (\tilde{\mathbf{\Theta}}^T \tilde{\mathbf{\Theta}} + \alpha \mathbf{I})^{-1} \tilde{\mathbf{\Theta}}^T \dot{\mathbf{X}}$$
3. **Thresholding in Physical Space:**
   Compute physical coefficients $\boldsymbol{\Xi}^{(k)} = \mathbf{D}^{-1} \tilde{\boldsymbol{\Xi}}^{(k)}$.
   Identify active support $S^{(k)} = \{(j,c) : |\xi_{j,c}^{(k)}| \ge \lambda\}$.
4. **Active Set Ridge Subproblem:**
   For each state variable column $c \in \{1, \dots, n\}$, solve least squares strictly on the submatrix $\tilde{\mathbf{\Theta}}_{S_c}$.
5. **Convergence Detection:**
   If $S^{(k)} == S^{(k-1)}$ or a cycle is detected, terminate iteration.
6. **Shrinkage-Free Active Refit (D02):**
   Once support $S^*$ is locked, unregularized least squares ($\alpha = 0$) is refitted on $\mathbf{\Theta}_{S^*}$ to eliminate all ridge/L2 bias from recovered parameters.
