"""Evidence-backed investigation cases."""

from dataclasses import dataclass, field

from .completeness import CompletenessDeclaration
from .identity import stable_id


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
