"""Repository states and comparisons."""

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
