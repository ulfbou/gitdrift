"""Required state-comparison matrix contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping

from .identity import stable_id
from .states import RepositoryState, StateKind


class MatrixEntryStatus(StrEnum):
    """Availability of one declared state-comparison row."""

    REQUIRED = "required"
    UNAVAILABLE = "unavailable"


class ComparisonKind(StrEnum):
    """Canonical comparison kinds in the state-awareness matrix."""

    HEAD_TO_INDEX = "head-to-index"
    INDEX_TO_WORKTREE = "index-to-worktree"
    HEAD_TO_WORKTREE = "head-to-worktree"
    HEAD_AND_UPSTREAM = "head-and-upstream"


@dataclass(frozen=True, slots=True)
class StateComparisonRow:
    """One required comparison, whether or not both endpoints exist."""

    kind: ComparisonKind
    question: str
    left_state_kind: StateKind
    right_state_kind: StateKind
    left_state_id: str | None
    right_state_id: str | None
    status: MatrixEntryStatus
    limitations: tuple[str, ...] = ()
    id: str = field(init=False)

    def __post_init__(self) -> None:
        endpoints_available = (
            self.left_state_id is not None
            and self.right_state_id is not None
        )
        if self.status is MatrixEntryStatus.REQUIRED:
            if not endpoints_available:
                raise ValueError(
                    "required comparison rows need both endpoint identities"
                )
        elif endpoints_available:
            raise ValueError(
                "available comparison endpoints cannot be marked unavailable"
            )

        object.__setattr__(
            self,
            "id",
            stable_id(
                "comparison-matrix-row",
                {
                    "kind": self.kind,
                    "question": self.question,
                    "left_state_kind": self.left_state_kind,
                    "right_state_kind": self.right_state_kind,
                    "left_state_id": self.left_state_id,
                    "right_state_id": self.right_state_id,
                    "status": self.status,
                    "limitations": self.limitations,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class StateComparisonMatrix:
    """The complete required matrix for the selected captured states."""

    rows: tuple[StateComparisonRow, ...]
    id: str = field(init=False)

    def __post_init__(self) -> None:
        kinds = tuple(row.kind for row in self.rows)
        expected = tuple(ComparisonKind)
        if kinds != expected:
            raise ValueError(
                "state comparison matrix must contain every required row "
                "in canonical order"
            )
        object.__setattr__(
            self,
            "id",
            stable_id(
                "state-comparison-matrix",
                {"row_ids": tuple(row.id for row in self.rows)},
            ),
        )


_ROW_CONTRACTS = (
    (
        ComparisonKind.HEAD_TO_INDEX,
        "What is staged relative to the captured HEAD state?",
        StateKind.COMMIT,
        StateKind.INDEX,
    ),
    (
        ComparisonKind.INDEX_TO_WORKTREE,
        "What differs from the captured index in the working tree?",
        StateKind.INDEX,
        StateKind.WORKING_TREE,
    ),
    (
        ComparisonKind.HEAD_TO_WORKTREE,
        "What is the cumulative local difference from HEAD?",
        StateKind.COMMIT,
        StateKind.WORKING_TREE,
    ),
    (
        ComparisonKind.HEAD_AND_UPSTREAM,
        "How do captured HEAD and upstream states relate?",
        StateKind.COMMIT,
        StateKind.BRANCH_TIP,
    ),
)


def construct_required_comparison_matrix(
    states: Mapping[StateKind, RepositoryState],
) -> StateComparisonMatrix:
    """Represent all required rows without inventing missing endpoints."""

    for kind, state in states.items():
        if state.kind is not kind:
            raise ValueError(
                "state mapping key must match the repository state kind"
            )

    rows: list[StateComparisonRow] = []
    for kind, question, left_kind, right_kind in _ROW_CONTRACTS:
        left = states.get(left_kind)
        right = states.get(right_kind)
        missing = tuple(
            endpoint.value
            for endpoint, state in (
                (left_kind, left),
                (right_kind, right),
            )
            if state is None
        )
        available = not missing
        rows.append(
            StateComparisonRow(
                kind=kind,
                question=question,
                left_state_kind=left_kind,
                right_state_kind=right_kind,
                left_state_id=left.id if left is not None else None,
                right_state_id=right.id if right is not None else None,
                status=(
                    MatrixEntryStatus.REQUIRED
                    if available
                    else MatrixEntryStatus.UNAVAILABLE
                ),
                limitations=(
                    ()
                    if available
                    else (
                        "missing endpoint kinds: " + ", ".join(missing),
                    )
                ),
            )
        )

    return StateComparisonMatrix(tuple(rows))
