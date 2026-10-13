"""Completeness declarations for investigation coverage."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


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
