"""Alignment obligations and their evaluations."""

from dataclasses import dataclass, field

from .completeness import CompletenessDeclaration
from .identity import stable_id


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
