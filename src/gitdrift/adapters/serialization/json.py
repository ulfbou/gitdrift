"""Canonical validation and JSON serialization for investigations."""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from enum import Enum
from importlib.resources import files
from typing import Any, Mapping, Sequence

from gitdrift.domain import (
    Investigation,
    stable_id,
    validate_reference_closure,
)
from gitdrift.ports.native import (
    NATIVE_SCHEMA_ID,
    NATIVE_SCHEMA_VERSION,
    NativeArtifact,
    NativeContractError,
    NativeValidationError,
)


_SCHEMA_RESOURCE = "gitdrift-investigation-v1.schema.json"

_REQUIRED_ROOT_FIELDS = frozenset(
    {
        "schema",
        "schema_version",
        "investigation_id",
        "manifest",
        "states",
        "comparisons",
        "snapshots",
        "changes",
        "evidence",
        "facts",
        "obligations",
        "evaluations",
        "cases",
        "diagnostics",
        "completeness",
    }
)

_COLLECTION_FIELDS = (
    "states",
    "comparisons",
    "snapshots",
    "changes",
    "evidence",
    "facts",
    "obligations",
    "evaluations",
    "cases",
    "diagnostics",
)


def load_native_schema() -> Mapping[str, Any]:
    """Load the packaged accepted schema without checkout-relative paths."""

    resource = files("gitdrift.schemas").joinpath(_SCHEMA_RESOURCE)
    document = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise NativeValidationError("native schema root must be an object")
    if document.get("$id") != NATIVE_SCHEMA_ID:
        raise NativeValidationError("packaged native schema identity mismatch")
    if document.get("x-gitdrift-schema-version") != NATIVE_SCHEMA_VERSION:
        raise NativeValidationError("packaged native schema version mismatch")
    return document


def _native(value: Any) -> Any:
    if is_dataclass(value):
        result: dict[str, Any] = {}
        for item in fields(value):
            result[item.name] = _native(getattr(value, item.name))
        return result
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {
            str(key.value if isinstance(key, Enum) else key): _native(item)
            for key, item in sorted(
                value.items(),
                key=lambda pair: str(
                    pair[0].value
                    if isinstance(pair[0], Enum)
                    else pair[0]
                ),
            )
        }
    if isinstance(value, (set, frozenset)):
        converted = [_native(item) for item in value]
        return sorted(
            converted,
            key=lambda item: json.dumps(
                item,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        return [_native(item) for item in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise NativeContractError(
        "unsupported native value: " + type(value).__name__
    )


def _ordered_records(records: object) -> list[dict[str, Any]]:
    if not isinstance(records, tuple):
        raise NativeValidationError(
            "investigation collections must be immutable tuples"
        )
    converted = [_native(record) for record in records]
    if not all(isinstance(record, dict) for record in converted):
        raise NativeValidationError(
            "investigation collections must contain records"
        )
    if not all(
        isinstance(record.get("id"), str) and record["id"]
        for record in converted
    ):
        raise NativeValidationError(
            "every native collection record requires a stable id"
        )
    identities = [record["id"] for record in converted]
    if len(set(identities)) != len(identities):
        raise NativeValidationError(
            "native collection contains duplicate record identities"
        )
    return sorted(converted, key=lambda record: record["id"])


def _validate_document(document: Mapping[str, Any]) -> None:
    unknown = set(document) - _REQUIRED_ROOT_FIELDS
    missing = _REQUIRED_ROOT_FIELDS - set(document)

    if missing:
        raise NativeValidationError(
            "native document is missing required fields: "
            + ", ".join(sorted(missing))
        )
    if unknown:
        raise NativeValidationError(
            "native document has unknown required semantics: "
            + ", ".join(sorted(unknown))
        )
    if document["schema"] != NATIVE_SCHEMA_ID:
        raise NativeValidationError("native schema identity is unsupported")
    if document["schema_version"] != NATIVE_SCHEMA_VERSION:
        raise NativeValidationError("native schema version is unsupported")
    if not isinstance(document["investigation_id"], str):
        raise NativeValidationError("investigation_id must be a string")
    if not isinstance(document["manifest"], dict):
        raise NativeValidationError("manifest must be an object")
    if not isinstance(document["completeness"], dict):
        raise NativeValidationError("completeness must be an object")

    for field_name in _COLLECTION_FIELDS:
        records = document[field_name]
        if not isinstance(records, list):
            raise NativeValidationError(
                f"{field_name} must be an array"
            )


def _canonical_bytes(document: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            document,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


class CanonicalNativeJsonSerializer:
    """Validate reference closure and emit deterministic native JSON."""

    def serialize(self, investigation: Investigation) -> NativeArtifact:
        if not isinstance(investigation, Investigation):
            raise NativeContractError(
                "serializer requires an Investigation"
            )

        load_native_schema()
        validate_reference_closure(investigation)

        manifest = _native(investigation.manifest)
        completeness = _native(investigation.completeness)

        identity_inputs = {
            "schema": NATIVE_SCHEMA_ID,
            "schema_version": NATIVE_SCHEMA_VERSION,
            "manifest": manifest,
            "states": sorted(item.id for item in investigation.states),
            "comparisons": sorted(
                item.id for item in investigation.comparisons
            ),
            "snapshots": sorted(
                item.id for item in investigation.snapshots
            ),
            "changes": sorted(item.id for item in investigation.changes),
            "evidence": sorted(item.id for item in investigation.evidence),
            "facts": sorted(item.id for item in investigation.facts),
            "obligations": sorted(
                item.id for item in investigation.obligations
            ),
            "evaluations": sorted(
                item.id for item in investigation.evaluations
            ),
            "cases": sorted(item.id for item in investigation.cases),
            "completeness": completeness,
        }
        investigation_id = stable_id(
            "investigation",
            identity_inputs,
        )

        document: dict[str, Any] = {
            "schema": NATIVE_SCHEMA_ID,
            "schema_version": NATIVE_SCHEMA_VERSION,
            "investigation_id": investigation_id,
            "manifest": manifest,
            "states": _ordered_records(investigation.states),
            "comparisons": _ordered_records(
                investigation.comparisons
            ),
            "snapshots": _ordered_records(investigation.snapshots),
            "changes": _ordered_records(investigation.changes),
            "evidence": _ordered_records(investigation.evidence),
            "facts": _ordered_records(investigation.facts),
            "obligations": _ordered_records(
                investigation.obligations
            ),
            "evaluations": _ordered_records(
                investigation.evaluations
            ),
            "cases": _ordered_records(investigation.cases),
            "diagnostics": sorted(
                (_native(item) for item in investigation.diagnostics),
                key=lambda item: (
                    item["code"],
                    item["severity"],
                    item["category"],
                    tuple(item["affected_ids"]),
                ),
            ),
            "completeness": completeness,
        }

        _validate_document(document)
        payload = _canonical_bytes(document)

        reparsed = json.loads(payload.decode("utf-8"))
        if reparsed != document:
            raise NativeValidationError(
                "canonical native JSON did not round-trip exactly"
            )

        return NativeArtifact(
            schema_id=NATIVE_SCHEMA_ID,
            schema_version=NATIVE_SCHEMA_VERSION,
            investigation_id=investigation_id,
            payload=payload,
        )
