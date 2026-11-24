# Project NOMOS — Milestone M5.2
## Held-Out Generalization Forensics: Brusselator Parity & Cahn–Hilliard Truncation

**Principal Investigator / Git Identity:** Saksham Mishra `<mishrasaksham080705@gmail.com>`  
**Hardware Profile:** Intel Core i7-12650H, 16 GB RAM, Windows 11  
**Target Manuscript Claim:** Claim P-08, P-09 (`paper/main.tex` lines 240–243)  
**Evaluated Artifacts:** `audit/m5_1/HELD_OUT_BENCHMARKS.csv`, `audit/m5_1/STRONG_BASELINES.csv`, `experiments/m5_2/run_ablations.py`  

---

### 1. Executive Summary

Section 5.5 of `paper/main.tex` presents 280 episodes across two additional benchmark systems (2D Brusselator and 1D Cahn–Hilliard) as evidence of held-out generalizability:
> *"To verify that the active discovery engine generalises beyond the primary five benchmarks, we evaluated 280 held-out episodes across 2D Brusselator reaction--diffusion and 1D Cahn--Hilliard phase separation without retraining or hyperparameter retuning, achieving 50.0% exact multi-parameter recovery on Brusselator and recovering dominant double-well flux on Cahn--Hilliard."*

The M5.2 red-team audit reveals that **the narrative in Section 5.5 severely misrepresents the actual experimental outcomes**:
1. **Universal Strategy Parity on 2D Brusselator:** On the 2D Brusselator benchmark, **every single evaluated acquisition strategy**—Active (Greedy Disagreement), Active (Cost-Normalized), Passive (Fixed), Passive (Random), and all three Strong Baselines (Uncertainty-Aware, Model Discrimination, Handcrafted)—achieved **identically 50.0% recovery (10/20)** and consumed **identically 2.00 mean queries**. Active learning provided **precisely zero marginal advantage**.
2. **Universal 0.0% Exact Recovery on 1D Cahn–Hilliard:** On 1D Cahn–Hilliard, every evaluated acquisition strategy achieved **0.0% exact recovery** because the defining 4th-order biharmonic operator $-0.0025 u_{xxxx}$ was pruned by STLSQ thresholding across all runs.
3. **Post-Hoc Tuning of "Held-Out" Systems:** Git revision history confirms that the weak-form discovery libraries were specifically modified during Milestone M5.1 to support these systems (adding `(u^3)_xx` to 1D weak form, `u^2*v` to 2D weak form, and hardcoding matching impostors in `controller.py`). Presenting them as untuned held-out generalization targets is an overstatement.

---

### 2. Forensic Breakdown of Held-Out Benchmark Logs

From `audit/m5_2/ABLATIONS_AND_BIC.json` ($N = 280$ total held-out episodes):

#### 2.1 2D Brusselator Reaction-Diffusion ($N = 140$ episodes)
Target Equation: $\partial_t u = 0.1 \Delta u - 4.0 u + 1.0 u^2 v + 1.0$

| Acquisition Strategy | Strategy Type | Episodes ($n$) | Recovery Rate | Mean Queries | Mean Parameter Error |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Greedy Disagreement (NOMOS)** | **Active** | 20 | **50.0% (10/20)** | **2.00** | **0.5368** |
| **Cost-Normalized (NOMOS)** | **Active** | 20 | **50.0% (10/20)** | **2.00** | **0.5368** |
| **Sequential Schedule (Passive)** | **Passive** | 20 | **50.0% (10/20)** | **2.00** | **0.5368** |
| **Uniform Random (Passive)** | **Passive** | 20 | **50.0% (10/20)** | **2.00** | **0.5368** |
| **Uncertainty-Aware (Max Variance)**| **Active SOTA** | 20 | **50.0% (10/20)** | **2.00** | **0.5368** |
| **Model Discrimination (B-Optimal)**| **Active SOTA** | 20 | **50.0% (10/20)** | **2.00** | **0.5368** |
| **Handcrafted Expert Schedule** | **Heuristic** | 20 | **50.0% (10/20)** | **2.00** | **0.5368** |

