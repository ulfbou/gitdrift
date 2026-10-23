"""Validation of evidence documents consumed by release aggregation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from release_evidence_contracts import ReleaseEvidenceFailure


def load_evidence(
    path: Path,
    expected_schema: str,
    candidate: str,
) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReleaseEvidenceFailure(
            f"cannot load evidence {path}: {error}"
        ) from error
    if not isinstance(document, dict):
        raise ReleaseEvidenceFailure(f"evidence root is not an object: {path}")
    expected = {
        "schema": expected_schema,
        "candidate_commit": candidate,
        "outcome": "pass",
    }
    mismatches = tuple(
        key for key, value in expected.items() if document.get(key) != value
    )
    if mismatches:
        raise ReleaseEvidenceFailure(
            f"invalid evidence {path}; mismatched fields: "
            + ", ".join(mismatches)
        )
    return document


def validated_pass_claims(
    document: dict[str, Any],
    field: str,
    allowed: tuple[str, ...],
) -> set[str]:
    """Return only schema-shaped passing claims from an evidence record."""
    claims = document.get(field)
    if not isinstance(claims, dict):
        raise ReleaseEvidenceFailure(f"evidence {field} claims must be an object")
    unknown = set(claims) - set(allowed)
    if unknown:
        raise ReleaseEvidenceFailure(
            f"evidence {field} contains unknown identities: "
            + ", ".join(sorted(unknown))
        )
    passing: set[str] = set()
    for identity, claim in claims.items():
        if not isinstance(claim, dict) or set(claim) != {"outcome"}:
            raise ReleaseEvidenceFailure(
                f"evidence claim has invalid shape: {field}.{identity}"
            )
        outcome = claim["outcome"]
        if outcome not in {"pass", "partial", "blocked"}:
            raise ReleaseEvidenceFailure(
                f"evidence claim has invalid outcome: {field}.{identity}"
            )
        if outcome == "pass":
            passing.add(identity)
    return passing
