"""The aggregate investigation record."""

from dataclasses import dataclass, field
from typing import Mapping

from .cases import Case
from .completeness import CompletenessDeclaration, CompletenessDimension
from .evidence import EvidenceReference, Fact
from .obligations import Obligation, ObligationEvaluation
from .states import (
    ArtifactSnapshot,
    Comparison,
    RawChange,
    RepositoryState,
)


@dataclass(frozen=True, slots=True)
class DiagnosticRecord:
    code: str
    severity: str
    category: str
    affected_ids: tuple[str, ...] = ()
    completeness_effects: Mapping[
        CompletenessDimension,
        str,
    ] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReproductionManifest:
    repository_id: str
    state_ids: tuple[str, ...]
    configuration_identity: str
    capability_identity: str
    native_schema_version: str
    producer_version: str
    budgets: Mapping[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Investigation:
    manifest: ReproductionManifest
    states: tuple[RepositoryState, ...] = ()
    comparisons: tuple[Comparison, ...] = ()
    snapshots: tuple[ArtifactSnapshot, ...] = ()
    changes: tuple[RawChange, ...] = ()
    evidence: tuple[EvidenceReference, ...] = ()
    facts: tuple[Fact, ...] = ()
    obligations: tuple[Obligation, ...] = ()
    evaluations: tuple[ObligationEvaluation, ...] = ()
    cases: tuple[Case, ...] = ()
    diagnostics: tuple[DiagnosticRecord, ...] = ()
    completeness: CompletenessDeclaration = field(
        default_factory=lambda: CompletenessDeclaration({})
    )