*Forensic Finding:* The performance matrix is completely degenerate across all seven acquisition strategies. Whether the algorithm selected initial conditions via active vector-field divergence, passive fixed ordering, epistemic variance, or pure random sampling, exactly 10 episodes succeeded and exactly 10 episodes failed across the identical noise levels ($100\%$ success at $\sigma=0.0, 0.01$; $0\%$ success at $\sigma=0.05, 0.10$). Omission of this baseline parity in Section 5.5 violates transparent reporting standards.

#### 2.2 1D Cahn–Hilliard Phase Separation ($N = 140$ episodes)
Target Equation: $\partial_t u = -1.0 u_{xx} + 1.0 (u^3)_{xx} - 0.0025 u_{xxxx}$

| Acquisition Strategy | Strategy Type | Episodes ($n$) | Strict Exact Recovery | Partial Support Recovery | Mean Queries |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Greedy Disagreement (NOMOS)** | **Active** | 20 | **0.0% (0/20)** | **100.0% (20/20)** | **2.00** |
| **Cost-Normalized (NOMOS)** | **Active** | 20 | **0.0% (0/20)** | **100.0% (20/20)** | **2.00** |
| **Sequential Schedule (Passive)** | **Passive** | 20 | **0.0% (0/20)** | **100.0% (20/20)** | **2.00** |
| **Uniform Random (Passive)** | **Passive** | 20 | **0.0% (0/20)** | **100.0% (20/20)** | **2.00** |
| **Uncertainty-Aware (Max Variance)**| **Active SOTA** | 20 | **0.0% (0/20)** | **100.0% (20/20)** | **2.60** |
| **Model Discrimination (B-Optimal)**| **Active SOTA** | 20 | **0.0% (0/20)** | **100.0% (20/20)** | **2.85** |
| **Handcrafted Expert Schedule** | **Heuristic** | 20 | **0.0% (0/20)** | **100.0% (20/20)** | **2.00** |

*Forensic Finding:* Under the strict recovery criteria pre-specified in the experiment script (`wh_keys == true_keys`), zero out of 140 episodes achieved exact recovery. All methods identified the 2nd-order double-well flux $-1.0 u_{xx} + 1.0 (u^3)_{xx}$ while thresholding out the 4th-order operator $-0.0025 u_{xxxx}$.

---

### 3. Physical Analysis: The Brusselator Turing Myth

As identified by Reviewer Group D (Numerical PDE), the manuscript's physical characterization of the Brusselator benchmark contains an elementary error:
- **Diffusion Ratio:** $D_u = 0.1, D_v = 0.05 \implies \frac{D_v}{D_u} = 0.5 < 1$.
- **Turing Condition:** Turing's classical theorem requires the inhibitor to diffuse strictly faster than the activator: $\frac{D_v}{D_u} > d_c > 1$.
- **Determinant Check:** The spatial dispersion matrix has determinant $\det(J - k^2 D) = 1 + 0.005 k^4 > 0$ for all real wavenumbers $k \ge 0$.
- **Conclusion:** Spatial Turing patterns are mathematically impossible under the simulated parameters. The system exhibits only a spatially uniform Hopf limit cycle. Calling initial perturbations "Turing-spot drivers" is scientifically inaccurate.

---

### 4. Prescriptive Manuscript Amendments

1. **Transparently Disclose Brusselator Parity:**  
   Revise Section 5.5 to state explicitly that on 2D Brusselator, all seven strategies (active, passive, random, and heuristic) tied at $50.0\%$ recovery rate, demonstrating that when the candidate pool contains no severe dynamical degeneracy, active selection confers no advantage over passive sampling.
2. **Reclassify Cahn–Hilliard as Tier 3 Partial Support:**  
   Report that all strategies achieved $0.0\%$ strict structural recovery due to STLSQ threshold pruning of the 4th-order biharmonic operator, but achieved $100\%$ partial flux recovery of the dominant second-order terms.
3. **Correct Physical Terminology:**  
   Replace references to "Turing morphogenesis" with "autocatalytic limit-cycle reaction dynamics".
