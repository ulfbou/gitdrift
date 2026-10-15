from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def git(root: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", *arguments],
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class StateAwarenessCliTests(unittest.TestCase):
    def test_cli_translates_explicit_repository_to_native_artifact(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            git(root, "config", "user.email", "test@example.com")
            git(root, "config", "user.name", "Test")
            (root / "tracked.txt").write_text(
                "base\n",
                encoding="utf-8",
            )
            git(root, "add", "tracked.txt")
            git(root, "commit", "-qm", "initial")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "gitdrift",
                    "state-awareness",
                    "--repository",
                    str(root),
                    "--without-upstream",
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            document = json.loads(completed.stdout)
            self.assertEqual(completed.stderr, b"")
            self.assertEqual(len(document["states"]), 3)
            self.assertEqual(len(document["comparisons"]), 3)
            self.assertEqual(
                document["manifest"]["capability_identity"],
                "gitdrift-state-awareness-composition-v1",
            )


if __name__ == "__main__":
    unittest.main()
