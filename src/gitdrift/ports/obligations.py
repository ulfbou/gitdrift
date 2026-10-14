"""Domain-owned contracts for explicit obligation loading and evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from gitdrift.domain import (
    CompletenessDeclaration,
    DiagnosticRecord,
    EvidenceReference,
    Fact,
    Obligation,
    ObligationEvaluation,
)


@dataclass(frozen=True, slots=True)
class ObligationSet:
    """One validated explicit obligation set with retained source evidence."""

    schema: str
    identity: str
    source_evidence: EvidenceReference
    obligations: tuple[Obligation, ...]
    diagnostics: tuple[DiagnosticRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class ObligationEvaluationRequest:
    """Exact deterministic inputs for evaluating explicit obligations."""

    obligation_set: ObligationSet
    state_id: str
    facts: tuple[Fact, ...]
    evidence: tuple[EvidenceReference, ...]
    completeness: CompletenessDeclaration


@dataclass(frozen=True, slots=True)
class ObligationEvaluationResult:
    """Evaluations with truthful diagnostics and completeness."""

    obligation_set_identity: str
    evaluations: tuple[ObligationEvaluation, ...]
    diagnostics: tuple[DiagnosticRecord, ...]
    completeness: CompletenessDeclaration


class ObligationSetLoader(Protocol):
    """Load obligations only from an explicitly supplied exact payload."""

    def load(
        self,
        payload: bytes,
        *,
        source_evidence: EvidenceReference,
    ) -> ObligationSet:
        """Validate and load one explicit obligation set."""


class ObligationEvaluator(Protocol):
    """Evaluate explicit obligations without inferring authority."""

    def evaluate(
        self,
        request: ObligationEvaluationRequest,
    ) -> ObligationEvaluationResult:
        """Evaluate the supplied obligation set deterministically."""
