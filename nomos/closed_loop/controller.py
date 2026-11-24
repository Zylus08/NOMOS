"""
NOMOS Autonomous Closed-Loop Scientific Controller
Phase 1: OBSERVE -> HYPOTHESIZE -> COMPARE -> DESIGN -> EXPERIMENT -> UPDATE -> VALIDATE -> STOP
Executes autonomous iterative experimentation and falsifiable law discovery.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from nomos.pde.schema import SpatiotemporalField, Grid1D, Grid2D, TimeGrid
from nomos.closed_loop.portfolio import ScientificHypothesis, HypothesisPortfolio, HypothesisStatus
from nomos.closed_loop.oracle import SimulationOracle, ExperimentRequest, ExperimentResponse, ExperimentCost
from nomos.closed_loop.acquisition import ExperimentAcquisitionEngine, AcquisitionStrategy
from nomos.closed_loop.diagnostics import IdentifiabilityStatus, IdentifiabilityAuditor
from nomos.pde.weak_form import WeakFormPDEDiscovery
from nomos.pde.weak_form_2d import WeakForm2DPDEDiscovery
from nomos.pde.symbolic_search import DifferentialBeamSearch


@dataclass
class InvestigationStepRecord:
    """Audit log entry for a single closed-loop experimentation cycle."""
    iteration: int
    stage: str                              # "DESIGN", "EXPERIMENT", "UPDATE", "VALIDATE", "STOP"
    selected_experiment: str
    acquisition_score: float
    active_hypotheses_count: int
    top_hypothesis: Optional[str]
    identifiability_status: str
    cost: Dict[str, Any]
    falsified_hypotheses: List[str]
    supported_hypotheses: List[str]
    elapsed_time_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InvestigationEpisode:
    """Complete history of an autonomous closed-loop scientific investigation."""
    system_name: str
    strategy: str
    max_budget: int
    noise_level: float
    random_seed: int
    status: IdentifiabilityStatus
    winning_hypothesis: Optional[ScientificHypothesis]
    total_cost: ExperimentCost
    duration_seconds: float
    trace: List[InvestigationStepRecord] = field(default_factory=list)
    portfolio_summary: List[Dict[str, Any]] = field(default_factory=list)


class ClosedLoopController:
    """
    Autonomous closed-loop scientific discovery controller.
    Iterates through observation, hypothesis generation, experiment selection,
    oracle execution, parameter refitting, and stopping audits.
    """

    def __init__(
        self,
        oracle: SimulationOracle,
        grid: Any,
        candidate_experiment_pool: List[Tuple[str, np.ndarray, float]], # (label, u0, cost)
        strategy: AcquisitionStrategy = AcquisitionStrategy.GREEDY_DISAGREEMENT,
        max_budget: int = 6,
        noise_level: float = 0.0,
        random_seed: int = 42,
        dimension: int = 1,
        target_channel: str = "u",
        candidate_library: Optional[List[str]] = None,
    ):
        self.oracle = oracle
        self.grid = grid
        self.candidate_pool = candidate_experiment_pool
        self.strategy = strategy
        self.max_budget = int(max_budget)
        self.noise_level = float(noise_level)
        self.random_seed = int(random_seed)
        self.dimension = int(dimension)
        self.target_channel = target_channel
        self.candidate_library = candidate_library or ["u*u_x", "u_xx", "u_xxx", "u_xxxx"]

        # Subsystems
        self.portfolio = HypothesisPortfolio()
        self.acquisition = ExperimentAcquisitionEngine(strategy=self.strategy, random_seed=self.random_seed)
        self.auditor = IdentifiabilityAuditor()

        # State storage
        self.observed_fields: List[SpatiotemporalField] = []
        self.trace: List[InvestigationStepRecord] = []

    def run_investigation(self, initial_field: Optional[SpatiotemporalField] = None) -> InvestigationEpisode:
        """
        Execute full autonomous scientific investigation loop.
        """
        t_start = time.time()
        iteration = 0

        # Stage 0: OBSERVE initial dataset
        if initial_field is not None:
            self.observed_fields.append(initial_field)
            self._generate_initial_hypotheses(initial_field)
        else:
            # Execute first experiment from pool
            init_lbl, init_u0, _ = self.candidate_pool[0]
            req = ExperimentRequest(
                experiment_id=f"exp_{iteration:02d}_{init_lbl}",
                u0=init_u0,
                noise_level=self.noise_level,
                random_seed=self.random_seed,
            )
            resp = self.oracle.execute_experiment(req)
            self.observed_fields.append(resp.field)
            self._generate_initial_hypotheses(resp.field)

        # Audit stopping condition immediately after initialization
        status, winning_h, diag = self.auditor.audit_portfolio(self.portfolio, iteration, self.max_budget)

        # Iterative Closed-Loop Cycle
        while iteration < self.max_budget and status == IdentifiabilityStatus.MULTIPLE_PLAUSIBLE_LAWS:
            iteration += 1
            step_t0 = time.time()

            # STAGE 1: COMPARE
            self.portfolio.compute_evidence_weights()
            active_hyps = self.portfolio.get_active()

            # STAGE 2: DESIGN
            dx = self.grid.dx
            dy = getattr(self.grid, "dy", 0.0)
            chosen_lbl, chosen_u0, acq_score, _ = self.acquisition.select_experiment(
                portfolio=self.portfolio,
                candidate_pool=self.candidate_pool,
                dx=dx,
                dy=dy,
                periodic=True,
                iteration_index=iteration,
            )

            # STAGE 3: EXPERIMENT (Strict Oracle Query)
            req = ExperimentRequest(
                experiment_id=f"exp_{iteration:02d}_{chosen_lbl}",
                u0=chosen_u0,
                noise_level=self.noise_level,
                random_seed=self.random_seed + iteration,
            )
            resp = self.oracle.execute_experiment(req)
            self.observed_fields.append(resp.field)

            # STAGE 4: UPDATE & VALIDATE
            falsified, supported = self._update_and_validate_hypotheses(resp.field, req.experiment_id, iteration)

            # STAGE 5: STOPPING AUDIT
            status, winning_h, diag = self.auditor.audit_portfolio(self.portfolio, iteration, self.max_budget)

            top_str = active_hyps[0].equation_str if active_hyps else None

            # Record step trace
            record = InvestigationStepRecord(
                iteration=iteration,
                stage="CLOSED_LOOP_STEP",
                selected_experiment=chosen_lbl,
                acquisition_score=round(acq_score, 6),
                active_hypotheses_count=len(self.portfolio.get_active()),
                top_hypothesis=top_str,
                identifiability_status=status.value,
                cost=resp.cost.to_dict(),
                falsified_hypotheses=falsified,
                supported_hypotheses=supported,
                elapsed_time_s=round(time.time() - step_t0, 4),
                metadata=diag,
            )
            self.trace.append(record)

            if status in (IdentifiabilityStatus.IDENTIFIED, IdentifiabilityStatus.BUDGET_EXHAUSTED):
                break

        total_duration = time.time() - t_start

        return InvestigationEpisode(
            system_name=self.observed_fields[0].pde_name,
            strategy=self.strategy.value,
            max_budget=self.max_budget,
            noise_level=self.noise_level,
            random_seed=self.random_seed,
            status=status,
            winning_hypothesis=winning_h,
            total_cost=self.oracle.cumulative_cost,
            duration_seconds=round(total_duration, 4),
            trace=self.trace,
            portfolio_summary=self.portfolio.export_summary(),
        )

    def _generate_initial_hypotheses(self, field: SpatiotemporalField, source_tag: str = "initial"):
        """Formulate candidate physical laws using discovery engines."""
        if self.dimension == 1:
            # 1. WSINDy fit
            wsindy = WeakFormPDEDiscovery(num_test_functions=80, threshold=0.045, random_seed=self.random_seed)
            res_w = wsindy.fit(field)
            if res_w.coefficients:
                h_wsindy = ScientificHypothesis(
                    id=f"hyp_wsindy_{field.pde_name}_{source_tag}",
                    equation_str=res_w.discovered_equation,
                    features=res_w.feature_names,
                    parameters=res_w.coefficients.copy(),
                    complexity=len(res_w.coefficients) * 2,
                    origin=f"wsindy_{source_tag}",
                    train_mse=res_w.residual_norm**2,
                    val_mse=res_w.residual_norm**2,
                    bic=float(len(field.u.flatten()) * np.log(res_w.residual_norm**2 + 1e-12) + len(res_w.coefficients) * np.log(len(field.u.flatten()))),
                )
                self.portfolio.register(h_wsindy)

            # 2. Scale-Adaptive Beam Search fit
            beam = DifferentialBeamSearch(scoring_mode="adaptive", complexity_penalty=1e-4, random_seed=self.random_seed)
            res_b = beam.fit(field)
            if res_b.coefficients:
                h_beam = ScientificHypothesis(
                    id=f"hyp_beam_{field.pde_name}_{source_tag}",
                    equation_str=res_b.discovered_equation,
                    features=res_b.feature_names,
                    parameters=res_b.coefficients.copy(),
                    complexity=len(res_b.coefficients) * 2,
                    origin=f"beam_{source_tag}",
                    train_mse=res_b.residual_norm**2,
                    val_mse=res_b.residual_norm**2,
                    bic=float(len(field.u.flatten()) * np.log(res_b.residual_norm**2 + 1e-12) + len(res_b.coefficients) * np.log(len(field.u.flatten()))),
                )
                self.portfolio.register(h_beam)

            # 3. Competing physical priors for active discrimination
            if source_tag == "initial":
                if "kdv" in field.pde_name:
                    h_adv = ScientificHypothesis(
                        id="hyp_linear_advection_impostor",
                        equation_str="u_t = -2.0000*u_x",
                        features=["u_x"],
                        parameters={"u_x": -2.0},
                        complexity=2,
                        origin="competing_physical_prior",
                        train_mse=0.001,
                        val_mse=0.001,
                        bic=0.0,
                    )
                    self.portfolio.register(h_adv)
                elif "burgers" in field.pde_name:
                    h_diff = ScientificHypothesis(
                        id="hyp_linear_diffusion_impostor",
                        equation_str="u_t = +0.0500*u_xx",
                        features=["u_xx"],
                        parameters={"u_xx": 0.05},
                        complexity=2,
                        origin="competing_physical_prior",
                        train_mse=0.001,
                        val_mse=0.001,
                        bic=0.0,
                    )
                    self.portfolio.register(h_diff)

        else:
            # 2D Field Hypothesis Generation via WSINDy-2D
            engine2d = WeakForm2DPDEDiscovery(num_test_functions=70, threshold=0.02, random_seed=self.random_seed)
            res2d = engine2d.fit_channel(field, self.target_channel, self.candidate_library)
            if res2d.coefficients:
                h2d = ScientificHypothesis(
                    id=f"hyp_wsindy2d_{field.pde_name}_{self.target_channel}_{source_tag}",
                    equation_str=res2d.discovered_equation,
                    features=res2d.feature_names,
                    parameters=res2d.coefficients.copy(),
                    complexity=len(res2d.coefficients) * 2,
                    origin=f"wsindy2d_{source_tag}",
                    train_mse=res2d.residual_norm**2,
                    val_mse=res2d.residual_norm**2,
                    bic=float(len(field.u.flatten()) * np.log(res2d.residual_norm**2 + 1e-12) + len(res2d.coefficients) * np.log(len(field.u.flatten()))),
                )
                self.portfolio.register(h2d)

            # Competing physical priors for 2D systems
            if source_tag == "initial":
                if "gray_scott" in field.pde_name:
                    h_diff = ScientificHypothesis(
                        id="hyp_gs_diffusion_only",
                        equation_str="v_t = +0.0800*lap_v",
                        features=["lap_v"],
                        parameters={"lap_v": 0.08},
                        complexity=2,
                        origin="competing_physical_prior",
                        train_mse=0.001,
                        val_mse=0.001,
                        bic=0.0,
                    )
                    self.portfolio.register(h_diff)
                elif "fitzhugh" in field.pde_name:
                    h_diff = ScientificHypothesis(
                        id="hyp_fhn_diffusion_only",
                        equation_str="u_t = +1.0000*lap_u",
                        features=["lap_u"],
                        parameters={"lap_u": 1.0},
                        complexity=2,
                        origin="competing_physical_prior",
                        train_mse=0.001,
                        val_mse=0.001,
                        bic=0.0,
                    )
                    self.portfolio.register(h_diff)
                elif "navier_stokes" in field.pde_name:
                    h_stokes = ScientificHypothesis(
                        id="hyp_stokes_decay_impostor",
                        equation_str="omega_t = +0.0200*lap_omega",
                        features=["lap_omega"],
                        parameters={"lap_omega": 0.02},
                        complexity=2,
                        origin="competing_physical_prior",
                        train_mse=0.001,
                        val_mse=0.001,
                        bic=0.0,
                    )
                    self.portfolio.register(h_stokes)

    def _update_and_validate_hypotheses(
        self, new_field: SpatiotemporalField, experiment_id: str, iteration: int = 1
    ) -> Tuple[List[str], List[str]]:
        """
        Evaluate predictive residual of each active hypothesis on newly acquired observations.
        Also formulates updated hypotheses from the newly acquired data, refits parameters,
        falsifies models whose predictive error exceeds tolerance, and confirms supporting ones.
        """
        falsified = []
        supported = []

        # 1. Formulate updated candidate hypotheses from the newly acquired observations
        self._generate_initial_hypotheses(new_field, source_tag=f"step{iteration}_{experiment_id}")

        active = self.portfolio.get_active()
        if not active:
            return falsified, supported

        errors = {}

        if self.dimension == 1:
            wsindy = WeakFormPDEDiscovery(num_test_functions=60, threshold=0.03, random_seed=self.random_seed)
            G, b, fnames = wsindy.build_weak_form_system(new_field)
            K = len(b)
            var_b = float(np.var(b)) + 1e-12

            for h in active:
                xi = np.zeros(len(fnames), dtype=np.float64)
                for term, coef in h.parameters.items():
                    if term in fnames:
                        xi[fnames.index(term)] = coef
                res_vec = b - G @ xi
                mse = float(np.mean(res_vec ** 2))
                errors[h.id] = mse
                h.val_mse = (h.val_mse + mse) / 2.0 if h.val_mse < 1e5 else mse
                h.bic = float(K * np.log(h.val_mse + 1e-12) + h.complexity * np.log(K))

        else:
            engine2d = WeakForm2DPDEDiscovery(num_test_functions=50, threshold=0.02, random_seed=self.random_seed)
            G, b = engine2d.build_weak_form_system(new_field, self.target_channel, self.candidate_library)
            K = len(b)
            var_b = float(np.var(b)) + 1e-12

            for h in active:
                xi = np.zeros(len(self.candidate_library), dtype=np.float64)
                for term, coef in h.parameters.items():
                    if term in self.candidate_library:
                        xi[self.candidate_library.index(term)] = coef
                res_vec = b - G @ xi
                mse = float(np.mean(res_vec ** 2))
                errors[h.id] = mse
                h.val_mse = (h.val_mse + mse) / 2.0 if h.val_mse < 1e5 else mse
                h.bic = float(K * np.log(h.val_mse + 1e-12) + h.complexity * np.log(K))

        min_mse = min(errors.values())

        # Falsification check: statistical discrimination against top predictive model
        for h in active:
            mse = errors[h.id]
            norm_err = mse / var_b
            if mse > 5.0 * (min_mse + 1e-7) and norm_err > 0.05:
                self.portfolio.record_falsification(
                    h.id, experiment_id, reason=f"Weak-form residual MSE {mse:.6f} exceeded margin vs best {min_mse:.6f}"
                )
                falsified.append(h.id)
            else:
                self.portfolio.record_support(h.id, experiment_id)
                supported.append(h.id)

        return falsified, supported
