from __future__ import annotations

import importlib.util
import pathlib
import unittest

MODULE_PATH = (
    pathlib.Path(__file__).parents[1]
    / "scripts"
    / "acceptance"
    / "gate_runner_contract.py"
)
SPEC = importlib.util.spec_from_file_location(
    "gate_runner_contract_acceptance",
    MODULE_PATH,
)
assert SPEC is not None
assert SPEC.loader is not None
acceptance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(acceptance)


class GateRunnerContractAcceptanceTests(unittest.TestCase):
    def test_contract_owns_no_release_gate_claims(self) -> None:
        self.assertFalse(hasattr(acceptance, "GATE_CLAIMS"))
        self.assertFalse(hasattr(acceptance, "OBLIGATION_CLAIMS"))

    def test_document_validation_accepts_passing_record(self) -> None:
        state = {
            "candidate_commit": "a" * 40,
            "source_tree_identity": "b" * 40,
            "status_sha256": "c" * 64,
        }
        document = {
            "schema": acceptance.SCHEMA,
            "command_exit_code": 0,
            "stdout_sha256": "d" * 64,
            "stderr_sha256": "e" * 64,
            "mutation_sentinel": {
                "before": state,
                "after": dict(state),
                "outcome": "pass",
            },
            "outcome": "pass",
        }
        acceptance.validate_document(document)

    def test_document_validation_rejects_mutation(self) -> None:
        before = {
            "candidate_commit": "a" * 40,
            "source_tree_identity": "b" * 40,
            "status_sha256": "c" * 64,
        }
        after = dict(before)
        after["status_sha256"] = "f" * 64
        document = {
            "schema": acceptance.SCHEMA,
            "command_exit_code": 0,
            "stdout_sha256": "d" * 64,
            "stderr_sha256": "e" * 64,
            "mutation_sentinel": {
                "before": before,
                "after": after,
                "outcome": "fail",
            },
            "outcome": "fail",
        }
        with self.assertRaisesRegex(
            ValueError,
            "mutation sentinel",
        ):
            acceptance.validate_document(document)

    def test_modules_cover_all_runner_boundaries(self) -> None:
        self.assertEqual(
            set(acceptance.TEST_MODULES),
            {
                "tests.test_gate_runner_entrypoint",
                "tests.test_gate_runner_host",
                "tests.test_gate_runner_docker_integration",
            },
        )


if __name__ == "__main__":
    unittest.main()
