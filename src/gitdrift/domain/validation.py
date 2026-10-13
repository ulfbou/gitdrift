"""Reference-closure validation for domain investigations."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any

from .investigation import Investigation


class ReferenceClosureError(ValueError):
    def __init__(self, missing: tuple[str, ...]) -> None:
        self.missing = missing
        super().__init__(
            "unresolved references: " + ", ".join(missing)
        )


def _references(value: Any) -> set[str]:
    found: set[str] = set()

    if is_dataclass(value):
        for item in fields(value):
            current = getattr(value, item.name)

            if item.name.endswith("_id") and current is not None:
                found.add(current)
            elif item.name.endswith("_ids"):
                found.update(current)
            else:
                found.update(_references(current))

    elif isinstance(value, dict):
        for current in value.values():
            found.update(_references(current))

    elif isinstance(value, (tuple, list, set, frozenset)):
        for current in value:
            found.update(_references(current))

    return found


def validate_reference_closure(
    investigation: Investigation,
) -> None:
    records = (
        investigation.states
        + investigation.comparisons
        + investigation.snapshots
        + investigation.changes
        + investigation.evidence
        + investigation.facts
        + investigation.obligations
        + investigation.evaluations
        + investigation.cases
    )

    identities = {record.id for record in records}

    external = {
        reference.payload_identity
        for reference in investigation.evidence
    }

    references = _references(investigation)

    ignored = {
        investigation.manifest.repository_id,
        investigation.manifest.configuration_identity,
        investigation.manifest.capability_identity,
    }

    missing = tuple(
        sorted(references - identities - external - ignored)
    )

    if missing:
        raise ReferenceClosureError(missing)
