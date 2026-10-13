import unittest

from gitdrift.contracts import Completeness, Diagnostic, DiagnosticSeverity


class ContractTests(unittest.TestCase):
    def test_diagnostic_serialization_is_stable_and_typed(self) -> None:
        diagnostic = Diagnostic(
            code="GD-SKELETON-001",
            severity=DiagnosticSeverity.WARNING,
            category="capability",
            message="not implemented",
            completeness_effects={"semantic-extraction": Completeness.UNAVAILABLE},
        )

        self.assertEqual(
            diagnostic.to_dict(),
            {
                "code": "GD-SKELETON-001",
                "severity": "warning",
                "category": "capability",
                "message": "not implemented",
                "completeness_effects": {"semantic-extraction": "unavailable"},
            },
        )


if __name__ == "__main__":
    unittest.main()
