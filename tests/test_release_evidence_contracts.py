from __future__ import annotations

import unittest

from release_evidence_test_support import ACCEPTANCE  # noqa: F401
from release_evidence_contracts import (
    REQUIRED_GATES,
    REQUIRED_OBLIGATIONS,
    CommandEvidence,
)


class ReleaseEvidenceContractTests(unittest.TestCase):
    def test_contract_covers_every_gate_and_obligation(self) -> None:
        self.assertEqual(
            REQUIRED_GATES,
            tuple(f"G{i}" for i in range(9)),
        )
        self.assertEqual(
            REQUIRED_OBLIGATIONS,
            tuple(f"GD01-{i:03d}" for i in range(1, 38)),
        )

    def test_command_evidence_serializes_digests_not_output(self) -> None:
        evidence = CommandEvidence(
            "test",
            ("false",),
            7,
            "a",
            "b",
        )
        serialized = evidence.to_dict()
        self.assertEqual(evidence.outcome, "fail")
        self.assertEqual(serialized["stdout_sha256"], "a")
        self.assertNotIn("stdout", serialized)
