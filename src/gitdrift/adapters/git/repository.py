"""Read-only Git repository adapter."""
from __future__ import annotations
import subprocess
from pathlib import Path
from gitdrift.ports import HeadEvidence

class GitRepositoryError(RuntimeError):
    """Git repository evidence could not be acquired safely."""

class GitRepositoryReader:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _git(self, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", *arguments],
            cwd=self._root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="strict",
            check=False,
        )
        if completed.returncode:
            raise GitRepositoryError(completed.stderr.strip() or "Git command failed")
        return completed.stdout.strip()

    def capture_head(self) -> HeadEvidence:
        repository_root = Path(self._git("rev-parse", "--show-toplevel")).resolve()
        if repository_root != self._root:
            raise GitRepositoryError("repository root does not match the explicit request")
        object_format = self._git("rev-parse", "--show-object-format")
        commit = self._git("rev-parse", "--verify", "HEAD^{commit}")
        tree = self._git("rev-parse", "--verify", "HEAD^{tree}")
        locator = self._git("symbolic-ref", "-q", "HEAD") or None
        repository_id = f"git:{object_format}:{repository_root.as_posix()}"
        return HeadEvidence(repository_id, commit, tree, locator)
