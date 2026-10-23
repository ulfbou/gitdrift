from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
from unittest import mock

from release_evidence_test_support import ACCEPTANCE, ROOT  # noqa: F401
import release_candidate_evidence as release
from release_evidence_contracts import ReleaseEvidenceFailure


class ReleaseAggregationTests(unittest.TestCase):
    def test_acceptance_commands_are_explicit_and_ordered(self) -> None:
        specifications = release._command_specs(
            Path("synthetic"),
            Path("semantic-contracts"),
            Path("installed"),
            Path("corpus"),
            Path("contract-quality"),
            Path("resource-bounds"),
            Path("corpus-root"),
        )
        self.assertEqual(
            tuple(item.identity for item in specifications),
            (
                "canonical-validation",
                "synthetic-state-awareness",
                "semantic-contracts",
                "installed-distribution",
                "contract-quality",
                "resource-bounds",
                "dx-artifacts-corpus",
            ),
        )

    def test_corpus_command_is_bound_to_the_immutable_identity(self) -> None:
        specification = release._command_specs(
            Path("synthetic"),
            Path("semantic-contracts"),
            Path("installed"),
            Path("corpus"),
            Path("contract-quality"),
            Path("resource-bounds"),
            Path("corpus-root"),
        )[-1]
        self.assertIn(release.CORPUS_COMMIT, specification.arguments)
        self.assertIn(release.CORPUS_TREE, specification.arguments)
        self.assertIn("corpus-root", specification.arguments)

    def test_collect_inputs_wires_semantic_contract_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence_root = Path(directory)
            expected_paths = (
                evidence_root / "synthetic.json",
                evidence_root / "semantic-contracts.json",
                evidence_root / "installed.json",
                evidence_root / "corpus.json",
                evidence_root / "contract-quality.json",
                evidence_root / "resource-bounds.json",
                Path("corpus-root"),
            )
            documents = (
                {"schema": "synthetic"},
                {"schema": "semantic-contracts"},
                {"schema": "installed"},
                {"schema": "corpus"},
                {"schema": "contract-quality"},
                {"schema": "resource-bounds"},
                {"schema": "platform-matrix"},
            )

            with mock.patch.object(
                release,
                "_command_specs",
                return_value=(),
            ) as command_specs, mock.patch.object(
                release,
                "load_evidence",
                side_effect=documents,
            ) as load_evidence, mock.patch.object(
                release,
                "validate_platform_matrix",
                return_value={"schema": "platform-matrix"},
            ) as validate_platform:
                inputs = release._collect_inputs(
                    ROOT,
                    "candidate",
                    "tree",
                    evidence_root,
                    Path("corpus-root"),
                    Path("platform-matrix"),
                )

            command_specs.assert_called_once_with(*expected_paths)
            self.assertEqual(load_evidence.call_count, 7)
            self.assertEqual(
                inputs.semantic_contracts,
                {"schema": "semantic-contracts"},
            )
            self.assertEqual(
                inputs.installed,
                {"schema": "installed"},
            )
            self.assertEqual(
                inputs.resource_bounds,
                {"schema": "resource-bounds"},
            )
            self.assertEqual(
                inputs.platform_matrix,
                {"schema": "platform-matrix"},
            )
            validate_platform.assert_called_once_with(
                {"schema": "platform-matrix"},
                candidate="candidate",
                source_tree="tree",
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
