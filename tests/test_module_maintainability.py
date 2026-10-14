from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.validation import gates as gate_module
from scripts.validation import validate as validate_module
from scripts.validation.model import (
    ValidationFailure,
    ValidationScope,
)
from scripts.validation.module_maintainability import (
    POLICY_ID,
    POLICY_PATH,
    classify_python_module,
    load_policy,
    module_maintainability,
)


EXPECTED_GATE_ORDER = (
    "changed-file-coverage",
    "python-compilation",
    "module-maintainability",
    "unit-tests",
    "architectural-imports",
    "public-api",
    "compatibility-aliases",
    "documentation-links",
    "git-diff-check",
)


def write_policy(
    root: Path,
    *,
    implementation_bytes: int = 1024,
    implementation_lines: int = 20,
    tooling_bytes: int = 1024,
    tooling_lines: int = 20,
    test_bytes: int = 1024,
    test_lines: int = 20,
    exceptions: list[dict[str, object]] | None = None,
) -> None:
    path = root / POLICY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "policy_id": POLICY_ID,
                "limits": {
                    "implementation": {
                        "maximum_bytes": implementation_bytes,
                        "maximum_lines": implementation_lines,
                    },
                    "repository-tooling": {
                        "maximum_bytes": tooling_bytes,
                        "maximum_lines": tooling_lines,
                    },
                    "test": {
                        "maximum_bytes": test_bytes,
                        "maximum_lines": test_lines,
                    },
                },
                "exceptions": exceptions or [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


class ModuleMaintainabilityTests(unittest.TestCase):
    def repository(
        self,
    ) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "src" / "gitdrift").mkdir(parents=True)
        (root / "scripts" / "tools").mkdir(parents=True)
        (root / "tests" / "fixtures").mkdir(parents=True)
        write_policy(root)
        return temporary, root

    def test_classification_uses_explicit_repository_roles(
        self,
    ) -> None:
        self.assertEqual(
            classify_python_module(
                Path("src/gitdrift/domain.py")
            ),
            "implementation",
        )
        self.assertEqual(
            classify_python_module(
                Path("scripts/tools/check.py")
            ),
            "repository-tooling",
        )
        self.assertEqual(
            classify_python_module(
                Path("tests/test_domain.py")
            ),
            "test",
        )
        self.assertIsNone(
            classify_python_module(
                Path("tests/fixtures/generated.py")
            )
        )
        self.assertIsNone(
            classify_python_module(
                Path("docs/example.py")
            )
        )
        self.assertIsNone(
            classify_python_module(
                Path("src/gitdrift/schema.json")
            )
        )

    def test_exact_bytes_and_physical_lines_are_enforced(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        candidate = root / "src" / "gitdrift" / "large.py"
        candidate.write_bytes(b"one\r\ntwo\r\nthree")

        write_policy(
            root,
            implementation_bytes=15,
            implementation_lines=2,
        )

        with self.assertRaisesRegex(
            ValidationFailure,
            (
                r"path=src/gitdrift/large\.py .*"
                r"bytes=15 .*"
                r"maximum_bytes=15 .*"
                r"lines=3 .*"
                r"maximum_lines=2 .*"
                r"exception=none"
            ),
        ):
            module_maintainability(root)

    def test_binary_non_utf8_python_is_measured_without_decoding(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        candidate = root / "src" / "gitdrift" / "bytes.py"
        candidate.write_bytes(b"\xff\xfe\n")

        write_policy(
            root,
            implementation_bytes=3,
            implementation_lines=1,
        )

        module_maintainability(root)

    def test_fixture_python_is_not_silently_classified_as_test_code(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        fixture = root / "tests" / "fixtures" / "generated.py"
        fixture.write_bytes(b"x\n" * 100)

        write_policy(
            root,
            test_bytes=1,
            test_lines=1,
        )

        module_maintainability(root)

    def test_exact_path_exception_is_bounded_and_reported(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        candidate = root / "src" / "gitdrift" / "legacy.py"
        candidate.write_bytes(b"x\n" * 4)

        write_policy(
            root,
            implementation_bytes=4,
            implementation_lines=2,
            exceptions=[
                {
                    "path": "src/gitdrift/legacy.py",
                    "maximum_bytes": 8,
                    "maximum_lines": 4,
                    "expires_after": "issue-99",
                    "reason": "split tracked by issue 99",
                }
            ],
        )

        module_maintainability(root)

    def test_exception_cannot_hide_growth_beyond_its_bound(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        candidate = root / "src" / "gitdrift" / "legacy.py"
        candidate.write_bytes(b"x\n" * 5)

        write_policy(
            root,
            implementation_bytes=4,
            implementation_lines=2,
            exceptions=[
                {
                    "path": "src/gitdrift/legacy.py",
                    "maximum_bytes": 8,
                    "maximum_lines": 4,
                    "expires_after": "issue-99",
                    "reason": "split tracked by issue 99",
                }
            ],
        )

        with self.assertRaisesRegex(
            ValidationFailure,
            r"exception=active;expires_after=issue-99",
        ):
            module_maintainability(root)

    def test_validation_modules_cannot_exempt_themselves(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        write_policy(
            root,
            exceptions=[
                {
                    "path": (
                        "scripts/validation/"
                        "module_maintainability.py"
                    ),
                    "maximum_bytes": 999999,
                    "maximum_lines": 999999,
                    "expires_after": "never",
                    "reason": "self exemption",
                }
            ],
        )

        with self.assertRaisesRegex(
            ValidationFailure,
            "validation modules cannot receive",
        ):
            load_policy(root)

    def test_missing_exception_path_fails(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        write_policy(
            root,
            exceptions=[
                {
                    "path": "src/gitdrift/missing.py",
                    "maximum_bytes": 8,
                    "maximum_lines": 4,
                    "expires_after": "issue-99",
                    "reason": "missing target",
                }
            ],
        )

        with self.assertRaisesRegex(
            ValidationFailure,
            (
                "exception path does not exist: "
                "src/gitdrift/missing.py"
            ),
        ):
            module_maintainability(root)

    def test_scope_limits_measurement_to_selected_paths(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        selected = root / "src" / "gitdrift" / "selected.py"
        excluded = root / "src" / "gitdrift" / "excluded.py"
        selected.write_bytes(b"x\n")
        excluded.write_bytes(b"x\n" * 100)

        write_policy(
            root,
            implementation_bytes=4,
            implementation_lines=2,
        )

        scope = ValidationScope(
            frozenset(
                {
                    Path("src/gitdrift/selected.py"),
                }
            )
        )
        module_maintainability(root, scope)

    def test_policy_rejects_unknown_version(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        path = root / POLICY_PATH
        document = json.loads(path.read_text(encoding="utf-8"))
        document["policy_id"] = "unknown-policy"
        path.write_text(
            json.dumps(document),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            ValidationFailure,
            "unsupported maintainability policy_id",
        ):
            load_policy(root)

    def test_gate_registration_preserves_exact_canonical_order(
        self,
    ) -> None:
        registered = gate_module.gates()

        self.assertEqual(
            tuple(gate.name for gate in registered),
            EXPECTED_GATE_ORDER,
        )

    def test_gate_registration_is_unique_and_uses_canonical_action(
        self,
    ) -> None:
        registered = [
            gate
            for gate in gate_module.gates()
            if gate.name == "module-maintainability"
        ]

        self.assertEqual(len(registered), 1)
        self.assertIs(
            registered[0].action,
            module_maintainability,
        )

    def test_cli_accepts_and_selects_only_module_maintainability_gate(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        captured: dict[str, object] = {}

        def capture_validation(
            current_root: Path,
            selected: set[str] | None,
            scope: ValidationScope,
        ) -> int:
            captured["root"] = current_root
            captured["selected"] = selected
            captured["scope"] = scope
            return 0

        with mock.patch.object(
            validate_module,
            "validate",
            side_effect=capture_validation,
        ):
            result = validate_module.main(
                [
                    "--root",
                    str(root),
                    "--gate",
                    "module-maintainability",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(captured["root"], root.resolve())
        self.assertEqual(
            captured["selected"],
            {"module-maintainability"},
        )
        scope = captured["scope"]
        self.assertIsInstance(scope, ValidationScope)
        self.assertIsNone(scope.changes)
        self.assertIsNone(scope.base_ref)
        self.assertFalse(scope.include_staged)
        self.assertFalse(scope.include_unstaged)


if __name__ == "__main__":
    unittest.main()
