from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from release_evidence_test_support import ACCEPTANCE  # noqa: F401
from release_evidence_contracts import ReleaseEvidenceFailure
from release_evidence_documents import load_evidence


class EvidenceDocumentTests(unittest.TestCase):
    def _write(self, value: object) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "evidence.json"
        path.write_text(
            json.dumps(value),
            encoding="utf-8",
        )
        return path

    def test_matching_evidence_is_loaded(self) -> None:
        path = self._write(
            {
                "schema": "expected",
                "candidate_commit": "c",
                "outcome": "pass",
            }
        )
        self.assertEqual(
            load_evidence(
                path,
                "expected",
                "c",
            )["outcome"],
            "pass",
        )

    def test_mismatched_evidence_is_rejected(self) -> None:
        path = self._write(
            {
                "schema": "other",
                "candidate_commit": "c",
                "outcome": "pass",
            }
        )
        with self.assertRaisesRegex(
            ReleaseEvidenceFailure,
            "mismatched fields",
        ):
            load_evidence(
                path,
                "expected",
                "c",
            )
