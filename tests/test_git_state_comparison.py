from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from gitdrift.adapters.git import GitStateComparator
from gitdrift.ports import DiffOptions


def git(
    root: Path,
    *arguments: str,
    input: bytes | None = None,
) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        input=input,
        stdin=None if input is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.decode("utf-8").strip()


def repository() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Test")

    (root / "tracked.txt").write_bytes(b"base\n")
    (root / "deleted.txt").write_bytes(b"delete\n")
    git(root, "add", "tracked.txt", "deleted.txt")
    git(root, "commit", "-qm", "initial")
    return temporary, root


def snapshot(root: Path) -> tuple[object, ...]:
    index = Path(git(root, "rev-parse", "--git-path", "index"))
    if not index.is_absolute():
        index = root / index

    return (
        git(root, "rev-parse", "HEAD"),
        index.read_bytes(),
        git(root, "status", "--porcelain=v1", "-z"),
        git(root, "config", "--local", "--list"),
        git(root, "show-ref"),
    )


class GitStateComparisonTests(unittest.TestCase):
    def test_head_to_index_is_exact_deterministic_and_read_only(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        (root / "tracked.txt").write_bytes(b"staged\n")
        git(root, "add", "tracked.txt")
        before = snapshot(root)

        comparator = GitStateComparator(root)
        first = comparator.compare_head_to_index()
        second = comparator.compare_head_to_index()

        self.assertEqual(snapshot(root), before)
        self.assertEqual(first, second)
        self.assertEqual(
            first.comparison.kind,
            "head-to-index",
        )
        self.assertFalse(
            first.comparison.ancestry_established
        )
        self.assertEqual(len(first.changes), 1)

        change = first.changes[0]
        self.assertEqual(change.status, "modification")
        self.assertEqual(change.source_path, "tracked.txt")
        self.assertEqual(
            change.destination_path,
            "tracked.txt",
        )
        self.assertIsNotNone(change.source_identity)
        self.assertIsNotNone(change.destination_identity)
        self.assertEqual(change.source_mode, "100644")
        self.assertEqual(change.destination_mode, "100644")
        self.assertTrue(
            change.patch_identity.startswith("sha256:")
        )

    def test_index_to_worktree_isolates_unstaged_change(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        (root / "tracked.txt").write_bytes(b"staged\n")
        git(root, "add", "tracked.txt")
        (root / "tracked.txt").write_bytes(b"unstaged\n")

        result = (
            GitStateComparator(root)
            .compare_index_to_working_tree()
        )

        self.assertEqual(len(result.changes), 1)
        self.assertEqual(
            result.changes[0].destination_path,
            "tracked.txt",
        )

    def test_head_to_worktree_combines_staged_and_unstaged(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        (root / "staged.txt").write_bytes(b"staged\n")
        git(root, "add", "staged.txt")
        (root / "tracked.txt").write_bytes(b"unstaged\n")

        result = (
            GitStateComparator(root)
            .compare_head_to_working_tree()
        )

        self.assertEqual(
            {
                change.destination_path
                for change in result.changes
            },
            {"staged.txt", "tracked.txt"},
        )

    def test_addition_deletion_mode_and_binary_are_retained(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        (root / "binary.bin").write_bytes(b"\x00\xff")
        (root / "deleted.txt").unlink()
        (root / "tracked.txt").write_bytes(b"changed\n")
        git(
            root,
            "add",
            "binary.bin",
            "deleted.txt",
            "tracked.txt",
        )
        git(root, "update-index", "--chmod=+x", "tracked.txt")

        result = (
            GitStateComparator(root)
            .compare_head_to_index()
        )
        by_status = {
            change.status: change
            for change in result.changes
        }

        self.assertIn("addition", by_status)
        self.assertIn("deletion", by_status)
        modified = next(
            change
            for change in result.changes
            if change.destination_path == "tracked.txt"
        )
        self.assertEqual(modified.destination_mode, "100755")

        binary = next(
            change
            for change in result.changes
            if change.destination_path == "binary.bin"
        )
        self.assertEqual(
            binary.binary_treatment,
            "binary-preserved",
        )

    def test_clean_comparisons_return_explicit_empty_changes(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        comparator = GitStateComparator(root)

        self.assertEqual(
            comparator.compare_head_to_index().changes,
            (),
        )
        self.assertEqual(
            comparator.compare_index_to_working_tree().changes,
            (),
        )
        self.assertEqual(
            comparator.compare_head_to_working_tree().changes,
            (),
        )

    def test_direction_and_diff_options_control_identity(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        (root / "tracked.txt").write_bytes(b"changed\n")
        git(root, "add", "tracked.txt")

        comparator = GitStateComparator(root)
        histogram = comparator.compare_head_to_index()
        minimal = comparator.compare_head_to_index(
            options=DiffOptions(algorithm="minimal")
        )

        self.assertNotEqual(
            histogram.comparison.id,
            minimal.comparison.id,
        )
        self.assertNotEqual(
            histogram.changes[0].id,
            minimal.changes[0].id,
        )

    def test_head_and_upstream_reports_ancestor_reachability(
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

        git(root, "checkout", "-q", "upstream")
        (root / "upstream.txt").write_bytes(b"upstream\n")
        git(root, "add", "upstream.txt")
        git(root, "commit", "-qm", "upstream")
        git(root, "checkout", "-q", "master")

        before = snapshot(root)
        comparator = GitStateComparator(root)
        first = comparator.compare_head_and_upstream()
        second = comparator.compare_head_and_upstream()

        self.assertEqual(snapshot(root), before)
        self.assertEqual(first, second)
        self.assertEqual(
            first.comparison.kind,
            "head-and-upstream",
        )
        self.assertFalse(
            first.comparison.ancestry_established
        )
        self.assertEqual(
            first.reachability,
            "head-ancestor-of-upstream",
        )
        self.assertEqual(len(first.changes), 1)
        self.assertEqual(
            first.changes[0].destination_path,
            "upstream.txt",
        )

    def test_head_and_upstream_reports_equal_reachability(
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

        result = (
            GitStateComparator(root)
            .compare_head_and_upstream()
        )

        self.assertEqual(result.reachability, "equal")
        self.assertEqual(result.changes, ())

    def test_head_and_upstream_reports_divergence(
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

        git(root, "checkout", "-q", "upstream")
        (root / "upstream.txt").write_bytes(b"upstream\n")
        git(root, "add", "upstream.txt")
        git(root, "commit", "-qm", "upstream")

        git(root, "checkout", "-q", "master")
        (root / "local.txt").write_bytes(b"local\n")
        git(root, "add", "local.txt")
        git(root, "commit", "-qm", "local")

        result = (
            GitStateComparator(root)
            .compare_head_and_upstream()
        )

        self.assertEqual(result.reachability, "divergent")
        self.assertFalse(
            result.comparison.ancestry_established
        )
        self.assertEqual(
            {
                change.source_path or change.destination_path
                for change in result.changes
            },
            {"local.txt", "upstream.txt"},
        )

    def test_head_and_upstream_requires_configured_upstream(
        self,
    ) -> None:
        temporary, root = repository()
        self.addCleanup(temporary.cleanup)

        with self.assertRaisesRegex(
            Exception,
            "configured upstream is unavailable",
        ):
            GitStateComparator(root).compare_head_and_upstream()

    def test_unsafe_pathspec_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "workspace-relative",
        ):
            DiffOptions(pathspecs=("../outside",))

    def test_rename_detection_is_not_silently_claimed(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "not supported",
        ):
            DiffOptions(rename_detection=True)


if __name__ == "__main__":
    unittest.main()
