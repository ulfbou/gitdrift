from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "acceptance" / "platform_matrix.py"
SPEC = importlib.util.spec_from_file_location("platform_matrix_acceptance", SCRIPT)
assert SPEC and SPEC.loader
matrix = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = matrix
SPEC.loader.exec_module(matrix)


class PlatformMatrixTests(unittest.TestCase):
    def observation(self, system: str, candidate: str = "candidate") -> dict[str, object]:
        return {
            "schema": matrix.OBSERVATION_SCHEMA,
            "candidate_commit": candidate,
            "source_tree_identity": "tree",
            "platform": {"system": system},
            "semantic_probe": {"exit_code": 0},
            "outcome": "pass",
        }

    def write(self, value: object) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "observation.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_linux_and_windows_close_platform_obligation_only(self) -> None:
        document = matrix.combine(
            (self.write(self.observation("Linux")), self.write(self.observation("Windows")))
        )
        self.assertEqual(document["outcome"], "pass")
        self.assertEqual(document["obligations"]["GD01-034"]["outcome"], "pass")
        self.assertEqual(document["gates"]["G7"]["outcome"], "partial")
        self.assertEqual(document["missing_systems"], [])

    def test_missing_required_system_blocks_matrix(self) -> None:
        document = matrix.combine((self.write(self.observation("Linux")),))
        self.assertEqual(document["outcome"], "blocked")
        self.assertEqual(document["missing_systems"], ["Windows"])
        self.assertEqual(document["obligations"]["GD01-034"]["outcome"], "blocked")

    def test_mixed_candidate_is_rejected(self) -> None:
        with self.assertRaisesRegex(matrix.MatrixFailure, "one exact candidate"):
            matrix.combine(
                (
                    self.write(self.observation("Linux")),
                    self.write(self.observation("Windows", candidate="other")),
                )
            )

    def test_duplicate_platform_is_rejected(self) -> None:
        with self.assertRaisesRegex(matrix.MatrixFailure, "duplicate"):
            matrix.combine(
                (self.write(self.observation("Linux")), self.write(self.observation("Linux")))
            )


if __name__ == "__main__":
    unittest.main()
