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
from nomos.pde.isolation import create_learner_field_observation
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
        self.max_budget = int(max_budget)
        if getattr(self.oracle, "max_budget", None) is None:
            self.oracle.max_budget = self.max_budget
        self.grid = grid
        self.candidate_pool = candidate_experiment_pool
        self.strategy = strategy
        self.noise_level = float(noise_level)
        self.random_seed = int(random_seed)
        self.dimension = int(dimension)
        self.target_channel = target_channel
        if candidate_library is not None:
            self.candidate_library = candidate_library
        elif self.dimension == 2:
            self.candidate_library = ["lap_u", "lap_v", "lap_omega", "u", "v", "u^2", "u^3", "u*v^2", "u^2*v", "1", "advection_omega"]
        else:
            self.candidate_library = ["u*u_x", "u_xx", "u_xxx", "u_xxxx"]

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

        # Stage 0: OBSERVE initial dataset (consumes Query 1 if initial_field is None)
        if initial_field is not None:
            sanitized_field = create_learner_field_observation(initial_field)
            self.observed_fields.append(sanitized_field)
            self._generate_initial_hypotheses(sanitized_field)
        else:
            # Execute first experiment from pool
            init_lbl, init_u0, _ = self.candidate_pool[0]
            req = ExperimentRequest(
                experiment_id=f"exp_{self.oracle.query_count:02d}_{init_lbl}",
                u0=init_u0,
                noise_level=self.noise_level,
                random_seed=self.random_seed,
            )
            resp = self.oracle.execute_experiment(req)
            self.observed_fields.append(resp.field)
            self._generate_initial_hypotheses(resp.field)

        # Audit stopping condition immediately after initialization
        status, winning_h, diag = self.auditor.audit_portfolio(
            self.portfolio, self.oracle.query_count, self.max_budget
        )

        # Iterative Closed-Loop Cycle: bounded strictly by total oracle query budget
        while (
            self.oracle.query_count < self.max_budget
            and status in (IdentifiabilityStatus.MULTIPLE_PLAUSIBLE_LAWS, IdentifiabilityStatus.INSUFFICIENT_EXCITATION)
        ):
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
                iteration_index=self.oracle.query_count,
            )

            # STAGE 3: EXPERIMENT (Strict Oracle Query)
            req = ExperimentRequest(
                experiment_id=f"exp_{self.oracle.query_count:02d}_{chosen_lbl}",
                u0=chosen_u0,
                noise_level=self.noise_level,
                random_seed=self.random_seed + iteration,
            )
            resp = self.oracle.execute_experiment(req)
            self.observed_fields.append(resp.field)

            # STAGE 4: UPDATE & VALIDATE
            falsified, supported = self._update_and_validate_hypotheses(resp.field, req.experiment_id, iteration)

            # STAGE 5: STOPPING AUDIT
            status, winning_h, diag = self.auditor.audit_portfolio(
                self.portfolio, self.oracle.query_count, self.max_budget
            )

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

        if (
            status in (IdentifiabilityStatus.MULTIPLE_PLAUSIBLE_LAWS, IdentifiabilityStatus.INSUFFICIENT_EXCITATION)
            and self.oracle.query_count >= self.max_budget
        ):
            status = IdentifiabilityStatus.BUDGET_EXHAUSTED

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

    def _register_or_update_hypothesis(self, h: ScientificHypothesis):
        """
        Register hypothesis, deduplicating structurally identical models
        by retaining the one with lower validation MSE / BIC.
        """
        feat_key = tuple(sorted(h.parameters.keys()))
        for existing in self.portfolio.get_active():
            if tuple(sorted(existing.parameters.keys())) == feat_key:
                if h.val_mse < existing.val_mse:
                    existing.parameters = h.parameters.copy()
                    existing.equation_str = h.equation_str
                    existing.val_mse = h.val_mse
                    existing.train_mse = h.train_mse
                    existing.bic = h.bic
                return
        self.portfolio.register(h)

    def _generate_initial_hypotheses(self, field: SpatiotemporalField, source_tag: str = "initial"):
        """
        Formulate candidate physical laws using discovery engines without simulator leakage.
        Employs:
        1. Multi-threshold WSINDy (weak-form sparse regression across multiple sparsity thresholds)
        2. Differential Beam Search (scale-adaptive symbolic grammar search in 1D)
        3. Parsimonious sub-model generation (data-derived single-operator sub-models
           fitted directly on the observed trajectory via least-squares projection)
        """
        if self.dimension == 1:
            # 1. Multi-threshold WSINDy discovery
            for thresh in [0.015, 0.045, 0.12]:
                wsindy = WeakFormPDEDiscovery(num_test_functions=80, threshold=thresh, random_seed=self.random_seed)
                res_w = wsindy.fit(field)
                if res_w.coefficients:
                    h_wsindy = ScientificHypothesis(
                        id=f"hyp_wsindy_{'_'.join(sorted(res_w.coefficients.keys()))}",
                        equation_str=res_w.discovered_equation,
                        features=res_w.feature_names,
                        parameters=res_w.coefficients.copy(),
                        complexity=len(res_w.coefficients) * 2,
                        origin=f"wsindy_thresh_{thresh}_{source_tag}",
                        train_mse=res_w.residual_norm**2,
                        val_mse=res_w.residual_norm**2,
                        bic=float(len(field.u.flatten()) * np.log(res_w.residual_norm**2 + 1e-12) + len(res_w.coefficients) * np.log(len(field.u.flatten()))),
                    )
                    self._register_or_update_hypothesis(h_wsindy)

            # 2. Scale-Adaptive Beam Search fit
            beam = DifferentialBeamSearch(scoring_mode="adaptive", complexity_penalty=1e-4, random_seed=self.random_seed)
            res_b = beam.fit(field)
            if res_b.coefficients:
                h_beam = ScientificHypothesis(
                    id=f"hyp_beam_{'_'.join(sorted(res_b.coefficients.keys()))}",
                    equation_str=res_b.discovered_equation,
                    features=res_b.feature_names,
                    parameters=res_b.coefficients.copy(),
                    complexity=len(res_b.coefficients) * 2,
                    origin=f"beam_{source_tag}",
                    train_mse=res_b.residual_norm**2,
                    val_mse=res_b.residual_norm**2,
                    bic=float(len(field.u.flatten()) * np.log(res_b.residual_norm**2 + 1e-12) + len(res_b.coefficients) * np.log(len(field.u.flatten()))),
                )
                self._register_or_update_hypothesis(h_beam)

            # 3. Autonomous Parsimonious Sub-model Proposal (Zero Leakage)
            # Fits single-term candidates directly from weak-form observations using least squares
            ws_base = WeakFormPDEDiscovery(num_test_functions=80, threshold=0.045, random_seed=self.random_seed)
            G, b, fnames = ws_base.build_weak_form_system(field)
            var_b = float(np.var(b)) + 1e-12
            N_pts = len(field.u.flatten())

            for fname in fnames:
                idx = fnames.index(fname)
                col = G[:, idx]
                denom = float(np.dot(col, col))
                if denom > 1e-12:
                    coef = float(np.dot(col, b) / denom)
                    if abs(coef) > 1e-4:
                        res = b - coef * col
                        mse = float(np.mean(res**2))
                        if mse / var_b < 0.85:
                            eq_str = f"u_t = {coef:+.4f}*{fname}"
                            h_sub = ScientificHypothesis(
                                id=f"hyp_sub_{fname}",
                                equation_str=eq_str,
                                features=[fname],
                                parameters={fname: coef},
                                complexity=2,
                                origin=f"parsimonious_submodel_{source_tag}",
                                train_mse=mse,
                                val_mse=mse,
                                bic=float(N_pts * np.log(mse + 1e-12) + 2 * np.log(N_pts)),
                            )
                            self._register_or_update_hypothesis(h_sub)

        else:
            # 2D Field Hypothesis Generation via Multi-Threshold WSINDy-2D
            for thresh in [0.015, 0.045, 0.12]:
                engine2d = WeakForm2DPDEDiscovery(num_test_functions=70, threshold=thresh, random_seed=self.random_seed)
                res2d = engine2d.fit_channel(field, self.target_channel, self.candidate_library)
                if res2d.coefficients:
                    h2d = ScientificHypothesis(
                        id=f"hyp_wsindy2d_{'_'.join(sorted(res2d.coefficients.keys()))}",
                        equation_str=res2d.discovered_equation,
                        features=res2d.feature_names,
                        parameters=res2d.coefficients.copy(),
                        complexity=len(res2d.coefficients) * 2,
                        origin=f"wsindy2d_thresh_{thresh}_{source_tag}",
                        train_mse=res2d.residual_norm**2,
                        val_mse=res2d.residual_norm**2,
                        bic=float(len(field.u.flatten()) * np.log(res2d.residual_norm**2 + 1e-12) + len(res2d.coefficients) * np.log(len(field.u.flatten()))),
                    )
                    self._register_or_update_hypothesis(h2d)

            # Autonomous Parsimonious Sub-models for 2D
            engine2d_base = WeakForm2DPDEDiscovery(num_test_functions=70, threshold=0.045, random_seed=self.random_seed)
            G, b = engine2d_base.build_weak_form_system(field, self.target_channel, self.candidate_library)
            var_b = float(np.var(b)) + 1e-12
            N_pts = len(field.u.flatten())

            for idx, cand in enumerate(self.candidate_library):
                col = G[:, idx]
                denom = float(np.dot(col, col))
                if denom > 1e-12:
                    coef = float(np.dot(col, b) / denom)
                    if abs(coef) > 1e-4:
                        res = b - coef * col
                        mse = float(np.mean(res**2))
                        if mse / var_b < 0.85:
                            eq_str = f"{self.target_channel}_t = {coef:+.4f}*{cand}"
                            h_sub2d = ScientificHypothesis(
                                id=f"hyp_sub2d_{cand}",
                                equation_str=eq_str,
                                features=[cand],
                                parameters={cand: coef},
                                complexity=2,
                                origin=f"parsimonious_submodel_{source_tag}",
                                train_mse=mse,
                                val_mse=mse,
                                bic=float(N_pts * np.log(mse + 1e-12) + 2 * np.log(N_pts)),
                            )
                            self._register_or_update_hypothesis(h_sub2d)

    def _update_and_validate_hypotheses(
        self, new_field: SpatiotemporalField, experiment_id: str, iteration: int = 1
    ) -> Tuple[List[str], List[str]]:
        """
        Evaluate predictive residual of each active hypothesis across ALL observed fields
        to enforce universal law invariance. Also proposes updated hypotheses from new observations.
        """
        falsified = []
        supported = []

        # 1. Propose candidate hypotheses from newly acquired observations
        self._generate_initial_hypotheses(new_field, source_tag=f"step{iteration}_{experiment_id}")

        active = self.portfolio.get_active()
        if not active:
            return falsified, supported

        if self.dimension == 1:
            wsindy = WeakFormPDEDiscovery(num_test_functions=60, threshold=0.03, random_seed=self.random_seed)
            field_systems = []
            for f in self.observed_fields:
                G_f, b_f, fnames_f = wsindy.build_weak_form_system(f)
                var_f = float(np.var(b_f)) + 1e-12
                field_systems.append((G_f, b_f, fnames_f, var_f))

            for h in active:
                field_mses = []
                is_falsified = False
                reasons = []

                for idx_f, (G_f, b_f, fnames_f, var_f) in enumerate(field_systems):
                    xi = np.zeros(len(fnames_f), dtype=np.float64)
                    for term, coef in h.parameters.items():
                        if term in fnames_f:
                            xi[fnames_f.index(term)] = coef
                    res_vec = b_f - G_f @ xi
                    mse_f = float(np.mean(res_vec ** 2))
                    norm_err_f = mse_f / var_f
                    field_mses.append(mse_f)

                    if norm_err_f > 0.05 and mse_f > 1e-4:
                        is_falsified = True
                        reasons.append(f"field_{idx_f} rel_err={norm_err_f:.4f}")

                mean_mse = float(np.mean(field_mses))
                h.val_mse = mean_mse
                K_total = sum(len(b_f) for _, b_f, _, _ in field_systems)
                h.bic = float(K_total * np.log(mean_mse + 1e-12) + h.complexity * np.log(K_total))

                if is_falsified:
                    self.portfolio.record_falsification(
                        h.id, experiment_id, reason="; ".join(reasons)
                    )
                    falsified.append(h.id)
                else:
                    self.portfolio.record_support(h.id, experiment_id)
                    supported.append(h.id)

        else:
            engine2d = WeakForm2DPDEDiscovery(num_test_functions=50, threshold=0.02, random_seed=self.random_seed)
            field_systems = []
            for f in self.observed_fields:
                G_f, b_f = engine2d.build_weak_form_system(f, self.target_channel, self.candidate_library)
                var_f = float(np.var(b_f)) + 1e-12
                field_systems.append((G_f, b_f, var_f))

            for h in active:
                field_mses = []
                is_falsified = False
                reasons = []

                for idx_f, (G_f, b_f, var_f) in enumerate(field_systems):
                    xi = np.zeros(len(self.candidate_library), dtype=np.float64)
                    for term, coef in h.parameters.items():
                        if term in self.candidate_library:
                            xi[self.candidate_library.index(term)] = coef
                    res_vec = b_f - G_f @ xi
                    mse_f = float(np.mean(res_vec ** 2))
                    norm_err_f = mse_f / var_f
                    field_mses.append(mse_f)

                    if norm_err_f > 0.05 and mse_f > 1e-4:
                        is_falsified = True
                        reasons.append(f"field_{idx_f} rel_err={norm_err_f:.4f}")

                mean_mse = float(np.mean(field_mses))
                h.val_mse = mean_mse
                K_total = sum(len(b_f) for _, b_f, _ in field_systems)
                h.bic = float(K_total * np.log(mean_mse + 1e-12) + h.complexity * np.log(K_total))

                if is_falsified:
                    self.portfolio.record_falsification(
                        h.id, experiment_id, reason="; ".join(reasons)
                    )
                    falsified.append(h.id)
                else:
                    self.portfolio.record_support(h.id, experiment_id)
                    supported.append(h.id)

        return falsified, supported
