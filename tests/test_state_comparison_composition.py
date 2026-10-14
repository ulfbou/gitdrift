from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from gitdrift.adapters.git import (
    GitRepositoryReader,
    GitStateComparator,
)
from gitdrift.application import (
    ComparisonMatrixRequest,
    compose_state_comparison_matrix,
)
from gitdrift.domain import (
    ComparisonKind,
    MatrixEntryStatus,
    StateKind,
)


def git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=True,
    )
    return completed.stdout.strip()


def repository() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)

    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Test")

    (root / "tracked.txt").write_text(
        "base\n",
        encoding="utf-8",
    )
    git(root, "add", "tracked.txt")
    git(root, "commit", "-qm", "initial")

    return temporary, root


def snapshot(root: Path) -> tuple[object, ...]:
    index_path = Path(
        git(root, "rev-parse", "--git-path", "index")
    )
    if not index_path.is_absolute():
        index_path = root / index_path

    return (
        git(root, "rev-parse", "HEAD"),
        index_path.read_bytes(),
        git(root, "status", "--porcelain=v1", "-z"),
        git(root, "config", "--local", "--list"),
        git(root, "show-ref"),
    )


class StateComparisonCompositionTests(unittest.TestCase):
    def test_all_available_required_rows_execute_in_order(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        git(root, "branch", "upstream")
        git(root, "config", "branch.master.remote", ".")
        git(
            root,
            "config",
            "branch.master.merge",
            "refs/heads/upstream",
        )

        (root / "tracked.txt").write_text(
            "staged\n",
            encoding="utf-8",
        )
        git(root, "add", "tracked.txt")
        (root / "tracked.txt").write_text(
            "unstaged\n",
            encoding="utf-8",
        )

        before = snapshot(root)
        reader = GitRepositoryReader(root)

        first = compose_state_comparison_matrix(
            ComparisonMatrixRequest(),
            reader,
            GitStateComparator(root),
        )
        second = compose_state_comparison_matrix(
            ComparisonMatrixRequest(),
            reader,
            GitStateComparator(root),
        )

        self.assertEqual(snapshot(root), before)
        self.assertEqual(first, second)
        self.assertEqual(
            tuple(row.kind for row in first.matrix.rows),
            tuple(ComparisonKind),
        )
        self.assertEqual(
            {row.status for row in first.matrix.rows},
            {MatrixEntryStatus.REQUIRED},
        )
        self.assertTrue(
            all(item.result is not None for item in first.executions)
        )
        self.assertEqual(
            tuple(state.kind for state in first.states),
            (
                StateKind.COMMIT,
                StateKind.BRANCH_TIP,
                StateKind.INDEX,
                StateKind.WORKING_TREE,
            ),
        )

        for execution in first.executions:
            assert execution.result is not None
            self.assertEqual(
                execution.result.comparison.left_state_id,
                execution.row.left_state_id,
            )
            self.assertEqual(
                execution.result.comparison.right_state_id,
                execution.row.right_state_id,
            )
            self.assertEqual(
                execution.result.comparison.kind,
                execution.row.kind.value,
            )

    def test_absent_upstream_remains_explicitly_unavailable(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        reader = GitRepositoryReader(root)
        result = compose_state_comparison_matrix(
            ComparisonMatrixRequest(),
            reader,
            GitStateComparator(root),
        )

        upstream = next(
            item
            for item in result.executions
            if item.row.kind
            is ComparisonKind.HEAD_AND_UPSTREAM
        )

        self.assertEqual(
            upstream.row.status,
            MatrixEntryStatus.UNAVAILABLE,
        )
        self.assertIsNone(upstream.result)
        self.assertIn(
            "branch-tip",
            upstream.row.limitations[0],
        )
        self.assertEqual(
            tuple(state.kind for state in result.states),
            (
                StateKind.COMMIT,
                StateKind.INDEX,
                StateKind.WORKING_TREE,
            ),
        )

    def test_upstream_can_be_explicitly_unselected(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        git(root, "branch", "upstream")
        git(root, "config", "branch.master.remote", ".")
        git(
            root,
            "config",
            "branch.master.merge",
            "refs/heads/upstream",
        )

        result = compose_state_comparison_matrix(
            ComparisonMatrixRequest(include_upstream=False),
            GitRepositoryReader(root),
            GitStateComparator(root),
        )

        upstream = next(
            item
            for item in result.executions
            if item.row.kind
            is ComparisonKind.HEAD_AND_UPSTREAM
        )
        self.assertEqual(
            upstream.row.status,
            MatrixEntryStatus.UNAVAILABLE,
        )
        self.assertIsNone(upstream.result)
        self.assertNotIn(
            StateKind.BRANCH_TIP,
            {state.kind for state in result.states},
        )


if __name__ == "__main__":
    unittest.main()
