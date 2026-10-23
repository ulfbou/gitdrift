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
    / "contract_quality.py"
)
SPEC = importlib.util.spec_from_file_location(
    "gitdrift_contract_quality_acceptance",
    SCRIPT,
)
assert SPEC
assert SPEC.loader
acceptance = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = acceptance
SPEC.loader.exec_module(acceptance)


class ContractQualityAcceptanceTests(unittest.TestCase):
    def test_boundary_declares_truthful_pass_and_partial_claims(self) -> None:
        self.assertEqual(
            acceptance.OBLIGATION_CLAIMS,
            {
                "GD01-024": "pass",
                "GD01-029": "pass",
                "GD01-032": "pass",
                "GD01-035": "pass",
            },
        )
        self.assertEqual(
            acceptance.GATE_CLAIMS,
            {"G5": "pass", "G6": "partial"},
        )
        self.assertTrue(acceptance.LIMITATIONS)

    def test_boundary_uses_existing_focused_evidence_modules(self) -> None:
        required = {
            "tests.test_identity",
            "tests.test_embedded_instruction_safety",
            "tests.test_native_investigation",
            "tests.test_native_compatibility",
            "tests.test_python_extractor",
            "tests.test_working_tree_capture",
        }
        self.assertLessEqual(
            required,
            set(acceptance.TEST_MODULES),
        )
        self.assertNotIn(
            "tests.test_state_awareness_corpus_acceptance",
            acceptance.TEST_MODULES,
        )

    def test_document_validation_rejects_overclaim(self) -> None:
        document = self.document()
        document["gates"]["G6"]["outcome"] = "pass"
        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "gate claims",
        ):
            acceptance.validate_document(document)

    def test_document_validation_rejects_mutation(self) -> None:
        document = self.document()
        document["mutation_sentinel"]["after"] = {
            "candidate_commit": "different",
            "source_tree_identity": "tree",
            "status_sha256": "status",
        }
        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "does not close",
        ):
            acceptance.validate_document(document)

    def test_failed_focused_tests_cannot_emit_evidence(self) -> None:
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
            acceptance,
            "_run_tests",
            return_value=completed,
        ):
            with self.assertRaisesRegex(
                acceptance.AcceptanceFailure,
                "test boundary failed",
            ):
                acceptance.run(Path("."))

    def document(self) -> dict[str, object]:
        state = {
            "candidate_commit": "candidate",
            "source_tree_identity": "tree",
            "status_sha256": acceptance._sha256(b""),
        }
        return {
            "schema": acceptance.SCHEMA,
            "candidate_commit": "candidate",
            "source_tree_identity": "tree",
            "test_modules": list(acceptance.TEST_MODULES),
            "test_exit_code": 0,
            "stdout_sha256": acceptance._sha256(b"stdout"),
            "stderr_sha256": acceptance._sha256(b"stderr"),
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
            "limitations": list(acceptance.LIMITATIONS),
            "outcome": "pass",
        }


if __name__ == "__main__":
    unittest.main()
