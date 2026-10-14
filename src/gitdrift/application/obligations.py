"""Deterministic evaluation of explicitly supplied obligations."""
from __future__ import annotations

from gitdrift.domain import (
    CompletenessDeclaration,
    CompletenessDimension,
    DiagnosticRecord,
    Obligation,
    ObligationEvaluation,
)
from gitdrift.ports.obligations import (
    ObligationEvaluationRequest,
    ObligationEvaluationResult,
)


def _evaluation(
    request: ObligationEvaluationRequest,
    obligation: Obligation,
    evidence_ids: tuple[str, ...],
    counterevidence_ids: tuple[str, ...],
    value: str,
    questions: tuple[str, ...] = (),
) -> ObligationEvaluation:
    return ObligationEvaluation(
        obligation_id=obligation.id,
        state_id=request.state_id,
        value=value,
        evidence_ids=evidence_ids,
        counterevidence_ids=counterevidence_ids,
        completeness=request.completeness,
        unresolved_questions=questions,
    )


class DeterministicObligationEvaluator:
    """Evaluate bounded existence relations without inferred authority."""

    def evaluate(
        self,
        request: ObligationEvaluationRequest,
    ) -> ObligationEvaluationResult:
        evidence_by_id = {item.id: item for item in request.evidence}
        facts_by_subject: dict[str, list[str]] = {}
        for fact in request.facts:
            if fact.state_id != request.state_id:
                continue
            facts_by_subject.setdefault(fact.subject, []).append(fact.id)

        evaluations: list[ObligationEvaluation] = []
        diagnostics: list[DiagnosticRecord] = list(
            request.obligation_set.diagnostics
        )

        for obligation in request.obligation_set.obligations:
            authority_ids = tuple(
                item
                for item in obligation.authority_evidence_ids
                if item in evidence_by_id
            )
            missing_authority = tuple(
                item
                for item in obligation.authority_evidence_ids
                if item not in evidence_by_id
            )
            subject_fact_ids = tuple(
                sorted(
                    fact_id
                    for subject in obligation.subject_ids
                    for fact_id in facts_by_subject.get(subject, ())
                )
            )
            search_complete = (
                request.completeness.values.get(
                    CompletenessDimension.SEMANTIC_EXTRACTION
                )
                == "complete"
                and request.completeness.values.get(
                    CompletenessDimension.OBLIGATION_COVERAGE
                )
                == "complete"
            )

            if missing_authority:
                questions = (
                    "Which explicit authority evidence resolves: "
                    + ", ".join(missing_authority)
                    + "?",
                )
                evaluations.append(
                    _evaluation(
                        request,
                        obligation,
                        authority_ids,
                        subject_fact_ids,
                        "unresolved",
                        questions,
                    )
                )
                diagnostics.append(
                    DiagnosticRecord(
                        code="GD-OBLIGATION-AUTHORITY-UNRESOLVED",
                        severity="warning",
                        category="evidence-unavailable",
                        affected_ids=(
                            obligation.id,
                            *missing_authority,
                        ),
                        completeness_effects={
                            CompletenessDimension.OBLIGATION_COVERAGE:
                            "partial"
                        },
                    )
                )
                continue

            inactive = obligation.activation == "inactive"
            retired = obligation.retirement == "retired"
            if inactive or retired:
                evaluations.append(
                    _evaluation(
                        request,
                        obligation,
                        authority_ids,
                        (),
                        "not-applicable",
                    )
                )
                continue

            if obligation.relation == "exists":
                if subject_fact_ids:
                    value = "satisfied"
                    questions = ()
                elif search_complete:
                    value = "absent"
                    questions = ()
                else:
                    value = "unresolved"
                    questions = (
                        "Is the required subject absent, or is semantic "
                        "coverage incomplete?",
                    )
                evaluations.append(
                    _evaluation(
                        request,
                        obligation,
                        authority_ids + subject_fact_ids,
                        (),
                        value,
                        questions,
                    )
                )
                continue

            if obligation.relation == "does-not-exist":
                if subject_fact_ids:
                    value = "violated"
                    questions = ()
                elif search_complete:
                    value = "satisfied"
                    questions = ()
                else:
                    value = "unresolved"
                    questions = (
                        "Is the prohibited subject absent, or is semantic "
                        "coverage incomplete?",
                    )
                evaluations.append(
                    _evaluation(
                        request,
                        obligation,
                        authority_ids,
                        subject_fact_ids,
                        value,
                        questions,
                    )
                )
                continue

            evaluations.append(
                _evaluation(
                    request,
                    obligation,
                    authority_ids,
                    subject_fact_ids,
                    "unresolved",
                    (
                        "No accepted deterministic evaluator is installed "
                        f"for relation {obligation.relation!r}.",
                    ),
                )
            )
            diagnostics.append(
                DiagnosticRecord(
                    code="GD-OBLIGATION-RELATION-UNRESOLVED",
                    severity="warning",
                    category="unsupported-capability",
                    affected_ids=(obligation.id,),
                    completeness_effects={
                        CompletenessDimension.OBLIGATION_COVERAGE:
                        "partial"
                    },
                )
            )

        completeness_values = dict(request.completeness.values)
        if any(
            evaluation.value == "unresolved"
            for evaluation in evaluations
        ):
            current = completeness_values.get(
                CompletenessDimension.OBLIGATION_COVERAGE
            )
            if current == "complete":
                completeness_values[
                    CompletenessDimension.OBLIGATION_COVERAGE
                ] = "partial"

        return ObligationEvaluationResult(
            obligation_set_identity=request.obligation_set.identity,
            evaluations=tuple(evaluations),
            diagnostics=tuple(diagnostics),
            completeness=CompletenessDeclaration(
                completeness_values,
                limitations=request.completeness.limitations,
            ),
        )


def evaluate_obligations(
    request: ObligationEvaluationRequest,
) -> ObligationEvaluationResult:
    """Evaluate explicit obligations through the deterministic evaluator."""

    return DeterministicObligationEvaluator().evaluate(request)
