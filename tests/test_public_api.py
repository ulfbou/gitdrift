import unittest

import gitdrift


class PublicApiTests(unittest.TestCase):
    def test_supported_exports_are_explicit(self) -> None:
        self.assertEqual(
            set(gitdrift.__all__),
            {
                "CapabilityDocument",
                "Completeness",
                "Diagnostic",
                "DiagnosticSeverity",
                "ExecutionStatus",
                "NATIVE_SCHEMA_VERSION",
                "__version__",
                "discover_capabilities",
            },
        )


if __name__ == "__main__":
    unittest.main()
