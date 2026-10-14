"""Domain-oriented state-comparison port contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from gitdrift.domain import Comparison, RawChange


@dataclass(frozen=True, slots=True)
class DiffOptions:
    """Every supported option that can alter raw comparison output."""

    algorithm: str = "histogram"
    whitespace: str = "retain"
    binary: str = "preserve"
    rename_detection: bool = False
    copy_detection: bool = False
    submodule: str = "short"
    pathspecs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.rename_detection or self.copy_detection:
            raise ValueError(
                "rename and copy detection are not supported "
                "by this deterministic increment"
            )
        for path in self.pathspecs:
            portable = path.replace(chr(92), "/")
            if (
                not portable
                or portable.startswith("/")
                or ".." in portable.split("/")
            ):
                raise ValueError(
                    "diff pathspecs must be workspace-relative"
                )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "algorithm": self.algorithm,
            "whitespace": self.whitespace,
            "binary": self.binary,
            "rename_detection": self.rename_detection,
            "copy_detection": self.copy_detection,
            "submodule": self.submodule,
            "pathspecs": tuple(
                path.replace(chr(92), "/")
                for path in self.pathspecs
            ),
        }


@dataclass(frozen=True, slots=True)
class StateComparisonResult:
    """One executed comparison and its exact raw path changes."""

    comparison: Comparison
    changes: tuple[RawChange, ...]


class StateComparator(Protocol):
    """Read-only repository comparison capability."""

    def compare_head_to_index(
        self,
        *,
        options: DiffOptions = DiffOptions(),
    ) -> StateComparisonResult:
        """Compare captured HEAD with the current captured index."""

    def compare_index_to_working_tree(
        self,
        *,
        options: DiffOptions = DiffOptions(),
    ) -> StateComparisonResult:
        """Compare the captured index with the working tree."""

    def compare_head_to_working_tree(
        self,
        *,
        options: DiffOptions = DiffOptions(),
    ) -> StateComparisonResult:
        """Compare captured HEAD with the cumulative working tree."""
