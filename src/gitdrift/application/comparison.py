"""Application composition for the required state-comparison matrix."""

from __future__ import annotations

from dataclasses import dataclass

from gitdrift.domain import (
    ComparisonKind,
    MatrixEntryStatus,
    RepositoryState,
    StateComparisonMatrix,
    StateComparisonRow,
    StateKind,
    construct_required_comparison_matrix,
)
from gitdrift.ports import (
    RepositoryReader,
    StateComparator,
    StateComparisonResult,
)

from .capture import (
    capture_head,
    capture_index,
    capture_upstream,
    capture_working_tree,
)


@dataclass(frozen=True, slots=True)
class ComparisonMatrixRequest:
    """Explicit selection for required state comparison composition."""

    include_upstream: bool = True


@dataclass(frozen=True, slots=True)
class ComparisonMatrixExecution:
    """One declared matrix row and its available execution result."""

    row: StateComparisonRow
    result: StateComparisonResult | None

    def __post_init__(self) -> None:
        if self.row.status is MatrixEntryStatus.REQUIRED:
            if self.result is None:
                raise ValueError(
                    "required comparison row needs an execution result"
                )
            comparison = self.result.comparison
            if (
                comparison.left_state_id != self.row.left_state_id
                or comparison.right_state_id
                != self.row.right_state_id
                or comparison.kind != self.row.kind.value
            ):
                raise ValueError(
                    "comparison result does not match its matrix row"
                )
        elif self.result is not None:
            raise ValueError(
                "unavailable comparison row cannot have a result"
            )


@dataclass(frozen=True, slots=True)
class ComparisonMatrixResult:
    """Captured states and complete required comparison composition."""

    states: tuple[RepositoryState, ...]
    matrix: StateComparisonMatrix
    executions: tuple[ComparisonMatrixExecution, ...]

    def __post_init__(self) -> None:
        if tuple(item.row.id for item in self.executions) != tuple(
            row.id for row in self.matrix.rows
        ):
            raise ValueError(
                "comparison executions must match matrix row order"
            )


def compose_state_comparison_matrix(
    request: ComparisonMatrixRequest,
    reader: RepositoryReader,
    comparator: StateComparator,
) -> ComparisonMatrixResult:
    """Capture selected states and execute every available required row."""

    head = capture_head(reader)
    index = capture_index(reader)
    working_tree = capture_working_tree(reader)
    upstream = capture_upstream(reader) if request.include_upstream else None

    states_by_kind = {
        StateKind.COMMIT: head,
        StateKind.INDEX: index,
        StateKind.WORKING_TREE: working_tree,
    }
    if upstream is not None:
        states_by_kind[StateKind.BRANCH_TIP] = upstream

    matrix = construct_required_comparison_matrix(states_by_kind)

    operations = {
        ComparisonKind.HEAD_TO_INDEX: (
            comparator.compare_head_to_index
        ),
        ComparisonKind.INDEX_TO_WORKTREE: (
            comparator.compare_index_to_working_tree
        ),
        ComparisonKind.HEAD_TO_WORKTREE: (
            comparator.compare_head_to_working_tree
        ),
        ComparisonKind.HEAD_AND_UPSTREAM: (
            comparator.compare_head_and_upstream
        ),
    }

    executions = tuple(
        ComparisonMatrixExecution(
            row=row,
            result=(
                operations[row.kind]()
                if row.status is MatrixEntryStatus.REQUIRED
                else None
            ),
        )
        for row in matrix.rows
    )

    ordered_states = tuple(
        state
        for kind in (
            StateKind.COMMIT,
            StateKind.BRANCH_TIP,
            StateKind.INDEX,
            StateKind.WORKING_TREE,
        )
        if (state := states_by_kind.get(kind)) is not None
    )

    return ComparisonMatrixResult(
        states=ordered_states,
        matrix=matrix,
        executions=executions,
    )
