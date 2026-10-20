from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from gitdrift.contracts import ExecutionStatus
from gitdrift.profiles import (
    StateAwarenessProfile,
    StateAwarenessRequest,
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


def repository_snapshot(root: Path) -> tuple[object, ...]:
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


class StateAwarenessProfileTests(unittest.TestCase):
    def test_clean_repository_without_upstream_is_valid_partial_output(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        before = repository_snapshot(root)
        request = StateAwarenessRequest(root)

        first = StateAwarenessProfile().run(request)
        second = StateAwarenessProfile().run(request)

        self.assertEqual(repository_snapshot(root), before)
        self.assertEqual(first, second)
        self.assertEqual(
            first.status,
            ExecutionStatus.COMPLETED_PARTIAL,
        )

        document = json.loads(first.artifact.payload)
        self.assertEqual(len(document["states"]), 3)
        self.assertEqual(len(document["comparisons"]), 3)
        self.assertEqual(document["changes"], [])
        self.assertEqual(
            document["completeness"]["values"][
                "semantic-extraction"
            ],
            "not-requested",
        )
        self.assertEqual(
            document["diagnostics"][0]["code"],
            "GD-STATE-COMPARISON-UNAVAILABLE",
        )
        self.assertEqual(
            document["completeness"]["values"]["selected-refs"],
            "not-applicable",
        )

    def test_upstream_completes_all_required_comparisons(
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

        before = repository_snapshot(root)
        result = StateAwarenessProfile().run(
            StateAwarenessRequest(root)
        )

        self.assertEqual(repository_snapshot(root), before)
        self.assertEqual(
            result.status,
            ExecutionStatus.COMPLETED,
        )

        document = json.loads(result.artifact.payload)
        self.assertEqual(len(document["states"]), 4)
        self.assertEqual(len(document["comparisons"]), 4)
        self.assertEqual(document["diagnostics"], [])
        self.assertEqual(
            document["completeness"]["values"]["selected-refs"],
            "complete",
        )

    def test_absent_upstream_explicitly_excluded_is_complete(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        result = StateAwarenessProfile().run(
            StateAwarenessRequest(
                root,
                include_upstream=False,
            )
        )

        self.assertEqual(
            result.status,
            ExecutionStatus.COMPLETED,
        )
        document = json.loads(result.artifact.payload)
        self.assertEqual(len(document["states"]), 3)
        self.assertEqual(len(document["comparisons"]), 3)
        self.assertEqual(document["diagnostics"], [])
        self.assertEqual(
            document["completeness"]["values"]["selected-refs"],
            "not-requested",
        )

    def test_available_upstream_explicitly_excluded_is_complete(
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

        result = StateAwarenessProfile().run(
            StateAwarenessRequest(
                root,
                include_upstream=False,
            )
        )

        self.assertEqual(
            result.status,
            ExecutionStatus.COMPLETED,
        )
        document = json.loads(result.artifact.payload)
        self.assertEqual(len(document["states"]), 3)
        self.assertEqual(len(document["comparisons"]), 3)
        self.assertEqual(document["diagnostics"], [])
        self.assertEqual(
            document["completeness"]["values"]["selected-refs"],
            "not-requested",
        )

    def test_comparison_budget_cannot_silently_truncate_matrix(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        with self.assertRaisesRegex(
            ValueError,
            "complete required state-awareness matrix",
        ):
            StateAwarenessProfile().run(
                StateAwarenessRequest(
                    root,
                    budgets=(("comparisons", 3),),
                )
            )

    def test_invalid_budget_is_rejected(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        with self.assertRaisesRegex(
            ValueError,
            "positive integer",
        ):
            StateAwarenessRequest(
                root,
                budgets=(("comparisons", 0),),
            )


if __name__ == "__main__":
    unittest.main()
