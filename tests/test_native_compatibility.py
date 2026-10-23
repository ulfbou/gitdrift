from __future__ import annotations

import unittest

from gitdrift.adapters.serialization import json as native_json
from gitdrift.discovery import discover_capabilities
from gitdrift.domain import StateKind
from gitdrift.ports import (
    NATIVE_SCHEMA_ID,
    NATIVE_SCHEMA_VERSION,
    NativeValidationError,
)


class NativeCompatibilityTests(unittest.TestCase):
    def valid_document(self) -> dict[str, object]:
        return {
            "schema": NATIVE_SCHEMA_ID,
            "schema_version": NATIVE_SCHEMA_VERSION,
            "investigation_id": "investigation:compatibility-fixture",
            "manifest": {},
            "states": [],
            "comparisons": [],
            "snapshots": [],
            "changes": [],
            "evidence": [],
            "facts": [],
            "obligations": [],
            "evaluations": [],
            "cases": [],
            "diagnostics": [],
            "completeness": {},
        }

    def test_supported_schema_identity_and_version_are_accepted(self) -> None:
        native_json._validate_document(self.valid_document())

    def test_unknown_root_semantics_are_rejected(self) -> None:
        document = self.valid_document()
        document["future_required_semantic"] = {"required": True}
        with self.assertRaisesRegex(
            NativeValidationError,
            "unknown required semantics: future_required_semantic",
        ):
            native_json._validate_document(document)

    def test_unknown_schema_identity_is_rejected(self) -> None:
        document = self.valid_document()
        document["schema"] = "https://gitdrift.dev/schemas/investigation/future"
        with self.assertRaisesRegex(
            NativeValidationError,
            "schema identity is unsupported",
        ):
            native_json._validate_document(document)

    def test_unknown_schema_version_is_rejected_without_coercion(self) -> None:
        document = self.valid_document()
        document["schema_version"] = "999.0.0"
        with self.assertRaisesRegex(
            NativeValidationError,
            "schema version is unsupported",
        ):
            native_json._validate_document(document)

    def test_unknown_enum_value_is_rejected_without_coercion(self) -> None:
        with self.assertRaisesRegex(ValueError, "future-state-kind"):
            StateKind("future-state-kind")

    def test_unavailable_migration_is_not_advertised(self) -> None:
        capabilities = discover_capabilities().to_dict()
        available = set(capabilities["operations"]["available"])
        self.assertNotIn("native-schema-migration", available)
        self.assertNotIn("migration", available)


if __name__ == "__main__":
    unittest.main()
