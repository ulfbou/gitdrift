"""Versioned JSON loader for explicitly supplied obligation sets."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from gitdrift.domain import (
    DiagnosticRecord,
    EvidenceReference,
    Obligation,
    stable_id,
)
from gitdrift.ports.obligations import ObligationSet

_SCHEMA = "gitdrift-obligation-set-v1"
_ALLOWED_RELATIONS = frozenset(
    {
        "exists",
        "does-not-exist",
        "consistent-with",
        "implements",
        "enforces",
        "references",
        "preserves",
        "stronger-than-or-equivalent-to",
    }
)


class ObligationSetValidationError(ValueError):
    """An explicit obligation set is malformed or unsupported."""


def _object(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ObligationSetValidationError(f"{field} must be an object")
    return value


def _string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ObligationSetValidationError(
            f"{field} must be a non-empty string"
        )
    return value


def _strings(value: object, field: str, *, nonempty: bool) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ObligationSetValidationError(f"{field} must be an array")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ObligationSetValidationError(
            f"{field} must contain only non-empty strings"
        )
    result = tuple(value)
    if nonempty and not result:
        raise ObligationSetValidationError(f"{field} must not be empty")
    if len(set(result)) != len(result):
        raise ObligationSetValidationError(
            f"{field} must not contain duplicates"
        )
    return result


class JsonObligationSetLoader:
    """Load only the versioned explicit JSON obligation-set contract."""

    def load(
        self,
        payload: bytes,
        *,
        source_evidence: EvidenceReference,
    ) -> ObligationSet:
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ObligationSetValidationError(
                "obligation set must be valid UTF-8"
            ) from error
        try:
            document = json.loads(text)
        except json.JSONDecodeError as error:
            raise ObligationSetValidationError(
                f"obligation set is invalid JSON: {error.msg}"
            ) from error

        root = _object(document, "root")
        unknown_root = set(root) - {"schema", "obligations"}
        if unknown_root:
            raise ObligationSetValidationError(
                "unknown root fields: " + ", ".join(sorted(unknown_root))
            )
        schema = _string(root.get("schema"), "schema")
        if schema != _SCHEMA:
            raise ObligationSetValidationError(
                f"unsupported obligation-set schema: {schema!r}"
            )
        raw_obligations = root.get("obligations")
        if not isinstance(raw_obligations, list):
            raise ObligationSetValidationError(
                "obligations must be an array"
            )

        obligations: list[Obligation] = []
        for index, raw in enumerate(raw_obligations):
            item = _object(raw, f"obligations[{index}]")
            allowed = {
                "subjects",
                "relation",
                "authority_evidence_ids",
                "scope",
                "activation",
                "retirement",
                "supersession_rules",
            }
            unknown = set(item) - allowed
            if unknown:
                raise ObligationSetValidationError(
                    f"obligations[{index}] has unknown fields: "
                    + ", ".join(sorted(unknown))
                )
            relation = _string(
                item.get("relation"),
                f"obligations[{index}].relation",
            )
            if relation not in _ALLOWED_RELATIONS:
                raise ObligationSetValidationError(
                    f"obligations[{index}].relation is unsupported: "
                    f"{relation!r}"
                )
            retirement = item.get("retirement")
            if retirement is not None:
                retirement = _string(
                    retirement,
                    f"obligations[{index}].retirement",
                )
            obligations.append(
                Obligation(
                    subject_ids=_strings(
                        item.get("subjects"),
                        f"obligations[{index}].subjects",
                        nonempty=True,
                    ),
                    relation=relation,
                    authority_evidence_ids=_strings(
                        item.get("authority_evidence_ids"),
                        (
                            f"obligations[{index}]"
                            ".authority_evidence_ids"
                        ),
                        nonempty=True,
                    ),
                    scope=_string(
                        item.get("scope"),
                        f"obligations[{index}].scope",
                    ),
                    activation=_string(
                        item.get("activation"),
                        f"obligations[{index}].activation",
                    ),
                    retirement=retirement,
                    supersession_rules=_strings(
                        item.get("supersession_rules", []),
                        f"obligations[{index}].supersession_rules",
                        nonempty=False,
                    ),
                )
            )

        identities = [obligation.id for obligation in obligations]
        if len(set(identities)) != len(identities):
            raise ObligationSetValidationError(
                "obligation set contains duplicate semantic obligations"
            )

        payload_identity = "sha256:" + hashlib.sha256(payload).hexdigest()
        identity = stable_id(
            "obligation-set",
            {
                "schema": schema,
                "payload_identity": payload_identity,
                "source_evidence_id": source_evidence.id,
                "obligation_ids": identities,
            },
        )
        return ObligationSet(
            schema=schema,
            identity=identity,
            source_evidence=source_evidence,
            obligations=tuple(obligations),
            diagnostics=(
                DiagnosticRecord(
                    code="GD-OBLIGATION-SET-LOADED",
                    severity="informational",
                    category="configuration",
                    affected_ids=(
                        source_evidence.id,
                        identity,
                    ),
                ),
            ),
        )
