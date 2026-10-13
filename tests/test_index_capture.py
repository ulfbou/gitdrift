from __future__ import annotations
import subprocess
import tempfile
import unittest
from pathlib import Path
from gitdrift.adapters.git import GitRepositoryReader, IndexChangedError
from gitdrift.application import capture_index
from gitdrift.domain import StateKind

def git(root: Path, *args: str, input: bytes | None = None) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, input=input,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.decode("utf-8").strip()

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

class IndexCaptureTests(unittest.TestCase):
    def test_capture_is_deterministic_and_read_only(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        (root / "tracked.txt").write_text("staged\n", encoding="utf-8")
        git(root, "add", "tracked.txt")
        index_path = Path(git(root, "rev-parse", "--git-path", "index"))
        if not index_path.is_absolute():
            index_path = root / index_path
        before = (
            git(root, "rev-parse", "HEAD"),
            index_path.read_bytes(),
            git(root, "status", "--porcelain=v1"),
            git(root, "config", "--local", "--list"),
        )
        first = GitRepositoryReader(root).capture_index()
        second = GitRepositoryReader(root).capture_index()
        after = (
            git(root, "rev-parse", "HEAD"),
            index_path.read_bytes(),
            git(root, "status", "--porcelain=v1"),
            git(root, "config", "--local", "--list"),
        )
        self.assertEqual(before, after)
        self.assertEqual(first, second)
        self.assertEqual(first.entries[0].path, "tracked.txt")
        self.assertEqual(first.entries[0].stage, 0)
        self.assertEqual(first.entries[0].mode, "100644")
        state = capture_index(GitRepositoryReader(root))
        self.assertEqual(state.kind, StateKind.INDEX)
        self.assertEqual(state.content_identity, first.manifest_identity)
        self.assertIsNotNone(state.base_state_id)

    def test_semantic_index_change_changes_manifest_identity(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        first = GitRepositoryReader(root).capture_index()
        (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
        git(root, "add", "tracked.txt")
        second = GitRepositoryReader(root).capture_index()
        self.assertNotEqual(first.manifest_identity, second.manifest_identity)
        self.assertNotEqual(first.entries, second.entries)

    def test_unmerged_entries_preserve_all_stages(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        base = git(root, "hash-object", "tracked.txt")
        ours = git(root, "hash-object", "-w", "--stdin", input=b"ours\n")
        theirs = git(root, "hash-object", "-w", "--stdin", input=b"theirs\n")
        git(root, "update-index", "--force-remove", "tracked.txt")
        index_info = (
            f"100644 {base} 1\ttracked.txt\n"
            f"100644 {ours} 2\ttracked.txt\n"
            f"100644 {theirs} 3\ttracked.txt\n"
        ).encode("utf-8")
        git(root, "update-index", "--index-info", input=index_info)
        evidence = GitRepositoryReader(root).capture_index()
        entries = [entry for entry in evidence.entries if entry.path == "tracked.txt"]
        self.assertEqual([entry.stage for entry in entries], [1, 2, 3])

    def test_empty_unborn_index_is_captured_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            evidence = GitRepositoryReader(root).capture_index()
            self.assertEqual(evidence.entries, ())
            self.assertIsNone(evidence.base_commit_id)
            self.assertTrue(evidence.limitations)

    def test_deletion_and_mode_change_affect_manifest(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        baseline = GitRepositoryReader(root).capture_index()
        git(root, "update-index", "--chmod=+x", "tracked.txt")
        executable = GitRepositoryReader(root).capture_index()
        self.assertEqual(executable.entries[0].mode, "100755")
        self.assertNotEqual(baseline.manifest_identity, executable.manifest_identity)
        git(root, "update-index", "--force-remove", "tracked.txt")
        deleted = GitRepositoryReader(root).capture_index()
        self.assertEqual(deleted.entries, ())
        self.assertNotEqual(executable.manifest_identity, deleted.manifest_identity)

    def test_unborn_repository_records_missing_base(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            (root / "new.txt").write_text("new\n", encoding="utf-8")
            git(root, "add", "new.txt")
            evidence = GitRepositoryReader(root).capture_index()
            self.assertIsNone(evidence.base_commit_id)
            self.assertIsNone(evidence.base_tree_id)
            self.assertTrue(evidence.limitations)

    def test_head_change_during_capture_is_rejected(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        reader = GitRepositoryReader(root)
        original = reader._head_marker
        calls = 0

        def changing_head() -> tuple[str | None, str | None]:
            nonlocal calls
            calls += 1
            commit, tree = original()
            if calls == 1:
                return commit, tree
            return (f"{commit}:changed" if commit else "changed"), tree

        reader._head_marker = changing_head  # type: ignore[method-assign]

        with self.assertRaises(IndexChangedError):
            reader.capture_index()

    def test_index_change_during_capture_is_rejected(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        reader = GitRepositoryReader(root)
        original = reader._index_marker
        calls = 0
        def changing_marker() -> str:
            nonlocal calls
            calls += 1
            marker = original()
            return marker if calls == 1 else marker + ":changed"
        reader._index_marker = changing_marker  # type: ignore[method-assign]
        with self.assertRaises(IndexChangedError):
            reader.capture_index()

if __name__ == "__main__":
    unittest.main()
