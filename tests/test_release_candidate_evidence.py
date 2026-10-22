from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from release_evidence_test_support import ACCEPTANCE, ROOT  # noqa: F401
import release_candidate_evidence as release
from release_evidence_contracts import ReleaseEvidenceFailure


class ReleaseAggregationTests(unittest.TestCase):
    def test_acceptance_commands_are_explicit_and_ordered(self) -> None:
        specifications = release._command_specs(
            Path("synthetic"),
            Path("installed"),
        )
        self.assertEqual(
            tuple(item.identity for item in specifications),
            (
                "canonical-validation",
                "synthetic-state-awareness",
                "installed-distribution",
            ),
        )

    def test_dirty_candidate_is_rejected_before_commands_run(self) -> None:
        with mock.patch.object(
            release,
            "git",
            side_effect=("candidate", "dirty"),
        ):
            with self.assertRaisesRegex(
                ReleaseEvidenceFailure,
                "clean committed candidate",
            ):
                release.aggregate(ROOT)
