"""Validation of evidence documents consumed by release aggregation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from release_evidence_contracts import (
    PLATFORM_MATRIX_SCHEMA,
    PLATFORM_OBSERVATION_SCHEMA,
    ReleaseEvidenceFailure,
)


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

_REQUIRED_SYSTEMS = ("Linux", "Windows")
_PLATFORM_OBLIGATION = "GD01-034"
_PLATFORM_GATE = "G7"


def _object(
    value: object,
    field: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReleaseEvidenceFailure(
            f"platform evidence {field} must be an object"
        )
    return value


def _exact_fields(
    value: dict[str, Any],
    expected: set[str],
    field: str,
) -> None:
    if set(value) != expected:
        missing = sorted(expected - set(value))
        unknown = sorted(set(value) - expected)
        raise ReleaseEvidenceFailure(
            f"platform evidence {field} fields are invalid; "
            f"missing={missing}; unknown={unknown}"
        )


def _pass_mutation_sentinel(
    value: object,
    *,
    system: str,
    candidate: str,
    source_tree: str,
) -> None:
    sentinel = _object(
        value,
        f"observations.{system}.mutation_sentinel",
    )
    _exact_fields(
        sentinel,
        {"before", "after", "outcome"},
        f"observations.{system}.mutation_sentinel",
    )
    if sentinel.get("outcome") != "pass":
        raise ReleaseEvidenceFailure(
            f"platform mutation sentinel did not pass: {system}"
        )

    before = _object(
        sentinel.get("before"),
        f"observations.{system}.mutation_sentinel.before",
    )
    after = _object(
        sentinel.get("after"),
        f"observations.{system}.mutation_sentinel.after",
    )
    expected_fields = {
        "candidate_commit",
        "source_tree_identity",
        "status_sha256",
    }
    _exact_fields(
        before,
        expected_fields,
        f"observations.{system}.mutation_sentinel.before",
    )
    _exact_fields(
        after,
        expected_fields,
        f"observations.{system}.mutation_sentinel.after",
    )

    if before != after:
        raise ReleaseEvidenceFailure(
            f"platform mutation sentinel does not close: {system}"
        )
    if before["candidate_commit"] != candidate:
        raise ReleaseEvidenceFailure(
            f"platform mutation candidate mismatch: {system}"
        )
    if before["source_tree_identity"] != source_tree:
        raise ReleaseEvidenceFailure(
            f"platform mutation source-tree mismatch: {system}"
        )

    status_identity = before["status_sha256"]
    if not isinstance(status_identity, str) or len(status_identity) != 64:
        raise ReleaseEvidenceFailure(
            f"platform mutation status identity is invalid: {system}"
        )


def _validate_platform_observation(
    observation: object,
    *,
    candidate: str,
    source_tree: str,
) -> str:
    value = _object(observation, "observation")
    required = {
        "schema",
        "candidate_commit",
        "source_tree_identity",
        "platform",
        "python",
        "git",
        "filesystem",
        "semantic_probe",
        "mutation_sentinel",
        "obligations",
        "gates",
        "limitations",
        "outcome",
    }
    _exact_fields(value, required, "observation")

    if value.get("schema") != PLATFORM_OBSERVATION_SCHEMA:
        raise ReleaseEvidenceFailure(
            "platform observation schema is invalid"
        )
    if value.get("candidate_commit") != candidate:
        raise ReleaseEvidenceFailure(
            "platform observation candidate mismatch"
        )
    if value.get("source_tree_identity") != source_tree:
        raise ReleaseEvidenceFailure(
            "platform observation source-tree mismatch"
        )
    if value.get("outcome") != "pass":
        raise ReleaseEvidenceFailure(
            "platform observation did not pass"
        )

    platform = _object(value.get("platform"), "observation.platform")
    system = platform.get("system")
    if system not in _REQUIRED_SYSTEMS:
        raise ReleaseEvidenceFailure(
            f"unknown platform observation: {system!r}"
        )

    probe = _object(
        value.get("semantic_probe"),
        f"observations.{system}.semantic_probe",
    )
    if probe.get("exit_code") != 0:
        raise ReleaseEvidenceFailure(
            f"platform semantic probe did not pass: {system}"
        )

    obligations = _object(
        value.get("obligations"),
        f"observations.{system}.obligations",
    )
    if obligations != {
        _PLATFORM_OBLIGATION: {"outcome": "partial"}
    }:
        raise ReleaseEvidenceFailure(
            f"platform observation obligation authority is invalid: "
            f"{system}"
        )

    gates = _object(
        value.get("gates"),
        f"observations.{system}.gates",
    )
    if gates != {_PLATFORM_GATE: {"outcome": "partial"}}:
        raise ReleaseEvidenceFailure(
            f"platform observation gate authority is invalid: {system}"
        )
    if "G8" in gates:
        raise ReleaseEvidenceFailure(
            f"platform observation must not claim G8: {system}"
        )

    _pass_mutation_sentinel(
        value.get("mutation_sentinel"),
        system=system,
        candidate=candidate,
        source_tree=source_tree,
    )
    return system


def validate_platform_matrix(
    document: dict[str, Any],
    *,
    candidate: str,
    source_tree: str,
) -> dict[str, Any]:
    """Validate complete exact-candidate Linux and Windows evidence."""

    required = {
        "schema",
        "candidate_commit",
        "source_tree_identity",
        "required_systems",
        "observed_systems",
        "observations",
        "missing_systems",
        "obligations",
        "gates",
        "limitations",
        "outcome",
    }
    _exact_fields(document, required, "matrix")

    if document.get("schema") != PLATFORM_MATRIX_SCHEMA:
        raise ReleaseEvidenceFailure(
            "platform matrix schema is invalid"
        )
    if document.get("candidate_commit") != candidate:
        raise ReleaseEvidenceFailure(
            "platform matrix candidate mismatch"
        )
    if document.get("source_tree_identity") != source_tree:
        raise ReleaseEvidenceFailure(
            "platform matrix source-tree mismatch"
        )
    if document.get("outcome") != "pass":
        raise ReleaseEvidenceFailure(
            "platform matrix did not pass"
        )
    if document.get("required_systems") != list(_REQUIRED_SYSTEMS):
        raise ReleaseEvidenceFailure(
            "platform matrix required systems are invalid"
        )
    if document.get("observed_systems") != list(_REQUIRED_SYSTEMS):
        raise ReleaseEvidenceFailure(
            "platform matrix observed systems are incomplete"
        )
    if document.get("missing_systems") != []:
        raise ReleaseEvidenceFailure(
            "platform matrix contains missing systems"
        )

    observations = document.get("observations")
    if not isinstance(observations, list):
        raise ReleaseEvidenceFailure(
            "platform matrix observations must be an array"
        )
    if len(observations) != len(_REQUIRED_SYSTEMS):
        raise ReleaseEvidenceFailure(
            "platform matrix must contain exactly two observations"
        )

    systems = tuple(
        _validate_platform_observation(
            observation,
            candidate=candidate,
            source_tree=source_tree,
        )
        for observation in observations
    )
    if len(set(systems)) != len(systems):
        raise ReleaseEvidenceFailure(
            "platform matrix contains a duplicate observation"
        )
    if set(systems) != set(_REQUIRED_SYSTEMS):
        raise ReleaseEvidenceFailure(
            "platform matrix lacks Linux or Windows evidence"
        )
    if list(systems) != list(_REQUIRED_SYSTEMS):
        raise ReleaseEvidenceFailure(
            "platform matrix observation order is not canonical"
        )

    obligations = _object(
        document.get("obligations"),
        "matrix.obligations",
    )
    if obligations != {
        _PLATFORM_OBLIGATION: {"outcome": "pass"}
    }:
        raise ReleaseEvidenceFailure(
            "platform matrix obligation authority must equal GD01-034"
        )

    gates = _object(document.get("gates"), "matrix.gates")
    if gates != {_PLATFORM_GATE: {"outcome": "partial"}}:
        raise ReleaseEvidenceFailure(
            "platform matrix must claim only partial G7"
        )
    if "G8" in gates:
        raise ReleaseEvidenceFailure(
            "platform matrix must not claim G8"
        )

    limitations = document.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        raise ReleaseEvidenceFailure(
            "platform matrix limitations are invalid"
        )

    return document

def _validate_resource_mutation_sentinel(
    document: dict[str, Any],
    *,
    candidate: str,
    source_tree: str,
) -> None:
    sentinel = _object(
        document.get("mutation_sentinel"),
        "resource.mutation_sentinel",
    )
    if set(sentinel) != {"before", "after", "outcome"}:
        raise ReleaseEvidenceFailure(
            "resource mutation sentinel fields are invalid"
        )
    if sentinel.get("outcome") != "pass":
        raise ReleaseEvidenceFailure(
            "resource mutation sentinel did not pass"
        )

    before = _object(
        sentinel.get("before"),
        "resource.mutation_sentinel.before",
    )
    after = _object(
        sentinel.get("after"),
        "resource.mutation_sentinel.after",
    )

    expected_fields = {
        "candidate_commit",
        "source_tree_identity",
        "status_sha256",
    }
    _exact_fields(
        before,
        expected_fields,
        "resource.mutation_sentinel.before",
    )
    _exact_fields(
        after,
        expected_fields,
        "resource.mutation_sentinel.after",
    )

    if before != after:
        raise ReleaseEvidenceFailure(
            "resource mutation sentinel does not close"
        )
    if before["candidate_commit"] != candidate:
        raise ReleaseEvidenceFailure(
            "resource mutation candidate mismatch"
        )
    if before["source_tree_identity"] != source_tree:
        raise ReleaseEvidenceFailure(
            "resource mutation source-tree mismatch"
        )


def validate_g7_composition(
    platform_matrix: dict[str, Any],
    resource_bounds: dict[str, Any],
    *,
    candidate: str,
    source_tree: str,
) -> tuple[set[str], set[str]]:
    """Return only GD01-034 and G7 after strict conjunction."""

    validate_platform_matrix(
        platform_matrix,
        candidate=candidate,
        source_tree=source_tree,
    )

    if (
        resource_bounds.get("candidate_commit") != candidate
        or resource_bounds.get("source_tree_identity") != source_tree
    ):
        raise ReleaseEvidenceFailure(
            "resource evidence exact-candidate identity mismatch"
        )
    if resource_bounds.get("outcome") != "pass":
        raise ReleaseEvidenceFailure(
            "resource evidence did not pass"
        )

    resource_obligations = validated_pass_claims(
        resource_bounds,
        "obligations",
        ("GD01-031",),
    )
    if resource_obligations != {"GD01-031"}:
        raise ReleaseEvidenceFailure(
            "resource evidence must pass exactly GD01-031"
        )

    resource_gates = validated_pass_claims(
        resource_bounds,
        "gates",
        ("G6", "G7"),
    )
    if "G6" not in resource_gates:
        raise ReleaseEvidenceFailure(
            "resource evidence must pass G6"
        )
    if "G7" in resource_gates:
        raise ReleaseEvidenceFailure(
            "resource evidence alone must not pass G7"
        )

    _validate_resource_mutation_sentinel(
        resource_bounds,
        candidate=candidate,
        source_tree=source_tree,
    )

    return {"GD01-034"}, {"G7"}
