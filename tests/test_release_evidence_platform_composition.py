from __future__ import annotations

import copy
import unittest

from release_evidence_test_support import ACCEPTANCE, ROOT  # noqa: F401
from release_evidence_contracts import (
    PLATFORM_MATRIX_SCHEMA,
    PLATFORM_OBSERVATION_SCHEMA,
    ReleaseEvidenceFailure,
)
from release_evidence_documents import (
    validate_g7_composition,
    validate_platform_matrix,
)


CANDIDATE = "a" * 40
TREE = "b" * 40
STATUS = "c" * 64


def observation(system: str) -> dict[str, object]:
    state = {
        "candidate_commit": CANDIDATE,
        "source_tree_identity": TREE,
        "status_sha256": STATUS,
    }
    return {
        "schema": PLATFORM_OBSERVATION_SCHEMA,
        "candidate_commit": CANDIDATE,
        "source_tree_identity": TREE,
        "platform": {
            "system": system,
            "release": "test",
            "machine": "test",
        },
        "python": {
            "implementation": "CPython",
            "version": "3.11",
        },
        "git": {"version": "git version test"},
        "filesystem": {
            "case_normalization": "test",
            "path_separator": "/",
            "symlink_supported": True,
        },
        "semantic_probe": {
            "modules": ["tests.example"],
            "exit_code": 0,
            "stdout_sha256": "d" * 64,
            "stderr_sha256": "e" * 64,
        },
        "mutation_sentinel": {
            "before": dict(state),
            "after": dict(state),
            "outcome": "pass",
        },
        "obligations": {
            "GD01-034": {"outcome": "partial"}
        },
        "gates": {"G7": {"outcome": "partial"}},
        "limitations": [
            "One observation does not establish the complete matrix."
        ],
        "outcome": "pass",
    }



def resource_bounds() -> dict[str, object]:
    state = {
        "candidate_commit": CANDIDATE,
        "source_tree_identity": TREE,
        "status_sha256": STATUS,
    }
    return {
        "schema": "gitdrift-resource-bounds-acceptance-v1",
        "candidate_commit": CANDIDATE,
        "source_tree_identity": TREE,
        "test_modules": ["tests.example"],
        "command": ["python", "-m", "unittest"],
        "command_exit_code": 0,
        "stdout_sha256": "d" * 64,
        "stderr_sha256": "e" * 64,
        "mutation_sentinel": {
            "before": dict(state),
            "after": dict(state),
            "outcome": "pass",
        },
        "obligations": {
            "GD01-031": {"outcome": "pass"}
        },
        "gates": {
            "G6": {"outcome": "pass"},
            "G7": {"outcome": "partial"},
        },
        "limitations": [
            "G7 requires platform composition."
        ],
        "outcome": "pass",
    }


def matrix() -> dict[str, object]:
    return {
        "schema": PLATFORM_MATRIX_SCHEMA,
        "candidate_commit": CANDIDATE,
        "source_tree_identity": TREE,
        "required_systems": ["Linux", "Windows"],
        "observed_systems": ["Linux", "Windows"],
        "observations": [
            observation("Linux"),
            observation("Windows"),
        ],
        "missing_systems": [],
        "obligations": {
            "GD01-034": {"outcome": "pass"}
        },
        "gates": {"G7": {"outcome": "partial"}},
        "limitations": [
            "G7 remains partial until resource-bound evidence passes."
        ],
        "outcome": "pass",
    }


