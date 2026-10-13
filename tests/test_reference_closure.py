import unittest

from gitdrift.domain import (
    ArtifactSnapshot,
    CompletenessDeclaration,
    Investigation,
    ReferenceClosureError,
    RepositoryState,
    ReproductionManifest,
    StateKind,
    validate_reference_closure,
)


class ReferenceClosureTests(unittest.TestCase):
    def test_closed_investigation_passes(self) -> None:
        state = RepositoryState(
            StateKind.COMMIT,
            "repo",
            "commit:abc",
        )
        snapshot = ArtifactSnapshot(
            state.id,
            "README.md",
            "blob:1",
        )
        manifest = ReproductionManifest(
            "repo",
            (state.id,),
            "config:1",
            "capabilities:1",
            "0.1.0-dev",
            "0.0.0",
        )
        investigation = Investigation(
            manifest,
            states=(state,),
            snapshots=(snapshot,),
            completeness=CompletenessDeclaration({}),
        )

        validate_reference_closure(investigation)

    def test_missing_reference_fails_with_exact_identity(
        self,
    ) -> None:
        manifest = ReproductionManifest(
            "repo",
            ("state:missing",),
            "config:1",
            "capabilities:1",
            "0.1.0-dev",
            "0.0.0",
        )
        investigation = Investigation(manifest)

        with self.assertRaises(
            ReferenceClosureError
        ) as captured:
            validate_reference_closure(investigation)

        self.assertEqual(
            captured.exception.missing,
            ("state:missing",),
        )


if __name__ == "__main__":
    unittest.main()
