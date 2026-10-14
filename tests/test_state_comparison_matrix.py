from __future__ import annotations

import unittest

from gitdrift.domain import (
    ComparisonKind,
    MatrixEntryStatus,
    RepositoryState,
    StateComparisonMatrix,
    StateComparisonRow,
    StateKind,
    construct_required_comparison_matrix,
)


def state(kind: StateKind, identity: str) -> RepositoryState:
    return RepositoryState(
        kind=kind,
        repository_id="repo",
        content_identity=identity,
    )


class StateComparisonMatrixTests(unittest.TestCase):
    def test_every_required_row_is_present_in_canonical_order(self) -> None:
        states = {
            StateKind.COMMIT: state(StateKind.COMMIT, "commit:head"),
            StateKind.BRANCH_TIP: state(
                StateKind.BRANCH_TIP,
                "commit:upstream",
            ),
            StateKind.INDEX: state(StateKind.INDEX, "manifest:index"),
            StateKind.WORKING_TREE: state(
                StateKind.WORKING_TREE,
                "manifest:worktree",
            ),
        }

        matrix = construct_required_comparison_matrix(states)

        self.assertEqual(
            tuple(row.kind for row in matrix.rows),
            tuple(ComparisonKind),
        )
        self.assertEqual(
            {row.status for row in matrix.rows},
            {MatrixEntryStatus.REQUIRED},
        )
        self.assertTrue(
            all(row.left_state_id for row in matrix.rows)
        )
        self.assertTrue(
            all(row.right_state_id for row in matrix.rows)
        )

    def test_missing_endpoints_remain_explicit_unavailable_rows(
        self,
    ) -> None:
        head = state(StateKind.COMMIT, "commit:head")

        matrix = construct_required_comparison_matrix(
            {StateKind.COMMIT: head}
        )

        self.assertEqual(len(matrix.rows), 4)
        rows = {row.kind: row for row in matrix.rows}

        head_to_index = rows[ComparisonKind.HEAD_TO_INDEX]
        self.assertEqual(
            head_to_index.status,
            MatrixEntryStatus.UNAVAILABLE,
        )
        self.assertEqual(head_to_index.left_state_id, head.id)
        self.assertIsNone(head_to_index.right_state_id)
        self.assertEqual(
            head_to_index.limitations,
            ("missing endpoint kinds: index",),
        )

        index_to_worktree = rows[
            ComparisonKind.INDEX_TO_WORKTREE
        ]
        self.assertEqual(
            index_to_worktree.status,
            MatrixEntryStatus.UNAVAILABLE,
        )
        self.assertIsNone(index_to_worktree.left_state_id)
        self.assertIsNone(index_to_worktree.right_state_id)
        self.assertEqual(
            index_to_worktree.limitations,
            (
                "missing endpoint kinds: index, working-tree",
            ),
        )

    def test_endpoint_direction_controls_row_identity(self) -> None:
        left = state(StateKind.COMMIT, "commit:left")
        right = state(StateKind.INDEX, "manifest:right")

        forward = StateComparisonRow(
            kind=ComparisonKind.HEAD_TO_INDEX,
            question="staged?",
            left_state_kind=StateKind.COMMIT,
            right_state_kind=StateKind.INDEX,
            left_state_id=left.id,
            right_state_id=right.id,
            status=MatrixEntryStatus.REQUIRED,
        )
        reverse = StateComparisonRow(
            kind=ComparisonKind.HEAD_TO_INDEX,
            question="staged?",
            left_state_kind=StateKind.INDEX,
            right_state_kind=StateKind.COMMIT,
            left_state_id=right.id,
            right_state_id=left.id,
            status=MatrixEntryStatus.REQUIRED,
        )

        self.assertNotEqual(forward.id, reverse.id)

    def test_required_row_rejects_missing_endpoint(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "need both endpoint identities",
        ):
            StateComparisonRow(
                kind=ComparisonKind.HEAD_TO_INDEX,
                question="staged?",
                left_state_kind=StateKind.COMMIT,
                right_state_kind=StateKind.INDEX,
                left_state_id="state:head",
                right_state_id=None,
                status=MatrixEntryStatus.REQUIRED,
            )

    def test_unavailable_row_rejects_two_available_endpoints(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "cannot be marked unavailable",
        ):
            StateComparisonRow(
                kind=ComparisonKind.HEAD_TO_INDEX,
                question="staged?",
                left_state_kind=StateKind.COMMIT,
                right_state_kind=StateKind.INDEX,
                left_state_id="state:head",
                right_state_id="state:index",
                status=MatrixEntryStatus.UNAVAILABLE,
            )

    def test_matrix_rejects_omitted_required_row(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "every required row",
        ):
            StateComparisonMatrix(())

    def test_mapping_key_must_match_state_kind(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "mapping key must match",
        ):
            construct_required_comparison_matrix(
                {
                    StateKind.INDEX: state(
                        StateKind.COMMIT,
                        "commit:head",
                    )
                }
            )


if __name__ == "__main__":
    unittest.main()
