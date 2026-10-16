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
    / "state_awareness_synthetic.py"
)

SPEC = importlib.util.spec_from_file_location(
    "gitdrift_state_awareness_synthetic_acceptance",
    SCRIPT,
)
assert SPEC
assert SPEC.loader

acceptance = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = acceptance
SPEC.loader.exec_module(acceptance)


class StateAwarenessSyntheticAcceptanceTests(
    unittest.TestCase
):
    def test_boundary_maps_every_required_scenario(
        self,
    ) -> None:
        self.assertEqual(
            set(acceptance.SCENARIOS),
            {
                "aligned-clean-repository",
                "no-staged-or-unstaged-changes",
                "local-branch-behind-captured-upstream",
                "staged-candidate",
                "unstaged-candidate",
                (
                    "simultaneous-upstream-and-"
                    "staged-candidates"
                ),
                (
                    "staged-and-working-tree-"
                    "divergence"
                ),
                "absent-or-unselected-upstream",
                "deterministic-repeated-execution",
                "zero-repository-mutation",
            },
        )

    def test_boundary_maps_controlling_obligations(
        self,
    ) -> None:
        required = {
            "GD01-001",
            "GD01-008",
            "GD01-018",
            "GD01-030",
            "GD01-036",
            "GD01-037",
        }

        self.assertLessEqual(
            required,
            set(acceptance.OBLIGATIONS),
        )
        self.assertEqual(
            acceptance.RELEASE_GATES,
            (
                "G2",
                "G3",
                "G4",
                "G5",
                "G7",
                "G8",
            ),
        )

    def test_failed_test_boundary_cannot_report_pass(
        self,
    ) -> None:
        completed = mock.Mock(
            returncode=1,
            stdout="",
            stderr="failure",
        )

        with mock.patch.object(
            acceptance,
            "_git",
            side_effect=(
                "candidate",
                "",
                "",
                "candidate",
            ),
        ), mock.patch.object(
            acceptance,
            "_run",
            return_value=completed,
        ):
            with self.assertRaises(
                acceptance.AcceptanceFailure
            ):
                acceptance.run(Path("."))

    def test_repository_mutation_cannot_report_pass(
        self,
    ) -> None:
        completed = mock.Mock(
            returncode=0,
            stdout="ok",
            stderr="",
        )

        with mock.patch.object(
            acceptance,
            "_git",
            side_effect=(
                "candidate",
                "",
                " M changed.txt",
                "candidate",
            ),
        ), mock.patch.object(
            acceptance,
            "_run",
            return_value=completed,
        ):
            with self.assertRaisesRegex(
                acceptance.AcceptanceFailure,
                "changed repository candidate state",
            ):
                acceptance.run(Path("."))

    def test_head_mutation_cannot_report_pass(
        self,
    ) -> None:
        completed = mock.Mock(
            returncode=0,
            stdout="ok",
            stderr="",
        )

        with mock.patch.object(
            acceptance,
            "_git",
            side_effect=(
                "candidate",
                "",
                "",
                "different-candidate",
            ),
        ), mock.patch.object(
            acceptance,
            "_run",
            return_value=completed,
        ):
            with self.assertRaisesRegex(
                acceptance.AcceptanceFailure,
                "changed candidate HEAD",
            ):
                acceptance.run(Path("."))


if __name__ == "__main__":
    unittest.main()
