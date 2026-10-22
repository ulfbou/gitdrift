from __future__ import annotations

import unittest

from release_evidence_test_support import ACCEPTANCE  # noqa: F401
from release_evidence_coverage import coverage_records, is_complete


class CoverageMappingTests(unittest.TestCase):
    def test_missing_coverage_remains_blocked(self) -> None:
        records = coverage_records(
            ("one", "two"),
            {"one"},
            ("evidence",),
            "missing evidence",
        )
        self.assertEqual(
            records["one"]["evidence_ids"],
            ["evidence"],
        )
        self.assertEqual(
            records["two"]["outcome"],
            "blocked",
        )
        self.assertEqual(
            records["two"]["evidence_ids"],
            [],
        )
        self.assertFalse(is_complete(records))
