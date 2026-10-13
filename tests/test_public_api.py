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
                "IDENTITY_SCHEME",
                "Investigation",
                "NATIVE_SCHEMA_VERSION",
                "__version__",
                "discover_capabilities",
                "stable_id",
                "validate_reference_closure",
            },
        )


if __name__ == "__main__":
    unittest.main()
