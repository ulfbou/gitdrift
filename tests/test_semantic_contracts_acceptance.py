from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "scripts" / "acceptance"
if str(ACCEPTANCE) not in sys.path:
    sys.path.insert(0, str(ACCEPTANCE))

import semantic_contracts as semantic

CANDIDATE = "1" * 40
TREE = "2" * 40
DIGEST = "3" * 64

def valid_document() -> dict[str, object]:
    return {
        "schema": semantic.SEMANTIC_CONTRACTS_SCHEMA,
        "candidate_commit": CANDIDATE,
        "source_tree_identity": TREE,
        "test_cases": list(semantic.TEST_CASES),
        "command": list(semantic.canonical_command()),
        "command_exit_code": 0,
        "stdout_sha256": DIGEST,
        "stderr_sha256": DIGEST,
        "mutation_sentinel": {
            "head_before": CANDIDATE, "head_after": CANDIDATE,
            "tree_before": TREE, "tree_after": TREE,
            "status_before_sha256": DIGEST, "status_after_sha256": DIGEST,
            "head_unchanged": True, "tree_unchanged": True, "status_unchanged": True,
        },
        "coverage": {identity: {"outcome": "pass", "test_cases": list(cases)}
            for identity, cases in sorted(semantic.OBLIGATION_TEST_CASES.items())},
        "obligations": semantic._claims({identity: "pass" for identity in semantic.OBLIGATION_TEST_CASES}),
        "gates": semantic._claims(semantic.GATE_CLAIMS),
        "limitations": list(semantic.LIMITATIONS),
        "outcome": "pass",
    }

class SemanticContractsAcceptanceTests(unittest.TestCase):
    def test_valid_document_is_accepted(self) -> None:
        semantic.validate_document(valid_document(), expected_candidate=CANDIDATE, expected_tree=TREE)

    def test_unknown_field_is_rejected(self) -> None:
        document = valid_document(); document["unknown"] = True
        with self.assertRaisesRegex(semantic.AcceptanceFailure, "fields"):
            semantic.validate_document(document)

    def test_candidate_and_tree_mismatches_are_rejected(self) -> None:
        with self.assertRaisesRegex(semantic.AcceptanceFailure, "candidate"):
            semantic.validate_document(valid_document(), expected_candidate="4" * 40)
        with self.assertRaisesRegex(semantic.AcceptanceFailure, "tree"):
            semantic.validate_document(valid_document(), expected_tree="4" * 40)

    def test_missing_or_expanded_authority_is_rejected(self) -> None:
        document = valid_document(); document["coverage"].pop("GD01-009")
        with self.assertRaisesRegex(semantic.AcceptanceFailure, "coverage"):
            semantic.validate_document(document)
        document = valid_document(); document["obligations"]["GD01-034"] = {"outcome": "pass"}
        with self.assertRaisesRegex(semantic.AcceptanceFailure, "obligation"):
            semantic.validate_document(document)

    def test_failed_command_and_mutation_are_rejected(self) -> None:
        document = valid_document(); document["command_exit_code"] = 1
        with self.assertRaisesRegex(semantic.AcceptanceFailure, "failed"):
            semantic.validate_document(document)
        document = valid_document(); document["mutation_sentinel"]["status_unchanged"] = False
        with self.assertRaisesRegex(semantic.AcceptanceFailure, "mutation"):
            semantic.validate_document(document)

    def test_run_binds_exact_candidate_and_digests(self) -> None:
        completed = mock.Mock(returncode=0, stdout=b"ok", stderr=b"")
        with mock.patch.object(semantic, "_git", side_effect=(CANDIDATE, TREE, "", CANDIDATE, TREE, "")),              mock.patch.object(semantic, "_run_tests", return_value=completed):
            result = semantic.run(ROOT)
        semantic.validate_document(result, expected_candidate=CANDIDATE, expected_tree=TREE)

    def test_failed_tests_cannot_emit_evidence(self) -> None:
        completed = mock.Mock(returncode=1, stdout=b"", stderr=b"failed")
        with mock.patch.object(semantic, "_git", side_effect=(CANDIDATE, TREE, "", CANDIDATE, TREE, "")),              mock.patch.object(semantic, "_run_tests", return_value=completed):
            with self.assertRaisesRegex(semantic.AcceptanceFailure, "focused tests failed"):
                semantic.run(ROOT)

if __name__ == "__main__":
    unittest.main()
