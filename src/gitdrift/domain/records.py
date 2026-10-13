"""Immutable records for the Gitdrift 0.1 investigation boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from .identity import stable_id


class StateKind(StrEnum):
    COMMIT = "commit"
    BRANCH_TIP = "branch-tip"
    INDEX = "index"
    WORKING_TREE = "working-tree"
    EXPLICIT_SNAPSHOT = "explicit-snapshot"
    SYNTHETIC_COMPARISON = "synthetic-comparison"


class EvidenceClass(StrEnum):
    OBSERVED = "observed"
    COMPUTED = "computed"
    HEURISTIC = "heuristic"
    AI_ASSISTED = "ai-assisted"
    HUMAN_SUPPLIED = "human-supplied"


class DerivationClass(StrEnum):
    DETERMINISTIC = "deterministic"
    HEURISTIC = "heuristic"
    AI_ASSISTED = "ai-assisted"
    HUMAN_SUPPLIED = "human-supplied"


class CompletenessDimension(StrEnum):
    GRAPH_TRAVERSAL = "graph-traversal"
    SELECTED_REFS = "selected-refs"
    STATE_CAPTURE = "state-capture"
    ARTIFACT_COVERAGE = "artifact-coverage"
    LINEAGE_RESOLUTION = "lineage-resolution"
    SEMANTIC_EXTRACTION = "semantic-extraction"
    OBLIGATION_COVERAGE = "obligation-coverage"
    COUNTEREVIDENCE_SEARCH = "counterevidence-search"
    EXTERNAL_CONTEXT = "external-context"


_COMPLETENESS_RANK = {
    "unavailable": 0,
    "partial": 1,
    "complete": 2,
}


@dataclass(frozen=True, slots=True)
class CompletenessDeclaration:
    values: Mapping[CompletenessDimension, str]
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        allowed = {
            "complete",
            "partial",
            "unavailable",
            "not-requested",
            "not-applicable",
        }
        if set(self.values.values()) - allowed:
            raise ValueError("unknown completeness value")

    def no_stronger_than(
        self,
        child: "CompletenessDeclaration",
    ) -> bool:
        for dimension, child_value in child.values.items():
            parent_value = self.values.get(dimension)
            if parent_value is None:
                continue
            if (
                child_value in _COMPLETENESS_RANK
                and parent_value in _COMPLETENESS_RANK
            ):
                if (
                    _COMPLETENESS_RANK[parent_value]
                    > _COMPLETENESS_RANK[child_value]
                ):
                    return False
            elif parent_value != child_value:
                return False
        return True


@dataclass(frozen=True, slots=True)
class RepositoryState:
    kind: StateKind
    repository_id: str
    content_identity: str
    locators: tuple[str, ...] = ()
    base_state_id: str | None = None
    limitations: tuple[str, ...] = ()
    id: str = field(init=False)

    def __post_init__(self) -> None:
        identity = stable_id(
            "state",
            {
                "kind": self.kind,
                "repository_id": self.repository_id,
                "content_identity": self.content_identity,
                "base_state_id": self.base_state_id,
            },
        )
        object.__setattr__(self, "id", identity)


@dataclass(frozen=True, slots=True)
class Comparison:
    left_state_id: str
    right_state_id: str
    kind: str
    question: str
    diff_options: Mapping[str, Any]
    ancestry_established: bool = False
    limitations: tuple[str, ...] = ()
    id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            stable_id(
                "comparison",
                {
                    "left": self.left_state_id,
                    "right": self.right_state_id,
                    "kind": self.kind,
                    "diff_options": self.diff_options,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class ArtifactSnapshot:
    state_id: str
    path: str
    content_identity: str
    mode: str | None = None
    evidence_id: str | None = None
    id: str = field(init=False)

    def __post_init__(self) -> None:
        normalized_path = self.path.replace(chr(92), "/")
        if (
            normalized_path.startswith("/")
            or ".." in normalized_path.split("/")
        ):
            raise ValueError(
                "artifact path must be workspace-relative"
            )

        object.__setattr__(
            self,
            "id",
            stable_id(
                "snapshot",
                {
                    "state_id": self.state_id,
                    "path": normalized_path,
                    "content_identity": self.content_identity,
                    "mode": self.mode,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class RawChange:
    comparison_id: str
    status: str
    source_path: str | None
    destination_path: str | None
    source_identity: str | None = None
    destination_identity: str | None = None
    limitations: tuple[str, ...] = ()
    id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            stable_id(
                "change",
                {
                    "comparison_id": self.comparison_id,
                    "status": self.status,
                    "source_path": self.source_path,
                    "destination_path": self.destination_path,
                    "source_identity": self.source_identity,
                    "destination_identity": self.destination_identity,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    evidence_class: EvidenceClass
    producer: str
    producer_version: str
    subject_id: str
    payload_identity: str
    input_evidence_ids: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            stable_id(
                "evidence",
                {
                    "class": self.evidence_class,
                    "producer": self.producer,
                    "producer_version": self.producer_version,
                    "subject_id": self.subject_id,
                    "payload_identity": self.payload_identity,
                    "inputs": sorted(self.input_evidence_ids),
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class Fact:
    subject: str
    assertion: str
    state_id: str
    producer: str
    producer_version: str
    method: str
    derivation_class: DerivationClass
    confidence_class: str
    input_evidence_ids: tuple[str, ...]
    limitations: tuple[str, ...] = ()
    id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            stable_id(
                "fact",
                {
                    "subject": self.subject,
                    "assertion": self.assertion,
                    "state_id": self.state_id,
                    "producer": self.producer,
                    "producer_version": self.producer_version,
                    "method": self.method,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class Obligation:
    subject_ids: tuple[str, ...]
    relation: str
    authority_evidence_ids: tuple[str, ...]
    scope: str
    activation: str
    retirement: str | None = None
    supersession_rules: tuple[str, ...] = ()
    id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            stable_id(
                "obligation",
                {
                    "subjects": sorted(self.subject_ids),
                    "relation": self.relation,
                    "authorities": sorted(
                        self.authority_evidence_ids
                    ),
                    "scope": self.scope,
                    "activation": self.activation,
                    "retirement": self.retirement,
                    "supersession_rules": sorted(
                        self.supersession_rules
                    ),
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class ObligationEvaluation:
    obligation_id: str
    state_id: str
    value: str
    evidence_ids: tuple[str, ...]
    counterevidence_ids: tuple[str, ...]
    completeness: CompletenessDeclaration
    unresolved_questions: tuple[str, ...] = ()
    id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            stable_id(
                "evaluation",
                {
                    "obligation_id": self.obligation_id,
                    "state_id": self.state_id,
                    "value": self.value,
                    "evidence_ids": sorted(self.evidence_ids),
                    "counterevidence_ids": sorted(
                        self.counterevidence_ids
                    ),
                    "completeness": self.completeness,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class Case:
    question: str
    subject_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    interpretation_ids: tuple[str, ...]
    obligation_ids: tuple[str, ...]
    evaluation_ids: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]
    counterevidence_ids: tuple[str, ...]
    alternatives: tuple[str, ...]
    unknowns: tuple[str, ...]
    completeness: CompletenessDeclaration
    judgment: str | None = None
    id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            stable_id(
                "case",
                {
                    "question": self.question,
                    "subjects": sorted(self.subject_ids),
                    "observations": sorted(self.observation_ids),
                    "interpretations": sorted(
                        self.interpretation_ids
                    ),
                    "obligations": sorted(self.obligation_ids),
                    "evaluations": sorted(self.evaluation_ids),
                    "supporting": sorted(
                        self.supporting_evidence_ids
                    ),
                    "counterevidence": sorted(
                        self.counterevidence_ids
                    ),
                    "alternatives": sorted(self.alternatives),
                    "unknowns": sorted(self.unknowns),
                    "completeness": self.completeness,
                    "judgment": self.judgment,
                },
            ),
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