class PlatformEvidenceCompositionTests(unittest.TestCase):
    def validate(
        self,
        document: dict[str, object],
    ) -> dict[str, object]:
        return validate_platform_matrix(
            document,
            candidate=CANDIDATE,
            source_tree=TREE,
        )

    def rejected(
        self,
        document: dict[str, object],
        message: str,
    ) -> None:
        with self.assertRaisesRegex(
            ReleaseEvidenceFailure,
            message,
        ):
            self.validate(document)

    def test_complete_linux_and_windows_matrix_passes(self) -> None:
        document = matrix()

        self.assertIs(self.validate(document), document)
        self.assertEqual(
            document["obligations"],
            {"GD01-034": {"outcome": "pass"}},
        )
        self.assertEqual(
            document["gates"],
            {"G7": {"outcome": "partial"}},
        )

    def test_malformed_root_is_rejected(self) -> None:
        document = matrix()
        document["unknown"] = True

        self.rejected(document, "fields are invalid")

    def test_incorrect_matrix_schema_is_rejected(self) -> None:
        document = matrix()
        document["schema"] = "incorrect"

        self.rejected(document, "matrix schema")

    def test_matrix_candidate_mismatch_is_rejected(self) -> None:
        document = matrix()
        document["candidate_commit"] = "f" * 40

        self.rejected(document, "matrix candidate mismatch")

    def test_matrix_tree_mismatch_is_rejected(self) -> None:
        document = matrix()
        document["source_tree_identity"] = "f" * 40

        self.rejected(document, "matrix source-tree mismatch")

    def test_missing_linux_is_rejected(self) -> None:
        document = matrix()
        document["observations"] = [observation("Windows")]

        self.rejected(document, "exactly two observations")

    def test_missing_windows_is_rejected(self) -> None:
        document = matrix()
        document["observations"] = [observation("Linux")]

        self.rejected(document, "exactly two observations")

    def test_duplicate_observation_is_rejected(self) -> None:
        document = matrix()
        document["observations"] = [
            observation("Linux"),
            observation("Linux"),
        ]

        self.rejected(document, "duplicate observation")

    def test_failed_observation_is_rejected(self) -> None:
        document = matrix()
        observations = document["observations"]
        assert isinstance(observations, list)
        assert isinstance(observations[0], dict)
        observations[0]["outcome"] = "fail"

        self.rejected(document, "observation did not pass")

    def test_failed_semantic_probe_is_rejected(self) -> None:
        document = matrix()
        observations = document["observations"]
        assert isinstance(observations, list)
        linux = observations[0]
        assert isinstance(linux, dict)
        probe = linux["semantic_probe"]
        assert isinstance(probe, dict)
        probe["exit_code"] = 1

        self.rejected(document, "semantic probe did not pass")

    def test_failed_mutation_sentinel_is_rejected(self) -> None:
        document = matrix()
        observations = document["observations"]
        assert isinstance(observations, list)
        linux = observations[0]
        assert isinstance(linux, dict)
        sentinel = linux["mutation_sentinel"]
        assert isinstance(sentinel, dict)
        sentinel["outcome"] = "fail"

        self.rejected(document, "mutation sentinel did not pass")

    def test_changed_mutation_sentinel_is_rejected(self) -> None:
        document = matrix()
        observations = document["observations"]
        assert isinstance(observations, list)
        linux = observations[0]
        assert isinstance(linux, dict)
        sentinel = linux["mutation_sentinel"]
        assert isinstance(sentinel, dict)
        after = sentinel["after"]
        assert isinstance(after, dict)
        after["status_sha256"] = "f" * 64

        self.rejected(document, "sentinel does not close")

    def test_unknown_platform_is_rejected(self) -> None:
        document = matrix()
        observations = document["observations"]
        assert isinstance(observations, list)
        observations[0] = observation("Darwin")

        self.rejected(document, "unknown platform")

    def test_gd01_034_without_complete_authority_is_rejected(
        self,
    ) -> None:
        document = matrix()
        document["obligations"] = {
            "GD01-034": {"outcome": "blocked"}
        }

        self.rejected(document, "obligation authority")

    def test_platform_evidence_cannot_claim_g7_pass(self) -> None:
        document = matrix()
        document["gates"] = {"G7": {"outcome": "pass"}}

        self.rejected(document, "partial G7")

    def test_platform_evidence_cannot_claim_g8(self) -> None:
        document = matrix()
        document["gates"] = {
            "G7": {"outcome": "partial"},
            "G8": {"outcome": "pass"},
        }

        self.rejected(document, "partial G7")

    def test_mixed_candidate_observations_are_rejected(self) -> None:
        document = matrix()
        observations = document["observations"]
        assert isinstance(observations, list)
        windows = observations[1]
        assert isinstance(windows, dict)
        windows["candidate_commit"] = "f" * 40

        self.rejected(document, "observation candidate mismatch")

    def test_mixed_tree_observations_are_rejected(self) -> None:
        document = matrix()
        observations = document["observations"]
        assert isinstance(observations, list)
        windows = observations[1]
        assert isinstance(windows, dict)
        windows["source_tree_identity"] = "f" * 40

        self.rejected(document, "observation source-tree mismatch")

    def test_unknown_obligation_claim_is_rejected(self) -> None:
        document = matrix()
        document["obligations"] = {
            "GD01-034": {"outcome": "pass"},
            "GD01-999": {"outcome": "pass"},
        }

        self.rejected(document, "obligation authority")

    def test_unknown_gate_claim_is_rejected(self) -> None:
        document = matrix()
        document["gates"] = {
            "G7": {"outcome": "partial"},
            "G9": {"outcome": "pass"},
        }

        self.rejected(document, "partial G7")

    def test_observation_unknown_claim_is_rejected(self) -> None:
        document = matrix()
        observations = document["observations"]
        assert isinstance(observations, list)
        linux = observations[0]
        assert isinstance(linux, dict)
        linux["obligations"] = {
            "GD01-034": {"outcome": "partial"},
            "GD01-999": {"outcome": "pass"},
        }

        self.rejected(
            document,
            "observation obligation authority",
        )

    def test_observation_claiming_g8_is_rejected(self) -> None:
        document = matrix()
        observations = document["observations"]
        assert isinstance(observations, list)
        linux = observations[0]
        assert isinstance(linux, dict)
        linux["gates"] = {
            "G7": {"outcome": "partial"},
            "G8": {"outcome": "pass"},
        }

        self.rejected(
            document,
            "observation gate authority",
        )

    def test_input_document_is_not_mutated(self) -> None:
        document = matrix()
        before = copy.deepcopy(document)

        self.validate(document)

        self.assertEqual(document, before)

    def test_platform_and_resource_evidence_close_g7(
        self,
    ) -> None:
        obligations, gates = validate_g7_composition(
            matrix(),
            resource_bounds(),
            candidate=CANDIDATE,
            source_tree=TREE,
        )

        self.assertEqual(obligations, {"GD01-034"})
        self.assertEqual(gates, {"G7"})

    def test_resource_evidence_alone_cannot_pass_g7(
        self,
    ) -> None:
        resource = resource_bounds()
        resource["gates"] = {
            "G6": {"outcome": "pass"},
            "G7": {"outcome": "pass"},
        }

        with self.assertRaisesRegex(
            ReleaseEvidenceFailure,
            "alone must not pass G7",
        ):
            validate_g7_composition(
                matrix(),
                resource,
                candidate=CANDIDATE,
                source_tree=TREE,
            )

    def test_failed_resource_evidence_cannot_close_g7(
        self,
    ) -> None:
        resource = resource_bounds()
        resource["outcome"] = "fail"

        with self.assertRaisesRegex(
            ReleaseEvidenceFailure,
            "resource evidence did not pass",
        ):
            validate_g7_composition(
                matrix(),
                resource,
                candidate=CANDIDATE,
                source_tree=TREE,
            )

    def test_resource_tree_mismatch_cannot_close_g7(
        self,
    ) -> None:
        resource = resource_bounds()
        resource["source_tree_identity"] = "f" * 40

        with self.assertRaisesRegex(
            ReleaseEvidenceFailure,
            "exact-candidate identity mismatch",
        ):
            validate_g7_composition(
                matrix(),
                resource,
                candidate=CANDIDATE,
                source_tree=TREE,
            )

    def test_resource_mutation_failure_cannot_close_g7(
        self,
    ) -> None:
        resource = resource_bounds()
        sentinel = resource["mutation_sentinel"]
        assert isinstance(sentinel, dict)
        sentinel["outcome"] = "fail"

        with self.assertRaisesRegex(
            ReleaseEvidenceFailure,
            "resource mutation sentinel did not pass",
        ):
            validate_g7_composition(
                matrix(),
                resource,
                candidate=CANDIDATE,
                source_tree=TREE,
            )


if __name__ == "__main__":
    unittest.main()
