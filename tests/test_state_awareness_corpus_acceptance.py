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
    / "state_awareness_corpus.py"
)
SPEC = importlib.util.spec_from_file_location(
    "gitdrift_state_awareness_corpus_acceptance",
    SCRIPT,
)
assert SPEC
assert SPEC.loader
acceptance = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = acceptance
SPEC.loader.exec_module(acceptance)


class CorpusAcceptanceTests(unittest.TestCase):
    def test_verify_corpus_rejects_commit_mismatch(self) -> None:
        with mock.patch.object(
            acceptance,
            "_git",
            side_effect=("actual", "tree", "", "", "origin"),
        ):
            with self.assertRaisesRegex(
                acceptance.AcceptanceFailure,
                "commit",
            ):
                acceptance._verify_corpus(
                    Path("."),
                    "expected",
                    "tree",
                )

    def test_verify_corpus_rejects_mutable_or_dirty_checkout(self) -> None:
        for branch, status, message in (
            ("master", "", "detached"),
            ("", "dirty", "clean"),
        ):
            with self.subTest(message=message), mock.patch.object(
                acceptance,
                "_git",
                side_effect=("commit", "tree", branch, status, "origin"),
            ):
                with self.assertRaisesRegex(
                    acceptance.AcceptanceFailure,
                    message,
                ):
                    acceptance._verify_corpus(
                        Path("."),
                        "commit",
                        "tree",
                    )

    def test_run_binds_candidate_corpus_and_mutation_evidence(self) -> None:
        native = {"schema": "gitdrift-investigation-v1"}
        payload = b'{"schema":"gitdrift-investigation-v1"}'
        snapshots = (
            {"head": "candidate"},
            {"head": "corpus"},
            {"head": "candidate"},
            {"head": "corpus"},
        )
        with mock.patch.object(
            acceptance,
            "_git",
            side_effect=("candidate", "source-tree", ""),
        ), mock.patch.object(
            acceptance,
            "_verify_corpus",
            return_value={
                "repository": "origin",
                "commit": "corpus-commit",
                "tree": "corpus-tree",
            },
        ), mock.patch.object(
            acceptance,
            "_snapshot",
            side_effect=snapshots,
        ), mock.patch.object(
            acceptance,
            "_run_profile",
            side_effect=((native, payload), (native, payload)),
        ):
            document = acceptance.run(
                Path("."),
                Path("."),
                "corpus-commit",
                "corpus-tree",
            )
        self.assertEqual(document["candidate_commit"], "candidate")
        self.assertEqual(document["source_tree_identity"], "source-tree")
        self.assertEqual(document["corpus"]["commit"], "corpus-commit")
        self.assertEqual(document["obligations"], ["GD01-033"])
        self.assertEqual(document["gates"], ["G4"])
        self.assertEqual(document["outcome"], "pass")

    def test_run_rejects_nondeterministic_output(self) -> None:
        snapshots = ({}, {}, {}, {})
        with mock.patch.object(
            acceptance,
            "_git",
            side_effect=("candidate", "source-tree", ""),
        ), mock.patch.object(
            acceptance,
            "_verify_corpus",
            return_value={"repository": "origin", "commit": "commit", "tree": "tree"},
        ), mock.patch.object(
            acceptance,
            "_snapshot",
            side_effect=snapshots,
        ), mock.patch.object(
            acceptance,
            "_run_profile",
            side_effect=(({"run": 1}, b"one"), ({"run": 2}, b"two")),
        ):
            with self.assertRaisesRegex(
                acceptance.AcceptanceFailure,
                "not deterministic",
            ):
                acceptance.run(Path("."), Path("."), "commit", "tree")


if __name__ == "__main__":
    unittest.main()
