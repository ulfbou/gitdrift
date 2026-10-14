from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from gitdrift.domain import RawChange


class RawChangeEvidenceTests(unittest.TestCase):
    def complete_change(self, **overrides: object) -> RawChange:
        values: dict[str, object] = {
            "comparison_id": "comparison:one",
            "status": "modification",
            "source_path": "src/original.py",
            "destination_path": "src/original.py",
            "source_identity": "blob:before",
            "destination_identity": "blob:after",
            "source_mode": "100644",
            "destination_mode": "100755",
            "patch_identity": "sha256:patch",
            "binary_treatment": "text",
            "diff_options": {
                "algorithm": "histogram",
                "binary": "preserve",
                "rename_detection": False,
                "whitespace": "retain",
            },
            "limitations": (),
        }
        values.update(overrides)
        return RawChange(**values)  # type: ignore[arg-type]

    def test_exact_evidence_is_retained_immutably(self) -> None:
        change = self.complete_change()

        self.assertEqual(change.source_identity, "blob:before")
        self.assertEqual(change.destination_identity, "blob:after")
        self.assertEqual(change.source_mode, "100644")
        self.assertEqual(change.destination_mode, "100755")
        self.assertEqual(change.patch_identity, "sha256:patch")
        self.assertEqual(change.binary_treatment, "text")
        self.assertEqual(
            change.diff_options["algorithm"],
            "histogram",
        )

        with self.assertRaises(FrozenInstanceError):
            change.status = "deletion"  # type: ignore[misc]

    def test_every_result_defining_field_controls_identity(self) -> None:
        baseline = self.complete_change()

        variants = (
            self.complete_change(
                comparison_id="comparison:other",
            ),
            self.complete_change(status="type-change"),
            self.complete_change(source_path="src/before.py"),
            self.complete_change(
                destination_path="src/after.py",
            ),
            self.complete_change(source_identity="blob:other"),
            self.complete_change(
                destination_identity="blob:other",
            ),
            self.complete_change(source_mode="100755"),
            self.complete_change(destination_mode="100644"),
            self.complete_change(
                patch_identity="sha256:other",
            ),
            self.complete_change(
                binary_treatment="binary",
            ),
            self.complete_change(
                submodule_identity="commit:nested",
            ),
            self.complete_change(
                diff_options={
                    "algorithm": "minimal",
                    "binary": "preserve",
                    "rename_detection": False,
                    "whitespace": "retain",
                }
            ),
            self.complete_change(
                limitations=("patch unavailable",),
            ),
        )

        for variant in variants:
            with self.subTest(variant=variant):
                self.assertNotEqual(baseline.id, variant.id)

    def test_path_separator_spelling_does_not_change_identity(
        self,
    ) -> None:
        portable = self.complete_change(
            source_path="src/module.py",
            destination_path="src/module.py",
        )
        platform_spelling = self.complete_change(
            source_path=r"src\module.py",
            destination_path=r"src\module.py",
        )

        self.assertEqual(
            platform_spelling.source_path,
            "src/module.py",
        )
        self.assertEqual(portable.id, platform_spelling.id)

    def test_paths_cannot_escape_the_workspace(self) -> None:
        for field_name in ("source_path", "destination_path"):
            with self.subTest(field_name=field_name):
                with self.assertRaisesRegex(
                    ValueError,
                    "must be workspace-relative",
                ):
                    self.complete_change(
                        **{field_name: "../outside.bin"}
                    )

    def test_change_requires_at_least_one_path(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "requires a source or destination path",
        ):
            self.complete_change(
                source_path=None,
                destination_path=None,
            )

    def test_addition_requires_destination_path(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "addition requires a destination path",
        ):
            self.complete_change(
                status="addition",
                source_path=None,
                destination_path=None,
            )

    def test_deletion_requires_source_path(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "deletion requires a source path",
        ):
            self.complete_change(
                status="deletion",
                source_path=None,
                destination_path="removed.txt",
            )

    def test_rename_candidate_retains_method_and_score(self) -> None:
        rename = self.complete_change(
            status="rename-candidate",
            source_path="old.txt",
            destination_path="new.txt",
            rename_or_copy_score=87,
            rename_or_copy_method="git-similarity",
        )

        self.assertEqual(rename.rename_or_copy_score, 87)
        self.assertEqual(
            rename.rename_or_copy_method,
            "git-similarity",
        )

    def test_candidate_requires_both_paths_score_and_method(
        self,
    ) -> None:
        invalid_cases = (
            {
                "status": "rename-candidate",
                "source_path": None,
                "destination_path": "new.txt",
                "rename_or_copy_score": 90,
                "rename_or_copy_method": "git-similarity",
            },
            {
                "status": "rename-candidate",
                "source_path": "old.txt",
                "destination_path": "new.txt",
                "rename_or_copy_score": None,
                "rename_or_copy_method": "git-similarity",
            },
            {
                "status": "copy-candidate",
                "source_path": "old.txt",
                "destination_path": "new.txt",
                "rename_or_copy_score": 75,
                "rename_or_copy_method": None,
            },
        )

        for values in invalid_cases:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    self.complete_change(**values)

    def test_candidate_score_is_bounded(self) -> None:
        for score in (-1, 101):
            with self.subTest(score=score):
                with self.assertRaisesRegex(
                    ValueError,
                    "between 0 and 100",
                ):
                    self.complete_change(
                        status="copy-candidate",
                        source_path="old.txt",
                        destination_path="new.txt",
                        rename_or_copy_score=score,
                        rename_or_copy_method="git-similarity",
                    )

    def test_non_candidate_rejects_similarity_evidence(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "requires a candidate status",
        ):
            self.complete_change(
                rename_or_copy_score=90,
                rename_or_copy_method="git-similarity",
            )

    def test_unknown_status_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "unsupported raw-change status",
        ):
            self.complete_change(status="changed")


if __name__ == "__main__":
    unittest.main()
