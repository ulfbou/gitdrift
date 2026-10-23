from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).parents[1]
    / "scripts"
    / "acceptance"
    / "platform_observation.py"
)
SPEC = importlib.util.spec_from_file_location(
    "platform_observation_acceptance",
    SCRIPT,
)
assert SPEC and SPEC.loader
acceptance = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = acceptance
SPEC.loader.exec_module(acceptance)


class PlatformObservationAcceptanceTests(
    unittest.TestCase
):
    def document(self) -> dict[str, object]:
        state = {
            "candidate_commit": "candidate",
            "source_tree_identity": "tree",
            "status_sha256": acceptance._sha256(
                b""
            ),
        }
        return {
            "schema": acceptance.SCHEMA,
            "candidate_commit": "candidate",
            "source_tree_identity": "tree",
            "platform": {
                "system": "Linux",
                "release": "test",
                "machine": "x86_64",
            },
            "python": {
                "implementation": "CPython",
                "version": "3.11.0",
            },
            "git": {
                "version": "git version test"
            },
            "semantic_probe": {
                "modules": list(acceptance.SEMANTIC_PROBE_MODULES),
                "exit_code": 0,
                "stdout_sha256": acceptance._sha256(b""),
                "stderr_sha256": acceptance._sha256(b""),
            },
            "filesystem": {
                "case_normalization": "GitDrift",
                "path_separator": "/",
                "symlink_supported": True,
            },
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

    def test_single_observation_remains_partial(
        self,
    ) -> None:
        self.assertEqual(
            acceptance.OBLIGATION_CLAIMS,
            {"GD01-034": "partial"},
        )
        self.assertEqual(
            acceptance.GATE_CLAIMS,
            {"G7": "partial"},
        )
        self.assertTrue(
            any(
                "matrix" in item
                for item in acceptance.LIMITATIONS
            )
        )

    def test_validation_rejects_overclaim(
        self,
    ) -> None:
        document = self.document()
        document["gates"]["G7"][
            "outcome"
        ] = "pass"

        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "gate claims",
        ):
            acceptance.validate_document(
                document
            )

    def test_validation_rejects_missing_platform_identity(
        self,
    ) -> None:
        document = self.document()
        document["platform"] = {}

        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "lacks platform",
        ):
            acceptance.validate_document(
                document
            )

    def test_validation_rejects_mutation(
        self,
    ) -> None:
        document = self.document()
        document["mutation_sentinel"][
            "after"
        ] = {
            "candidate_commit": "different"
        }

        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "does not close",
        ):
            acceptance.validate_document(
                document
            )


if __name__ == "__main__":
    unittest.main()
