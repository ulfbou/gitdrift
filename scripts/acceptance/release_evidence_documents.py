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
