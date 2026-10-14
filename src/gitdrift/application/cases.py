"""Deterministic construction of bounded evidence-complete cases."""

from __future__ import annotations

from gitdrift.domain import Case
from gitdrift.ports.cases import (
    CaseConstructionRequest,
    CaseConstructionResult,
)


def _referenced_ids(
    request: CaseConstructionRequest,
) -> frozenset[str]:
    return frozenset(
        (
            *request.subject_ids,
            *request.observation_ids,
            *request.interpretation_ids,
            *request.obligation_ids,
            *request.evaluation_ids,
            *request.assessment_ids,
            *request.supporting_evidence_ids,
            *request.counterevidence_ids,
            request.reproduction_id,
            *request.evidence_inventory_ids,
        )
    )


class DeterministicCaseBuilder:
    """Build only from explicit records and preserve ambiguity."""

    def build(
        self,
        request: CaseConstructionRequest,
    ) -> CaseConstructionResult:
        missing = sorted(
            _referenced_ids(request) - request.available_record_ids
        )
        if missing:
            raise ValueError(
                "case references unavailable records: "
                + ", ".join(missing)
            )

        if request.judgment is not None and request.unknowns:
            raise ValueError(
                "a case with unresolved unknowns cannot carry judgment"
            )

        case = Case(
            question=request.question,
            subject_ids=request.subject_ids,
            observation_ids=request.observation_ids,
            interpretation_ids=request.interpretation_ids,
            obligation_ids=request.obligation_ids,
            evaluation_ids=request.evaluation_ids,
            assessment_ids=request.assessment_ids,
            supporting_evidence_ids=request.supporting_evidence_ids,
            counterevidence_ids=request.counterevidence_ids,
            alternatives=request.alternatives,
            unknowns=request.unknowns,
            completeness=request.completeness,
            reproduction_id=request.reproduction_id,
            evidence_inventory_ids=request.evidence_inventory_ids,
            judgment=request.judgment,
        )
        return CaseConstructionResult(
            case=case,
            unresolved=bool(case.unknowns) or case.judgment is None,
        )


def build_case(
    request: CaseConstructionRequest,
) -> CaseConstructionResult:
    """Construct one bounded case through the deterministic builder."""

    return DeterministicCaseBuilder().build(request)
