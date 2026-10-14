"""Evidence-backed bounded investigation cases."""

from dataclasses import dataclass, field

from .completeness import CompletenessDeclaration
from .identity import stable_id


def _nonempty_token(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _unique(values: tuple[str, ...], field_name: str) -> None:
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError(f"{field_name} must contain non-empty identifiers")
    if len(set(values)) != len(values):
        raise ValueError(f"{field_name} must not contain duplicates")


@dataclass(frozen=True, slots=True)
class Case:
    """One bounded question with explicit evidence and uncertainty."""

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
    judgment: str | None = None
    id: str = field(init=False)

    def __post_init__(self) -> None:
        _nonempty_token(self.question, "question")
        _nonempty_token(self.reproduction_id, "reproduction_id")

        collections = {
            "subject_ids": self.subject_ids,
            "observation_ids": self.observation_ids,
            "interpretation_ids": self.interpretation_ids,
            "obligation_ids": self.obligation_ids,
            "evaluation_ids": self.evaluation_ids,
            "assessment_ids": self.assessment_ids,
            "supporting_evidence_ids": self.supporting_evidence_ids,
            "counterevidence_ids": self.counterevidence_ids,
            "evidence_inventory_ids": self.evidence_inventory_ids,
        }
        for name, values in collections.items():
            _unique(values, name)

        if not self.subject_ids:
            raise ValueError("a case requires at least one stable subject")
        if not self.evidence_inventory_ids:
            raise ValueError("a case requires an explicit evidence inventory")

        inventory = set(self.evidence_inventory_ids)
        evidence_references = (
            set(self.observation_ids)
            | set(self.interpretation_ids)
            | set(self.supporting_evidence_ids)
            | set(self.counterevidence_ids)
        )
        missing = sorted(evidence_references - inventory)
        if missing:
            raise ValueError(
                "case evidence references are absent from the inventory: "
                + ", ".join(missing)
            )

        overlap = (
            set(self.supporting_evidence_ids)
            & set(self.counterevidence_ids)
        )
        if overlap:
            raise ValueError(
                "supporting evidence and counterevidence must remain "
                "distinct roles: "
                + ", ".join(sorted(overlap))
            )

        if self.judgment is not None:
            _nonempty_token(self.judgment, "judgment")

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
                    "assessments": sorted(self.assessment_ids),
                    "supporting": sorted(
                        self.supporting_evidence_ids
                    ),
                    "counterevidence": sorted(
                        self.counterevidence_ids
                    ),
                    "alternatives": sorted(self.alternatives),
                    "unknowns": sorted(self.unknowns),
                    "completeness": self.completeness,
                    "reproduction_id": self.reproduction_id,
                    "evidence_inventory": sorted(
                        self.evidence_inventory_ids
                    ),
                    "judgment": self.judgment,
                },
            ),
        )
