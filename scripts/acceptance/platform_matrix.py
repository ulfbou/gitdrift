#!/usr/bin/env python3
"""Combine exact-candidate observations for the required platform matrix."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "gitdrift-platform-matrix-v1"
OBSERVATION_SCHEMA = "gitdrift-platform-observation-v1"
REQUIRED_SYSTEMS = ("Linux", "Windows")


class MatrixFailure(RuntimeError):
    """The required platform matrix is incomplete or inconsistent."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise MatrixFailure(f"cannot load platform observation {path}: {error}") from error
    if not isinstance(value, dict):
        raise MatrixFailure(f"platform observation root is not an object: {path}")
    return value


def combine(paths: Sequence[Path]) -> dict[str, Any]:
    if not paths:
        raise MatrixFailure("at least one platform observation is required")
    observations = tuple(_load(path) for path in paths)
    candidate = observations[0].get("candidate_commit")
    tree = observations[0].get("source_tree_identity")
    by_system: dict[str, dict[str, Any]] = {}
    for observation in observations:
        if observation.get("schema") != OBSERVATION_SCHEMA or observation.get("outcome") != "pass":
            raise MatrixFailure("platform observation schema or outcome is invalid")
        if observation.get("candidate_commit") != candidate or observation.get("source_tree_identity") != tree:
            raise MatrixFailure("platform observations do not belong to one exact candidate")
        platform_value = observation.get("platform")
        system = platform_value.get("system") if isinstance(platform_value, dict) else None
        if system not in REQUIRED_SYSTEMS:
            raise MatrixFailure(f"platform observation is not required: {system!r}")
        if system in by_system:
            raise MatrixFailure(f"duplicate platform observation: {system}")
        probe = observation.get("semantic_probe")
        if not isinstance(probe, dict) or probe.get("exit_code") != 0:
            raise MatrixFailure(f"platform semantic probe did not pass: {system}")
        by_system[system] = observation
    missing = tuple(system for system in REQUIRED_SYSTEMS if system not in by_system)
    complete = not missing
    return {
        "schema": SCHEMA,
        "candidate_commit": candidate,
        "source_tree_identity": tree,
        "required_systems": list(REQUIRED_SYSTEMS),
        "observed_systems": sorted(by_system),
        "observations": [by_system[system] for system in sorted(by_system)],
        "missing_systems": list(missing),
        "obligations": {"GD01-034": {"outcome": "pass" if complete else "blocked"}},
        "gates": {"G7": {"outcome": "partial"}},
        "limitations": [
            "G7 remains partial until resource-bound GD01-031 passes."
        ],
        "outcome": "pass" if complete else "blocked",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observation", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        document = combine(arguments.observation)
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return 0 if document["outcome"] == "pass" else 1
    except MatrixFailure as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
