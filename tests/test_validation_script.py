import importlib.util
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "scripts"
    / "validation"
    / "validate.py"
)

SPEC = importlib.util.spec_from_file_location(
    "gitdrift_validation",
    SCRIPT,
)

assert SPEC
assert SPEC.loader

validation = importlib.util.module_from_spec(
    SPEC
)

sys.modules[SPEC.name] = validation
SPEC.loader.exec_module(validation)


class ValidationScriptTests(unittest.TestCase):
    def repository(
        self,
    ) -> tuple[
        tempfile.TemporaryDirectory[str],
        Path,
    ]:
        temporary = (
            tempfile.TemporaryDirectory()
        )
        root = Path(temporary.name)

        (
            root
            / "src"
            / "gitdrift"
            / "domain"
        ).mkdir(parents=True)

        (root / "tests").mkdir()
        (root / "scripts").mkdir()
        (root / "docs").mkdir()

        return temporary, root

    def test_compilation_reports_syntax_failure(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        (
            root
            / "src"
            / "gitdrift"
            / "broken.py"
        ).write_text(
            "def broken(:\n",
            encoding="utf-8",
        )

        with self.assertRaises(
            validation.ValidationFailure
        ):
            validation.compile_python(root)

    def test_domain_adapter_import_is_rejected(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        (
            root
            / "src"
            / "gitdrift"
            / "domain"
            / "bad.py"
        ).write_text(
            "from gitdrift.adapters "
            "import git\n",
            encoding="utf-8",
        )

        with self.assertRaises(
            validation.ValidationFailure
        ):
            validation.architectural_imports(
                root
            )

    def test_broken_relative_document_link_is_rejected(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        (
            root
            / "docs"
            / "README.md"
        ).write_text(
            "[missing](missing.md)\n",
            encoding="utf-8",
        )

        with self.assertRaises(
            validation.ValidationFailure
        ):
            validation.documentation_links(
                root
            )

    def test_unit_test_gate_injects_source_tree_into_pythonpath(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            package = (
                root
                / "src"
                / "example_package"
            )
            package.mkdir(parents=True)

            (package / "__init__.py").write_text(
                "VALUE = 42\n",
                encoding="utf-8",
            )

            tests = root / "tests"
            tests.mkdir()

            (tests / "test_import.py").write_text(
                "import unittest\n"
                "import example_package\n"
                "\n"
                "class ImportTests(unittest.TestCase):\n"
                "    def test_source_import(self):\n"
                "        self.assertEqual("
                "example_package.VALUE, 42"
                ")\n",
                encoding="utf-8",
            )

            with mock.patch.dict(
                os.environ,
                {
                    "PYTHONPATH": "",
                },
            ):
                validation.run_tests(root)

    def test_changed_paths_unions_base_staged_unstaged_and_untracked(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validation.subprocess.run(
                ["git", "init", "-q"], cwd=root, check=True
            )
            validation.subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=root, check=True,
            )
            validation.subprocess.run(
                ["git", "config", "user.name", "Test"],
                cwd=root, check=True,
            )
            (root / "base.txt").write_text("base\n", encoding="utf-8")
            validation.subprocess.run(
                ["git", "add", "base.txt"], cwd=root, check=True
            )
            validation.subprocess.run(
                ["git", "commit", "-qm", "base"], cwd=root, check=True
            )
            base = validation.subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True,
                text=True, capture_output=True,
            ).stdout.strip()
            (root / "pr.txt").write_text("pr\n", encoding="utf-8")
            validation.subprocess.run(
                ["git", "add", "pr.txt"], cwd=root, check=True
            )
            validation.subprocess.run(
                ["git", "commit", "-qm", "pr"], cwd=root, check=True
            )
            (root / "staged.txt").write_text("staged\n", encoding="utf-8")
            validation.subprocess.run(
                ["git", "add", "staged.txt"], cwd=root, check=True
            )
            (root / "base.txt").write_text("changed\n", encoding="utf-8")
            (root / "untracked.txt").write_text("new\n", encoding="utf-8")
            scope = validation.changed_paths(
                root, base_ref=base, include_staged=True, include_unstaged=True
            )
            self.assertEqual(
                scope.paths,
                frozenset({
                    Path("pr.txt"), Path("staged.txt"),
                    Path("base.txt"), Path("untracked.txt"),
                }),
            )

    def test_changed_file_coverage_rejects_carrier_inside_repository(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)
        (root / "blob.dx").write_text(
            "%%DX v2.0.0\n%%END\n",
            encoding="utf-8",
        )
        scope = validation.ValidationScope(
            frozenset({Path("blob.dx")})
        )
        with self.assertRaisesRegex(
            validation.ValidationFailure,
            "CARRIER_SOURCE_DIR",
        ):
            validation.changed_file_coverage(root, scope)

    def test_changed_file_coverage_rejects_dx_txt_inside_repository(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)
        (root / "candidate.dx.txt").write_text(
            "%%DX v2.0.0\n%%END\n",
            encoding="utf-8",
        )
        scope = validation.ValidationScope(
            frozenset({Path("candidate.dx.txt")})
        )
        with self.assertRaises(validation.ValidationFailure):
            validation.changed_file_coverage(root, scope)

    def test_changed_file_coverage_rejects_non_utf8(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)
        (root / "binary.bin").write_bytes(b"\xff")
        scope = validation.ValidationScope(
            frozenset({Path("binary.bin")})
        )
        validation.changed_file_coverage(root, scope)

    def test_existing_relative_document_link_passes(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        (
            root
            / "docs"
            / "target.md"
        ).write_text(
            "# Target\n",
            encoding="utf-8",
        )

        (
            root
            / "docs"
            / "README.md"
        ).write_text(
            "[target](target.md)\n",
            encoding="utf-8",
        )

        validation.documentation_links(root)


    def test_changed_file_coverage_reports_binary_without_failing(self) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)
        (root / "binary.bin").write_bytes(b"\x00\xff")
        scope = validation.ValidationScope(
            (validation.ChangedPath(Path("binary.bin"), "A", source="untracked"),)
        )
        validation.changed_file_coverage(root, scope)

    def test_changed_file_coverage_reports_deletion_without_missing_file_failure(self) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)
        scope = validation.ValidationScope(
            (validation.ChangedPath(Path("removed.txt"), "D", source="base-ref"),)
        )
        validation.changed_file_coverage(root, scope)

    def test_changed_paths_discovers_committed_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for args in (("init", "-q"), ("config", "user.email", "test@example.com"), ("config", "user.name", "Test")):
                validation.subprocess.run(["git", *args], cwd=root, check=True)
            (root / "removed.txt").write_text("content\n", encoding="utf-8")
            validation.subprocess.run(["git", "add", "removed.txt"], cwd=root, check=True)
            validation.subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            base = validation.subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True,
                text=True, capture_output=True,
            ).stdout.strip()
            (root / "removed.txt").unlink()
            validation.subprocess.run(["git", "add", "-u"], cwd=root, check=True)
            validation.subprocess.run(["git", "commit", "-qm", "delete"], cwd=root, check=True)
            scope = validation.changed_paths(
                root, base_ref=base, include_staged=False, include_unstaged=False
            )
            change = scope.change_for(Path("removed.txt"))
            self.assertIsNotNone(change)
            self.assertEqual(change.status, "D")

    def test_changed_paths_characterizes_each_local_scope_independently(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for args in (("init", "-q"), ("config", "user.email", "test@example.com"), ("config", "user.name", "Test")):
                validation.subprocess.run(["git", *args], cwd=root, check=True)
            (root / "tracked.txt").write_text("base\n", encoding="utf-8")
            validation.subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True)
            validation.subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            base = validation.subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True,
                text=True, capture_output=True,
            ).stdout.strip()
            (root / "committed.txt").write_text("committed\n", encoding="utf-8")
            validation.subprocess.run(["git", "add", "committed.txt"], cwd=root, check=True)
            validation.subprocess.run(["git", "commit", "-qm", "candidate"], cwd=root, check=True)
            (root / "staged.txt").write_text("staged\n", encoding="utf-8")
            validation.subprocess.run(["git", "add", "staged.txt"], cwd=root, check=True)
            (root / "tracked.txt").write_text("unstaged\n", encoding="utf-8")
            (root / "untracked.txt").write_text("untracked\n", encoding="utf-8")

            base_scope = validation.changed_paths(root, base_ref=base, include_staged=False, include_unstaged=False)
            staged_scope = validation.changed_paths(root, base_ref=None, include_staged=True, include_unstaged=False)
            worktree_scope = validation.changed_paths(root, base_ref=None, include_staged=False, include_unstaged=True)

            self.assertEqual(base_scope.paths, frozenset({Path("committed.txt")}))
            self.assertEqual(staged_scope.paths, frozenset({Path("staged.txt")}))
            self.assertEqual(worktree_scope.paths, frozenset({Path("tracked.txt"), Path("untracked.txt")}))

    def test_validation_pass_and_failure_paths_preserve_candidate_bytes_and_git_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            validation.subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            validation.subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            validation.subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            candidate = root / "candidate.bin"
            candidate.write_bytes(b"\x00candidate\r\n")
            validation.subprocess.run(["git", "add", "candidate.bin"], cwd=root, check=True)
            validation.subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            candidate.write_bytes(b"\xffchanged\r\n")
            index_path = Path(validation.subprocess.run(
                ["git", "rev-parse", "--git-path", "index"], cwd=root, check=True,
                text=True, capture_output=True,
            ).stdout.strip())
            if not index_path.is_absolute():
                index_path = root / index_path

            def snapshot():
                return (
                    validation.subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, text=True, capture_output=True).stdout,
                    index_path.read_bytes(),
                    validation.subprocess.run(["git", "status", "--porcelain=v1", "-z"], cwd=root, check=True, stdout=validation.subprocess.PIPE).stdout,
                    candidate.read_bytes(),
                )

            def passing_gate(current_root, scope):
                self.assertEqual((current_root / "candidate.bin").read_bytes(), b"\xffchanged\r\n")

            def failing_gate(current_root, scope):
                self.assertEqual((current_root / "candidate.bin").read_bytes(), b"\xffchanged\r\n")
                raise validation.ValidationFailure("characterized failure")

            before = snapshot()
            with mock.patch("scripts.validation.orchestration.gates", return_value=(validation.Gate("sentinel", passing_gate),)):
                self.assertEqual(validation.validate(root), 0)
            self.assertEqual(snapshot(), before)
            with mock.patch("scripts.validation.orchestration.gates", return_value=(validation.Gate("sentinel", failing_gate),)):
                self.assertEqual(validation.validate(root), 1)
            self.assertEqual(snapshot(), before)

    def test_validate_runs_all_selected_gates_after_multiple_failures(self) -> None:
        calls: list[str] = []
        def fail_one(root, scope):
            calls.append("one")
            raise validation.ValidationFailure("one")
        def fail_two(root, scope):
            calls.append("two")
            raise validation.ValidationFailure("two")
        with mock.patch.object(
            validation, "gates",
            return_value=(validation.Gate("one", fail_one), validation.Gate("two", fail_two)),
        ):
            # validate is owned by orchestration, so patch its imported gate factory.
            with mock.patch("scripts.validation.orchestration.gates", validation.gates):
                self.assertEqual(validation.validate(Path.cwd()), 1)
        self.assertEqual(calls, ["one", "two"])

if __name__ == "__main__":
    unittest.main()
