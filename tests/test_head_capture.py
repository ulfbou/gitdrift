from __future__ import annotations
import subprocess
import tempfile
import unittest
from pathlib import Path
from gitdrift.adapters.git import GitRepositoryError, GitRepositoryReader
from gitdrift.application import capture_head
from gitdrift.domain import StateKind

def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, text=True, capture_output=True).stdout.strip()

class HeadCaptureTests(unittest.TestCase):
    def test_capture_records_immutable_commit_and_tree_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            git(root, "config", "user.email", "test@example.com")
            git(root, "config", "user.name", "Test")
            (root / "a.txt").write_text("content\n", encoding="utf-8")
            git(root, "add", "a.txt")
            git(root, "commit", "-qm", "initial")
            before = (git(root, "rev-parse", "HEAD"), git(root, "status", "--porcelain=v1"))
            state = capture_head(GitRepositoryReader(root))
            after = (git(root, "rev-parse", "HEAD"), git(root, "status", "--porcelain=v1"))
            self.assertEqual(before, after)
            self.assertEqual(state.kind, StateKind.COMMIT)
            self.assertIn(f"commit:{before[0]}", state.content_identity)
            self.assertIn(f"tree:{git(root, 'rev-parse', 'HEAD^{tree}')}", state.content_identity)

    def test_explicit_repository_root_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            child = root / "child"
            child.mkdir()
            with self.assertRaises(GitRepositoryError):
                GitRepositoryReader(child).capture_head()

if __name__ == "__main__":
    unittest.main()
