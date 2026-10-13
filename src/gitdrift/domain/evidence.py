"""Evidence and semantic facts."""

from dataclasses import dataclass, field
from enum import StrEnum

from .identity import stable_id


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
