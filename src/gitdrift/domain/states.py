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
    """Exact path-level evidence from one configured comparison."""

    comparison_id: str
    status: str
    source_path: str | None
    destination_path: str | None
    source_identity: str | None = None
    destination_identity: str | None = None
    source_mode: str | None = None
    destination_mode: str | None = None
    patch_identity: str | None = None
    binary_treatment: str | None = None
    rename_or_copy_score: int | None = None
    rename_or_copy_method: str | None = None
    submodule_identity: str | None = None
    diff_options: Mapping[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    id: str = field(init=False)

    def __post_init__(self) -> None:
        allowed_statuses = {
            "addition",
            "deletion",
            "modification",
            "type-change",
            "rename-candidate",
            "copy-candidate",
            "unmerged",
            "unsupported",
        }
        if self.status not in allowed_statuses:
            raise ValueError(f"unsupported raw-change status: {self.status}")

        normalized_source = self._normalized_path(
            self.source_path,
            field_name="source_path",
        )
        normalized_destination = self._normalized_path(
            self.destination_path,
            field_name="destination_path",
        )

        if self.status == "addition" and normalized_destination is None:
            raise ValueError("addition requires a destination path")
        if self.status == "deletion" and normalized_source is None:
            raise ValueError("deletion requires a source path")
        if normalized_source is None and normalized_destination is None:
            raise ValueError(
                "raw change requires a source or destination path"
            )
        if self.status in {"rename-candidate", "copy-candidate"}:
            if (
                normalized_source is None
                or normalized_destination is None
            ):
                raise ValueError(
                    f"{self.status} requires both endpoint paths"
                )
            if self.rename_or_copy_score is None:
                raise ValueError(
                    f"{self.status} requires an explicit score"
                )
            if not self.rename_or_copy_method:
                raise ValueError(
                    f"{self.status} requires an explicit method"
                )

        if self.rename_or_copy_score is not None:
            if not 0 <= self.rename_or_copy_score <= 100:
                raise ValueError(
                    "rename or copy score must be between 0 and 100"
                )
            if self.status not in {
                "rename-candidate",
                "copy-candidate",
            }:
                raise ValueError(
                    "rename or copy score requires a candidate status"
                )

        if (
            self.rename_or_copy_method is not None
            and self.status
            not in {"rename-candidate", "copy-candidate"}
        ):
            raise ValueError(
                "rename or copy method requires a candidate status"
            )

        object.__setattr__(self, "source_path", normalized_source)
        object.__setattr__(
            self,
            "destination_path",
            normalized_destination,
        )
        object.__setattr__(
            self,
            "id",
            stable_id(
                "change",
                {
                    "comparison_id": self.comparison_id,
                    "status": self.status,
                    "source_path": normalized_source,
                    "destination_path": normalized_destination,
                    "source_identity": self.source_identity,
                    "destination_identity": (
                        self.destination_identity
                    ),
                    "source_mode": self.source_mode,
                    "destination_mode": self.destination_mode,
                    "patch_identity": self.patch_identity,
                    "binary_treatment": self.binary_treatment,
                    "rename_or_copy_score": (
                        self.rename_or_copy_score
                    ),
                    "rename_or_copy_method": (
                        self.rename_or_copy_method
                    ),
                    "submodule_identity": self.submodule_identity,
                    "diff_options": self.diff_options,
                    "limitations": self.limitations,
                },
            ),
        )

    @staticmethod
    def _normalized_path(
        value: str | None,
        *,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None
        normalized = value.replace(chr(92), "/")
        if (
            not normalized
            or normalized.startswith("/")
            or ".." in normalized.split("/")
        ):
            raise ValueError(
                f"{field_name} must be workspace-relative"
            )
        return normalized
