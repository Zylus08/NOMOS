# NOMOS Milestone M2 — Evolutionary Symbolic Regression (Genetic Programming)

**Milestone:** M2 — Open-Ended Neural-Symbolic Discovery Beyond Fixed Candidate Libraries  
**Lead Evolutionary Specialists:** Agents D01, D02, D13  
**Principal Investigator:** Saksham Mishra (`mishrasaksham080705@gmail.com`)  
**Implementation Module:** `nomos/search/genetic.py`  

---

## 1. Algorithmic Architecture

The NOMOS M2 Genetic Programming engine (`GeneticProgrammingSearch`) implements population-based stochastic expression evolution over abstract syntax trees. It serves as an independent, alternative search paradigm to validate results discovered by structured beam search.

---

## 2. Evolutionary Operators & Population Lifecycle

### 2.1 Population Initialization
Employs the **Ramped Half-and-Half** initialization method (Koza 1992):
- Half the population is generated using the *Full* method (all branches grown to maximum initial depth).
- Half the population is generated using the *Grow* method (branches terminate with variables or constants probabilistically).
- Depth ramps uniformly from 1 to 3, ensuring structural diversity in generation 0.

### 2.2 Selection Mechanism
- **Tournament Selection:** Selects individuals via $k$-way tournament selection ($k=3$) based on Pareto dominance and multi-objective fitness:
  $$\text{Fitness}(T) = \mathcal{L}_{MSE}(T) + \lambda \cdot \mathcal{C}(T)$$
- **Elitism:** The top 2 non-dominated individuals from each generation are preserved verbatim into the next generation.

### 2.3 Genetic Variation Operators
1. **Subtree Crossover:** Randomly selects crossover points in two parent trees and swaps the subtrees, validating that child depths remain $\le d_{\max}$.
2. **Subtree Mutation:** Replaces a randomly selected node with a freshly generated random subtree.
3. **Point Mutation:** Replaces an operator with another operator of identical arity (e.g., swapping `+` with `-`, or `sin` with `cos`).
4. **Constant Perturbation:** Perturbs existing constant values via Gaussian noise: $c \leftarrow c + \mathcal{N}(0, 0.2^2)$.

---

## 3. Bloat Control & Pareto Frontier Tracking

To prevent the classic genetic programming failure mode of exponential expression bloat:
1. Strict maximum depth bound ($d \le 4$).
2. Non-dominated candidates across all generations are streamed directly into the unified `ParetoFrontier` repository.
