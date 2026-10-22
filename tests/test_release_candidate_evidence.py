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
            Path("corpus"),
            Path("corpus-root"),
        )
        self.assertEqual(
            tuple(item.identity for item in specifications),
            (
                "canonical-validation",
                "synthetic-state-awareness",
                "installed-distribution",
                "dx-artifacts-corpus",
            ),
        )

    def test_corpus_command_is_bound_to_the_immutable_identity(self) -> None:
        specification = release._command_specs(
            Path("synthetic"),
            Path("installed"),
            Path("corpus"),
            Path("corpus-root"),
        )[-1]
        self.assertIn(release.CORPUS_COMMIT, specification.arguments)
        self.assertIn(release.CORPUS_TREE, specification.arguments)
        self.assertIn("corpus-root", specification.arguments)

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

    def test_missing_corpus_is_rejected_before_commands_run(self) -> None:
        with mock.patch.object(
            release,
            "git",
            side_effect=("candidate", ""),
        ), mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(
                ReleaseEvidenceFailure,
                release.CORPUS_ROOT_ENV,
            ):
                release.aggregate(ROOT)


if __name__ == "__main__":
    unittest.main()
