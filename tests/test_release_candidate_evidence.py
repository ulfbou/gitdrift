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
    / "release_candidate.py"
)
SPEC = importlib.util.spec_from_file_location(
    "gitdrift_release_candidate",
    SCRIPT,
)
assert SPEC
assert SPEC.loader
release = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = release
SPEC.loader.exec_module(release)

class ReleaseCandidateEvidenceTests(unittest.TestCase):
    def test_contract_covers_every_gate_and_obligation(
        self,
    ) -> None:
        self.assertEqual(
            release.REQUIRED_GATES,
            tuple(f"G{i}" for i in range(9)),
        )
        self.assertEqual(
            release.REQUIRED_OBLIGATIONS,
            tuple(
                f"GD01-{i:03d}"
                for i in range(1, 38)
            ),
        )

    def test_command_evidence_uses_exit_status_and_bounded_digests(
        self,
    ) -> None:
        evidence = release.CommandEvidence(
            "test",
            ("python", "-m", "unittest"),
            0,
            "a",
            "b",
        )
        self.assertEqual(evidence.outcome, "pass")
        self.assertEqual(
            evidence.to_dict()["stderr_sha256"],
            "b",
        )

    def test_mixed_candidate_evidence_is_rejected(
        self,
    ) -> None:
        with mock.patch.object(
            Path,
            "read_text",
            return_value=(
                '{"schema":"expected",'
                '"candidate_commit":"other",'
                '"outcome":"pass"}'
            ),
        ):
            with self.assertRaisesRegex(
                release.ReleaseEvidenceFailure,
                "mixed candidate",
            ):
                release._load(
                    Path("evidence.json"),
                    "expected",
                    "candidate",
                )

    def test_incomplete_release_closure_is_blocked_not_passed(
        self,
    ) -> None:
        record = release._record(
            "blocked",
            (),
            "missing evidence",
        )
        self.assertEqual(
            record["outcome"],
            "blocked",
        )
        self.assertEqual(
            record["evidence_ids"],
            [],
        )
        self.assertEqual(
            record["limitation"],
            "missing evidence",
        )

    def test_failed_command_cannot_be_pass_evidence(
        self,
    ) -> None:
        evidence = release.CommandEvidence(
            "test",
            ("false",),
            7,
            "a",
            "b",
        )
        self.assertEqual(
            evidence.outcome,
            "fail",
        )

if __name__ == "__main__":
    unittest.main()
