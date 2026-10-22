"""Release gate and obligation coverage mapping."""
from __future__ import annotations

from typing import Any, Sequence

from release_evidence_contracts import evidence_record


def coverage_records(
    required: Sequence[str],
    covered: set[str],
    evidence_ids: Sequence[str],
    limitation: str,
) -> dict[str, dict[str, Any]]:
    return {
        identity: evidence_record(
            "pass" if identity in covered else "blocked",
            evidence_ids if identity in covered else (),
            None if identity in covered else limitation,
        )
        for identity in required
    }


def is_complete(*record_sets: dict[str, dict[str, Any]]) -> bool:
    return all(
        record["outcome"] == "pass"
        for records in record_sets
        for record in records.values()
    )
