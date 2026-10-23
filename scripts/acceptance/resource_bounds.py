#!/usr/bin/env python3
"""Produce candidate-bound evidence for bounded operational behavior."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "gitdrift-resource-bounds-acceptance-v1"
TEST_MODULES = (
    "tests.test_git_command_timeouts",
    "tests.test_state_awareness_output_budget",
    "tests.test_state_awareness_profile",
    "tests.test_working_tree_capture",
)
OBLIGATION_CLAIMS = {"GD01-031": "pass"}
GATE_CLAIMS = {"G6": "pass", "G7": "partial"}
LIMITATIONS = (
    "G7 remains partial until this resource record is aggregated with "
    "the exact-candidate Linux and Windows platform matrix.",
)


class AcceptanceFailure(RuntimeError):
    """Resource-bound evidence could not be established truthfully."""


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=30,
        check=False,
    )
    if completed.returncode:
        raise AcceptanceFailure(
            completed.stderr.strip()
            or f"git {' '.join(arguments)} failed"
        )
    return completed.stdout.strip()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _claims(
    values: dict[str, str],
) -> dict[str, dict[str, str]]:
    return {
        identity: {"outcome": outcome}
        for identity, outcome in sorted(values.items())
    }


def validate_document(document: dict[str, Any]) -> None:
    required = {
        "schema",
        "candidate_commit",
        "source_tree_identity",
        "test_modules",
        "command",
        "command_exit_code",
        "stdout_sha256",
        "stderr_sha256",
        "mutation_sentinel",
        "obligations",
        "gates",
        "limitations",
        "outcome",
    }
    if set(document) != required:
        raise AcceptanceFailure(
            "resource evidence fields do not match the schema"
        )
    if (
        document["schema"] != SCHEMA
        or document["outcome"] != "pass"
    ):
        raise AcceptanceFailure(
            "resource evidence root is invalid"
        )
    if document["command_exit_code"] != 0:
        raise AcceptanceFailure(
            "resource evidence records a failed test command"
        )
    if document["test_modules"] != list(TEST_MODULES):
        raise AcceptanceFailure(
            "resource evidence test-module identity is invalid"
        )
    if document["obligations"] != _claims(OBLIGATION_CLAIMS):
        raise AcceptanceFailure(
            "resource evidence obligation claims are invalid"
        )
    if document["gates"] != _claims(GATE_CLAIMS):
        raise AcceptanceFailure(
            "resource evidence gate claims are invalid"
        )
    if document["limitations"] != list(LIMITATIONS):
        raise AcceptanceFailure(
            "resource evidence limitations are invalid"
        )
    sentinel = document["mutation_sentinel"]
    if (
        not isinstance(sentinel, dict)
        or sentinel.get("outcome") != "pass"
    ):
        raise AcceptanceFailure(
            "resource evidence mutation sentinel is invalid"
        )
    if sentinel.get("before") != sentinel.get("after"):
        raise AcceptanceFailure(
            "resource evidence mutation sentinel does not close"
        )


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    candidate = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    status = _git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        raise AcceptanceFailure(
            "resource acceptance requires a clean candidate"
        )

    command = (
        sys.executable,
        "-m",
        "unittest",
        "-v",
        *TEST_MODULES,
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")

    try:
        completed = subprocess.run(
            command,
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=1_200,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise AcceptanceFailure(
            "resource acceptance tests timed out"
        ) from error

    after = {
        "candidate_commit": _git(
            root,
            "rev-parse",
            "HEAD",
        ),
        "source_tree_identity": _git(
            root,
            "rev-parse",
            "HEAD^{tree}",
        ),
        "status_sha256": _sha256(
            _git(
                root,
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ).encode()
        ),
    }
    before = {
        "candidate_commit": candidate,
        "source_tree_identity": tree,
        "status_sha256": _sha256(status.encode()),
    }

    if before != after:
        raise AcceptanceFailure(
            "candidate changed during resource acceptance"
        )
    if completed.returncode:
        raise AcceptanceFailure(
            "resource acceptance tests failed; "
            f"stdout_sha256={_sha256(completed.stdout)}; "
            f"stderr_sha256={_sha256(completed.stderr)}"
        )

    document: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_commit": candidate,
        "source_tree_identity": tree,
        "test_modules": list(TEST_MODULES),
        "command": list(command),
        "command_exit_code": completed.returncode,
        "stdout_sha256": _sha256(completed.stdout),
        "stderr_sha256": _sha256(completed.stderr),
        "mutation_sentinel": {
            "before": before,
            "after": after,
            "outcome": "pass",
        },
        "obligations": _claims(OBLIGATION_CLAIMS),
        "gates": _claims(GATE_CLAIMS),
        "limitations": list(LIMITATIONS),
        "outcome": "pass",
    }
    validate_document(document)
    return document


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )
    arguments = parser.parse_args(argv)

    try:
        document = run(arguments.root)
        arguments.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        arguments.output.write_text(
            json.dumps(
                document,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return 0
    except AcceptanceFailure as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
