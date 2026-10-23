from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest import mock

from gitdrift.adapters.git.comparison import GitStateComparator
from gitdrift.adapters.git.repository import (
    GIT_COMMAND_TIMEOUT_SECONDS,
    GitRepositoryError,
    GitRepositoryReader,
)


class GitCommandTimeoutTests(unittest.TestCase):
    def test_repository_commands_use_the_declared_ceiling(self) -> None:
        completed = mock.Mock(returncode=0, stdout=b"ok", stderr=b"")
        with mock.patch(
            "gitdrift.adapters.git.repository.subprocess.run",
            return_value=completed,
        ) as run:
            result = GitRepositoryReader(Path("."))._git_bytes("status")

        self.assertEqual(result, b"ok")
        self.assertEqual(
            run.call_args.kwargs["timeout"],
            GIT_COMMAND_TIMEOUT_SECONDS,
        )

    def test_repository_timeout_is_a_truthful_domain_failure(self) -> None:
        with mock.patch(
            "gitdrift.adapters.git.repository.subprocess.run",
            side_effect=subprocess.TimeoutExpired(("git", "status"), 30),
        ):
            with self.assertRaisesRegex(
                GitRepositoryError,
                "execution ceiling",
            ):
                GitRepositoryReader(Path("."))._git_bytes("status")

    def test_comparison_timeout_is_a_truthful_domain_failure(self) -> None:
        with mock.patch(
            "gitdrift.adapters.git.comparison.subprocess.run",
            side_effect=subprocess.TimeoutExpired(("git", "diff"), 30),
        ):
            with self.assertRaisesRegex(
                GitRepositoryError,
                "comparison exceeded",
            ):
                GitStateComparator(Path("."))._git_bytes("diff")

    def test_ancestry_timeout_is_a_truthful_domain_failure(self) -> None:
        with mock.patch(
            "gitdrift.adapters.git.comparison.subprocess.run",
            side_effect=subprocess.TimeoutExpired(("git", "merge-base"), 30),
        ):
            with self.assertRaisesRegex(
                GitRepositoryError,
                "ancestry check exceeded",
            ):
                GitStateComparator(Path("."))._is_ancestor("left", "right")


if __name__ == "__main__":
    unittest.main()
