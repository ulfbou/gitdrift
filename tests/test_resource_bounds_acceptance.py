from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = (
    Path(__file__).parents[1]
    / "scripts"
    / "acceptance"
    / "resource_bounds.py"
)
SPEC = importlib.util.spec_from_file_location(
    "resource_bounds_acceptance",
    SCRIPT,
)
assert SPEC and SPEC.loader
acceptance = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = acceptance
SPEC.loader.exec_module(acceptance)


class ResourceBoundsAcceptanceTests(unittest.TestCase):
    def document(self) -> dict[str, object]:
        state = {
            "candidate_commit": "candidate",
            "source_tree_identity": "tree",
            "status_sha256": acceptance._sha256(b""),
        }
        command = [
            sys.executable,
            "-m",
            "unittest",
            "-v",
            *acceptance.TEST_MODULES,
        ]
        return {
            "schema": acceptance.SCHEMA,
            "candidate_commit": "candidate",
            "source_tree_identity": "tree",
            "test_modules": list(
                acceptance.TEST_MODULES
            ),
            "command": command,
            "command_exit_code": 0,
            "stdout_sha256": acceptance._sha256(
                b"stdout"
            ),
            "stderr_sha256": acceptance._sha256(
                b"stderr"
            ),
            "mutation_sentinel": {
                "before": dict(state),
                "after": dict(state),
                "outcome": "pass",
            },
            "obligations": acceptance._claims(
                acceptance.OBLIGATION_CLAIMS
            ),
            "gates": acceptance._claims(
                acceptance.GATE_CLAIMS
            ),
            "limitations": list(
                acceptance.LIMITATIONS
            ),
            "outcome": "pass",
        }

    def test_boundary_remains_partial_and_names_missing_limits(
        self,
    ) -> None:
        self.assertEqual(
            acceptance.OBLIGATION_CLAIMS,
            {"GD01-031": "partial"},
        )
        self.assertEqual(
            acceptance.GATE_CLAIMS,
            {
                "G6": "partial",
                "G7": "partial",
            },
        )
        self.assertTrue(
            any(
                "file-count" in item
                for item in acceptance.LIMITATIONS
            )
        )

    def test_document_validation_rejects_overclaim(
        self,
    ) -> None:
        document = self.document()
        document["obligations"]["GD01-031"][
            "outcome"
        ] = "pass"

        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "obligation claims",
        ):
            acceptance.validate_document(document)

    def test_document_validation_rejects_mutation(
        self,
    ) -> None:
        document = self.document()
        document["mutation_sentinel"]["after"] = {
            "candidate_commit": "different"
        }

        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "does not close",
        ):
            acceptance.validate_document(document)

    def test_failed_tests_cannot_emit_evidence(
        self,
    ) -> None:
        completed = mock.Mock(
            returncode=1,
            stdout=b"stdout",
            stderr=b"stderr",
        )
        with mock.patch.object(
            acceptance,
            "_git",
            side_effect=(
                "candidate",
                "tree",
                "",
                "candidate",
                "tree",
                "",
            ),
        ), mock.patch.object(
            acceptance.subprocess,
            "run",
            return_value=completed,
        ):
            with self.assertRaisesRegex(
                acceptance.AcceptanceFailure,
                "tests failed",
            ):
                acceptance.run(Path("."))


if __name__ == "__main__":
    unittest.main()
