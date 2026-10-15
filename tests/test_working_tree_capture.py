from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from gitdrift.adapters.git import (
    GitRepositoryError,
    GitRepositoryReader,
    WorkingTreeChangedError,
)
from gitdrift.application import capture_working_tree
from gitdrift.domain import StateKind
from gitdrift.ports import (
    IgnoredPolicy,
    UntrackedPolicy,
    WorkingTreeEntryKind,
)


def git(
    root: Path,
    *arguments: str,
    input: bytes | None = None,
) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        input=input,
        stdin=None if input is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.decode("utf-8").strip()


def repository() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Test")
    (root / ".gitignore").write_text(
        "ignored.txt\n",
        encoding="utf-8",
    )
    (root / "tracked.txt").write_bytes(b"base\r\n")
    (root / "delete.txt").write_bytes(b"delete\n")
    git(root, "add", ".gitignore", "tracked.txt", "delete.txt")
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
        tuple(
            sorted(
                (
                    path.relative_to(root).as_posix(),
                    path.read_bytes(),
                )
                for path in root.rglob("*")
                if path.is_file()
                and ".git" not in path.relative_to(root).parts
            )
        ),
    )


class WorkingTreeCaptureTests(unittest.TestCase):
    def test_clean_capture_is_deterministic_and_read_only(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        before = snapshot(root)
        reader = GitRepositoryReader(root)

        first = reader.capture_working_tree()
        second = reader.capture_working_tree()
        after = snapshot(root)

        self.assertEqual(before, after)
        self.assertEqual(first, second)
        self.assertEqual(
            [entry.path for entry in first.entries],
            [".gitignore", "delete.txt", "tracked.txt"],
        )

        state = capture_working_tree(reader)
        self.assertEqual(state.kind, StateKind.WORKING_TREE)
        self.assertEqual(
            state.content_identity,
            first.manifest_identity,
        )
        self.assertIsNotNone(state.base_state_id)

    def test_application_state_references_exact_captured_index(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        reader = GitRepositoryReader(root)
        index_state = __import__(
            "gitdrift.application",
            fromlist=["capture_index"],
        ).capture_index(reader)
        working_tree_state = capture_working_tree(reader)

        self.assertEqual(
            working_tree_state.base_state_id,
            index_state.id,
        )

    def test_modified_binary_and_deleted_content_are_exact(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        (root / "tracked.txt").write_bytes(b"\x00\xffchanged")
        (root / "delete.txt").unlink()

        evidence = GitRepositoryReader(root).capture_working_tree()
        entries = {entry.path: entry for entry in evidence.entries}

        self.assertEqual(
            entries["tracked.txt"].kind,
            WorkingTreeEntryKind.REGULAR,
        )
        self.assertEqual(entries["tracked.txt"].size, 9)
        self.assertEqual(
            entries["delete.txt"].kind,
            WorkingTreeEntryKind.DELETED,
        )

    def test_untracked_policies_are_explicit(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        (root / "one.txt").write_text("one\n", encoding="utf-8")
        (root / "two.txt").write_text("two\n", encoding="utf-8")
        reader = GitRepositoryReader(root)

        excluded = reader.capture_working_tree()
        self.assertNotIn(
            "one.txt",
            {entry.path for entry in excluded.entries},
        )

        selected = reader.capture_working_tree(
            untracked_policy=UntrackedPolicy.INCLUDE_SELECTED,
            selected_paths=("one.txt",),
        )
        self.assertIn(
            "one.txt",
            {entry.path for entry in selected.entries},
        )
        self.assertNotIn(
            "two.txt",
            {entry.path for entry in selected.entries},
        )

        all_visible = reader.capture_working_tree(
            untracked_policy=UntrackedPolicy.INCLUDE_ALL_VISIBLE,
        )
        paths = {entry.path for entry in all_visible.entries}
        self.assertIn("one.txt", paths)
        self.assertIn("two.txt", paths)

    def test_ignored_files_require_explicit_selected_policy(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        (root / "ignored.txt").write_text(
            "ignored\n",
            encoding="utf-8",
        )
        reader = GitRepositoryReader(root)

        excluded = reader.capture_working_tree()
        self.assertNotIn(
            "ignored.txt",
            {entry.path for entry in excluded.entries},
        )

        included = reader.capture_working_tree(
            ignored_policy=IgnoredPolicy.INCLUDE_SELECTED,
            selected_paths=("ignored.txt",),
        )
        self.assertIn(
            "ignored.txt",
            {entry.path for entry in included.entries},
        )

    @unittest.skipUnless(
        hasattr(os, "symlink"),
        "symlinks unavailable",
    )
    def test_symlink_target_is_captured_without_following(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        target = Path(temporary.name).parent / "outside-secret.txt"
        target.write_text("secret\n", encoding="utf-8")
        self.addCleanup(
            lambda: target.unlink()
            if target.exists()
            else None
        )
        link = root / "link.txt"
        try:
            os.symlink(target, link)
        except OSError as error:
            self.skipTest(str(error))

        evidence = GitRepositoryReader(root).capture_working_tree(
            untracked_policy=UntrackedPolicy.INCLUDE_SELECTED,
            selected_paths=("link.txt",),
        )
        entry = next(
            item
            for item in evidence.entries
            if item.path == "link.txt"
        )

        self.assertEqual(
            entry.kind,
            WorkingTreeEntryKind.SYMLINK,
        )
        observed_target = os.readlink(link)
        self.assertEqual(entry.symlink_target, observed_target)
        self.assertEqual(
            entry.content_identity,
            "sha256:"
            + __import__("hashlib").sha256(
                os.fsencode(observed_target)
            ).hexdigest(),
        )
        self.assertNotEqual(
            entry.content_identity,
            "sha256:"
            + __import__("hashlib").sha256(
                target.read_bytes()
            ).hexdigest(),
        )

    def test_selected_missing_path_is_rejected(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        with self.assertRaisesRegex(
            GitRepositoryError,
            "selected paths are unavailable",
        ):
            GitRepositoryReader(root).capture_working_tree(
                untracked_policy=UntrackedPolicy.INCLUDE_SELECTED,
                selected_paths=("missing.txt",),
            )

    def test_index_change_during_capture_is_rejected(self) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        reader = GitRepositoryReader(root)
        original = reader.capture_index
        calls = 0

        def changing_index():
            nonlocal calls
            calls += 1
            evidence = original()
            if calls == 2:
                return type(evidence)(
                    evidence.repository_id,
                    evidence.object_format,
                    evidence.base_commit_id,
                    evidence.base_tree_id,
                    evidence.entries,
                    evidence.manifest_identity + ":changed",
                    evidence.limitations,
                )
            return evidence

        reader.capture_index = changing_index  # type: ignore[method-assign]
        with self.assertRaises(WorkingTreeChangedError):
            reader.capture_working_tree()

    def test_selected_bytes_change_during_capture_is_rejected(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)
        reader = GitRepositoryReader(root)
        original = reader._capture_entry
        calls = 0

        def changing_entry(path, index_entry):
            nonlocal calls
            entry = original(path, index_entry)
            calls += 1
            if calls == 3:
                (root / "tracked.txt").write_bytes(b"changed")
            return entry

        reader._capture_entry = changing_entry  # type: ignore[method-assign]
        with self.assertRaises(WorkingTreeChangedError):
            reader.capture_working_tree()


if __name__ == "__main__":
    unittest.main()
