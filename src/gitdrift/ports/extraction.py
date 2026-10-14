"""Domain-oriented semantic extraction contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from gitdrift.domain import (
    CompletenessDeclaration,
    DiagnosticRecord,
    EvidenceReference,
    Fact,
    stable_id,
)


class ArtifactKind(StrEnum):
    """Artifact kinds accepted by implemented extractors."""

    MARKDOWN = "markdown"
    PYTHON = "python"
    UNSUPPORTED = "unsupported"


class ExtractorDeterminism(StrEnum):
    """Declared extractor determinism class."""

    DETERMINISTIC = "deterministic"


class ExtractorCost(StrEnum):
    """Declared bounded cost classification."""

    LINEAR = "linear"


@dataclass(frozen=True, slots=True)
class ExtractorCapability:
    """Stable declaration of one installed extractor capability."""

    extractor_id: str
    version: str
    accepted_artifact_kinds: tuple[ArtifactKind, ...]
    produced_fact_kinds: tuple[str, ...]
    determinism: ExtractorDeterminism
    cost: ExtractorCost
    configuration_schema_id: str
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ExtractionInput:
    """Exact artifact evidence supplied to an extractor."""

    state_id: str
    path: str
    artifact_kind: ArtifactKind
    payload: bytes
    evidence: EvidenceReference
    configuration_identity: str
    id: str = field(init=False)

    def __post_init__(self) -> None:
        normalized = self.path.replace(chr(92), "/")
        if (
            not normalized
            or normalized.startswith("/")
            or ".." in normalized.split("/")
        ):
            raise ValueError(
                "extraction input path must be workspace-relative"
            )

        if self.evidence.subject_id != self.state_id:
            raise ValueError(
                "input evidence subject must identify the input state"
            )

        object.__setattr__(self, "path", normalized)
        object.__setattr__(
            self,
            "id",
            stable_id(
                "extraction-input",
                {
                    "state_id": self.state_id,
                    "path": normalized,
                    "artifact_kind": self.artifact_kind,
                    "payload": self.payload,
                    "evidence_id": self.evidence.id,
                    "configuration_identity": (
                        self.configuration_identity
                    ),
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class ExtractedFragment:
    """One bounded extractor-owned artifact fragment."""

    extraction_input_id: str
    kind: str
    address: str
    heading_level: int
    heading: str
    parent_address: str | None
    start_line: int
    end_line: int
    content_identity: str
    fact_id: str
    id: str = field(init=False)

    def __post_init__(self) -> None:
        if self.start_line < 1 or self.end_line < self.start_line:
            raise ValueError("fragment line range is invalid")
        if not 1 <= self.heading_level <= 6:
            raise ValueError("Markdown heading level must be 1 through 6")

        object.__setattr__(
            self,
            "id",
            stable_id(
                "fragment",
                {
                    "extraction_input_id": self.extraction_input_id,
                    "kind": self.kind,
                    "address": self.address,
                    "heading_level": self.heading_level,
                    "heading": self.heading,
                    "parent_address": self.parent_address,
                    "start_line": self.start_line,
                    "end_line": self.end_line,
                    "content_identity": self.content_identity,
                    "fact_id": self.fact_id,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """Facts and fragments produced from one exact input."""

    capability: ExtractorCapability
    extraction_input: ExtractionInput
    fragments: tuple[ExtractedFragment, ...]
    facts: tuple[Fact, ...]
    diagnostics: tuple[DiagnosticRecord, ...]
    completeness: CompletenessDeclaration


class FactExtractor(Protocol):
    """Read-only extraction over explicit exact artifact evidence."""

    @property
    def capability(self) -> ExtractorCapability:
        """Declare the stable installed extractor capability."""

    def extract(self, request: ExtractionInput) -> ExtractionResult:
        """Extract supported facts without mutating input evidence."""
