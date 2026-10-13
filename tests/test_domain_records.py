import unittest
from dataclasses import FrozenInstanceError

from gitdrift.domain import (
    ArtifactSnapshot,
    CompletenessDeclaration,
    CompletenessDimension,
    Comparison,
    EvidenceClass,
    EvidenceReference,
    RepositoryState,
    StateKind,
)


class DomainRecordTests(unittest.TestCase):
    def test_records_are_immutable(self) -> None:
        state = RepositoryState(
            StateKind.COMMIT,
            "repo",
            "commit:abc",
        )

        with self.assertRaises(FrozenInstanceError):
            state.content_identity = "commit:def"  # type: ignore[misc]

    def test_path_is_location_and_must_be_workspace_relative(
        self,
    ) -> None:
        state = RepositoryState(
            StateKind.COMMIT,
            "repo",
            "commit:abc",
        )
        first = ArtifactSnapshot(
            state.id,
            "docs/a.md",
            "blob:1",
        )
        second = ArtifactSnapshot(
            state.id,
            "docs/b.md",
            "blob:1",
        )

        self.assertNotEqual(first.id, second.id)

        with self.assertRaises(ValueError):
            ArtifactSnapshot(
                state.id,
                "../outside",
                "blob:1",
            )

    def test_observed_and_derived_evidence_remain_distinct(
        self,
    ) -> None:
        observed = EvidenceReference(
            EvidenceClass.OBSERVED,
            "git",
            "1",
            "subject",
            "blob:1",
        )
        computed = EvidenceReference(
            EvidenceClass.COMPUTED,
            "git",
            "1",
            "subject",
            "blob:1",
        )

        self.assertNotEqual(observed.id, computed.id)

    def test_comparison_identity_retains_endpoint_direction(
        self,
    ) -> None:
        options = {"algorithm": "histogram"}
        forward = Comparison(
            "a",
            "b",
            "head-to-index",
            "staged?",
            options,
        )
        reverse = Comparison(
            "b",
            "a",
            "head-to-index",
            "staged?",
            options,
        )

        self.assertNotEqual(forward.id, reverse.id)

    def test_parent_completeness_cannot_strengthen_partial_child(
        self,
    ) -> None:
        dimension = CompletenessDimension.SEMANTIC_EXTRACTION
        parent = CompletenessDeclaration(
            {dimension: "complete"}
        )
        child = CompletenessDeclaration(
            {dimension: "partial"}
        )

        self.assertFalse(parent.no_stronger_than(child))
        self.assertTrue(child.no_stronger_than(parent))


if __name__ == "__main__":
    unittest.main()
