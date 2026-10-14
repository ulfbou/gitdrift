from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from gitdrift.adapters.git import (
    GitRepositoryError,
    GitRepositoryReader,
)
from gitdrift.application import capture_upstream
from gitdrift.domain import StateKind


def git(
    root: Path,
    *arguments: str,
    allowed: tuple[int, ...] = (0,),
) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if completed.returncode not in allowed:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


class UpstreamCaptureTests(unittest.TestCase):
    def repository(
        self,
    ) -> tuple[
        tempfile.TemporaryDirectory[str],
        Path,
        Path,
    ]:
        temporary = tempfile.TemporaryDirectory()
        container = Path(temporary.name)
        remote = container / "remote.git"
        root = container / "repository"

        git(container, "init", "--bare", "-q", str(remote))
        git(container, "clone", "-q", str(remote), str(root))
        git(root, "config", "user.email", "test@example.com")
        git(root, "config", "user.name", "Test")
        git(root, "checkout", "-qb", "master")

        (root / "tracked.txt").write_text(
            "base\n",
            encoding="utf-8",
        )
        git(root, "add", "tracked.txt")
        git(root, "commit", "-qm", "initial")
        git(root, "push", "-qu", "origin", "master")

        return temporary, remote, root

    def snapshot(self, root: Path) -> tuple[object, ...]:
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

    def test_configured_upstream_retains_locator_and_target(
        self,
    ) -> None:
        temporary, _, root = self.repository()
        self.addCleanup(temporary.cleanup)

        before = self.snapshot(root)
        reader = GitRepositoryReader(root)
        evidence = reader.capture_upstream()
        after = self.snapshot(root)

        self.assertEqual(before, after)
        self.assertIsNotNone(evidence)
        assert evidence is not None
        self.assertEqual(
            evidence.locator,
            "refs/remotes/origin/master",
        )
        self.assertEqual(
            evidence.commit_id,
            git(root, "rev-parse", "origin/master^{commit}"),
        )
        self.assertEqual(
            evidence.tree_id,
            git(root, "rev-parse", "origin/master^{tree}"),
        )

        state = capture_upstream(reader)
        self.assertIsNotNone(state)
        assert state is not None
        self.assertEqual(state.kind, StateKind.BRANCH_TIP)
        self.assertEqual(
            state.locators,
            ("refs/remotes/origin/master",),
        )
        self.assertIn(
            f"commit:{evidence.commit_id}",
            state.content_identity,
        )
        self.assertIn(
            f"tree:{evidence.tree_id}",
            state.content_identity,
        )

    def test_absent_upstream_returns_none(self) -> None:
        temporary, _, root = self.repository()
        self.addCleanup(temporary.cleanup)
        git(
            root,
            "branch",
            "--unset-upstream",
        )

        before = self.snapshot(root)
        reader = GitRepositoryReader(root)

        self.assertIsNone(reader.capture_upstream())
        self.assertIsNone(capture_upstream(reader))
        self.assertEqual(self.snapshot(root), before)

    def test_capture_does_not_fetch_remote_movement(self) -> None:
        temporary, remote, root = self.repository()
        self.addCleanup(temporary.cleanup)

        other = Path(temporary.name) / "other"
        git(Path(temporary.name), "clone", "-q", str(remote), str(other))
        git(other, "config", "user.email", "test@example.com")
        git(other, "config", "user.name", "Test")
        git(other, "checkout", "-q", "master")

        local_remote_tip = git(
            root,
            "rev-parse",
            "refs/remotes/origin/master",
        )
        (other / "remote.txt").write_text(
            "remote\n",
            encoding="utf-8",
        )
        git(other, "add", "remote.txt")
        git(other, "commit", "-qm", "remote movement")
        git(other, "push", "-q", "origin", "master")

        evidence = GitRepositoryReader(root).capture_upstream()
        self.assertIsNotNone(evidence)
        assert evidence is not None
        self.assertEqual(evidence.commit_id, local_remote_tip)
        self.assertNotEqual(
            evidence.commit_id,
            git(other, "rev-parse", "HEAD"),
        )
        self.assertEqual(
            git(root, "rev-parse", "refs/remotes/origin/master"),
            local_remote_tip,
        )

    def test_upstream_movement_during_capture_is_rejected(
        self,
    ) -> None:
        temporary, _, root = self.repository()
        self.addCleanup(temporary.cleanup)

        reader = GitRepositoryReader(root)
        original = reader._git
        commit_reads = 0

        def changing_git(
            *arguments: str,
            allowed: tuple[int, ...] = (0,),
        ) -> str:
            nonlocal commit_reads
            value = original(*arguments, allowed=allowed)
            if (
                arguments[:2] == ("rev-parse", "--verify")
                and arguments[-1].endswith("^{commit}")
            ):
                commit_reads += 1
                if commit_reads == 2:
                    return value + ":changed"
            return value

        reader._git = changing_git  # type: ignore[method-assign]

        with self.assertRaisesRegex(
            GitRepositoryError,
            "upstream changed during capture",
        ):
            reader.capture_upstream()


if __name__ == "__main__":
    unittest.main()
