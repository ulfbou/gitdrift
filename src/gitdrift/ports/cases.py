"""Domain-owned contracts for bounded case construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from gitdrift.domain import Case, CompletenessDeclaration


@dataclass(frozen=True, slots=True)
class CaseConstructionRequest:
    """Explicit records and boundaries supplied to one case build."""

    question: str
    subject_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    interpretation_ids: tuple[str, ...]
    obligation_ids: tuple[str, ...]
    evaluation_ids: tuple[str, ...]
    assessment_ids: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]
    counterevidence_ids: tuple[str, ...]
    alternatives: tuple[str, ...]
    unknowns: tuple[str, ...]
    completeness: CompletenessDeclaration
    reproduction_id: str
    evidence_inventory_ids: tuple[str, ...]
    available_record_ids: frozenset[str]
    judgment: str | None = None


@dataclass(frozen=True, slots=True)
class CaseConstructionResult:
    """A deterministic bounded case and retained unresolved state."""

    case: Case
    unresolved: bool


class CaseBuilder(Protocol):
    """Construct cases without inferring evidence, authority, or judgment."""

    def build(
        self,
        request: CaseConstructionRequest,
    ) -> CaseConstructionResult:
        """Construct one bounded case from explicit referenced records."""
