from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from gitdrift.profiles import StateAwarenessProfile, StateAwarenessRequest


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
    (root / "tracked.txt").write_text("base\n", encoding="utf-8")
    git(root, "add", "tracked.txt")
    git(root, "commit", "-qm", "initial")
    return temporary, root


class StateAwarenessOutputBudgetTests(unittest.TestCase):
    def test_default_policy_declares_a_finite_native_output_ceiling(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        budgets = dict(StateAwarenessRequest(root).budgets)

        self.assertEqual(budgets["comparisons"], 4)
        self.assertEqual(budgets["native_output_bytes"], 16 * 1024 * 1024)

    def test_output_above_ceiling_fails_without_false_success(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        before = git(root, "status", "--porcelain=v1", "-z")
        request = StateAwarenessRequest(
            root,
            budgets=(
                ("comparisons", 4),
                ("native_output_bytes", 1),
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "native output exceeds.*no artifact was delivered",
        ):
            StateAwarenessProfile().run(request)

        self.assertEqual(
            git(root, "status", "--porcelain=v1", "-z"),
            before,
        )

    def test_output_within_ceiling_is_accepted_deterministically(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        ceiling = 16 * 1024 * 1024
        request = StateAwarenessRequest(
            root,
            budgets=(
                ("comparisons", 4),
                ("native_output_bytes", ceiling),
            ),
        )

        first = StateAwarenessProfile().run(request)
        second = StateAwarenessProfile().run(request)

        self.assertLessEqual(
            len(first.artifact.payload),
            ceiling,
        )
        self.assertEqual(
            second.artifact.payload,
            first.artifact.payload,
        )


if __name__ == "__main__":
    unittest.main()
