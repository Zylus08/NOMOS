# Project NOMOS — Milestone M5.3
## Blind Discovery Observational Contract & Information Boundary Specification

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Module Target:** `nomos/pde/isolation.py`, `nomos/closed_loop/oracle.py`, `nomos/closed_loop/controller.py`  
**Execution Timestamp:** November 2026  

---

### 1. Specification of the Blind Discovery Contract

To guarantee that Project NOMOS performs genuine autonomous scientific discovery from observations without privileged access to the simulation oracle, this contract formally establishes the immutable boundary between **Simulation Truth** and **Learner Observations**.

```
+----------------------------------------------------------------------------------+
|                                SIMULATION ORACLE                                 |
|  - Ground Truth Simulator (Equations, Parameters, Solvers)                       |
|  - Unsanitized Trajectories (u_clean, u_t_true, true_parameters)                  |
|  - Benchmark Identity (pde_name: "kdv", "viscous_burgers", "gray_scott", etc.)   |
+----------------------------------------------------------------------------------+
                                        ||
                                        ||  [ISOLATION BOUNDARY / SERIALIZATION]
                                        ||  create_blind_field_observation()
                                        \/
+----------------------------------------------------------------------------------+
|                            BLIND DISCOVERY LEARNER                               |
|  PERMITTED:                                                                      |
|    - Observed noisy state arrays u(x, t) or u(x, y, t)                           |
|    - Numerical coordinates (x, y, t) and spatial/temporal step sizes (dx, dy, dt)|
|    - Declared boundary condition type (e.g. Periodic)                            |
|    - Channel identifiers (e.g. ["u"] or ["u", "v"] or ["omega"])                 |
|    - Generic operator grammar (algebraic polynomials, spatial derivatives)       |
|                                                                                  |
|  FORBIDDEN (PURGED / BLINDED):                                                   |
|    - True PDE name (pde_name is replaced with opaque "blind_field_<uuid>")        |
|    - True physical parameter values (true_parameters = None)                     |
|    - True analytical derivatives (u_t_true = None)                               |
|    - Clean noiseless fields (u_clean = None)                                     |
|    - Simulator implementation class or internal state                            |
|    - Benchmark evaluation labels or test-set answers                             |
|    - Hardcoded or benchmark-specific hypothesis priors                           |
+----------------------------------------------------------------------------------+
```

---

### 2. Permitted vs. Forbidden Information Table

| Information Category | Specific Data Element | Learner Visible? | Storage / Transmission Rule |
| :--- | :--- | :---: | :--- |
| **Observation Grid** | Spatial coordinates ($x, y$), Time grid ($t$) | **YES** | Preserved on `SpatiotemporalField` |
| **Observation Grid** | Differential steps ($dx, dy, dt$) | **YES** | Derived numerically from coordinate arrays |
| **State Channels** | Number and names of channels (`["u"]`, `["u", "v"]`) | **YES** | Declared sensor channels |
| **Measured Data** | Noisy numerical state arrays $u(\mathbf{x}, t)$ | **YES** | Copied as `field.u` |
| **Boundary Physics** | Declared BC (e.g. `BoundaryConditionType.PERIODIC`) | **YES** | Declared experimental domain property |
| **Hypothesis Grammar**| Declared operator library (derivatives up to 4th order, polynomials) | **YES** | Disclosed mathematical prior |
| **System Identity** | True PDE Name (`field.pde_name`) | **NO (BLINDED)** | **Replaced with opaque hash `blind_field_<id>`** |
| **System Identity** | Simulator Class (`KdV1DSimulator`, etc.) | **NO (BLINDED)** | Quarantined inside Oracle instance |
| **Ground-Truth Truth**| Exact parameter values ($c=2, \nu=0.05, D_v=0.08$) | **NO (PURGED)** | `true_parameters = None` |
| **Clean Field** | Uncorrupted trajectory without noise ($u_{\text{clean}}$) | **NO (PURGED)** | `u_clean = None` |
| **True Velocity** | Exact temporal derivative ($\partial_t u_{\text{true}}$) | **NO (PURGED)** | `u_t_true = None` |
| **Hypothesis Prior** | Pre-seeded impostor hypotheses with ground-truth values | **NO (PURGED)** | **Deleted entirely from controller** |
| **Candidate Library** | Custom 2D libraries matching only true terms | **NO (PURGED)** | **Replaced with generic overcomplete grammar** |

---

### 3. Implementation and Enforcement

The contract is enforced through two mandatory code modifications:

1. **In `nomos/pde/isolation.py`:**
   ```python
   def create_blind_field_observation(field: SpatiotemporalField) -> SpatiotemporalField:
       """
       Enforces strict zero-leakage blind contract.
       Purges simulator identity, parameters, clean fields, and derivatives.
       """
       opaque_id = hashlib.sha256(f"{field.id}_{time.time()}".encode("utf-8")).hexdigest()[:12]
       return SpatiotemporalField(
           id=f"blind_obs_{opaque_id}",
           pde_name=f"blind_system_{opaque_id}",  # OPAQUE IDENTIFIER
           x=field.x.copy(),
           y=field.y.copy() if field.y is not None else None,
           t=field.t.copy(),
           u=field.u.copy(),
           channel_names=copy.deepcopy(field.channel_names),
           boundary_condition=field.boundary_condition,
           spatial_dim=field.spatial_dim,
           units=copy.deepcopy(field.units),
           u_clean=None,
           u_t_true=None,
           true_parameters=None,
           observation_mask=field.observation_mask.copy() if field.observation_mask is not None else None,
           noise_level=field.noise_level,
           provenance={"isolated": True, "blind_contract_enforced": True},
       )
   ```

2. **In `nomos/closed_loop/controller.py`:**
   - Eliminate all string matches on `pde_name`.
   - Implement data-derived multi-threshold hypothesis generation.
   - Enforce that hypothesis generation depends strictly on the numerical arrays of `field.u`.
