import json
import subprocess
import sys
import unittest

from gitdrift import NATIVE_SCHEMA_VERSION, discover_capabilities


class DiscoveryTests(unittest.TestCase):
    def test_discovery_reports_only_implemented_capabilities(self) -> None:
        payload = discover_capabilities().to_dict()
        self.assertEqual(
            payload["operations"]["available"],
            [
                "capability-discovery",
                "repository-acquisition",
                "state-comparison",
                "native-investigation-serialization",
            ],
        )
        self.assertEqual(
            payload["profiles"]["available"],
            ["state-awareness"],
        )
        self.assertNotIn(
            "state-awareness",
            payload["profiles"]["unavailable"],
        )
        self.assertIn("repository-mutation", payload["operations"]["unavailable"])
        self.assertEqual(payload["native_schema_versions"], [NATIVE_SCHEMA_VERSION])

    def test_module_cli_emits_json_without_diagnostics_on_stdout(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "gitdrift", "discover"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(
            payload["operations"]["available"],
            [
                "capability-discovery",
                "repository-acquisition",
                "state-comparison",
                "native-investigation-serialization",
            ],
        )


if __name__ == "__main__":
    unittest.main()
