#!/usr/bin/env python3
"""Produce one exact-candidate platform observation without overstating support."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "gitdrift-platform-observation-v1"
SEMANTIC_PROBE_MODULES = (
    "tests.test_identity",
    "tests.test_native_investigation",
    "tests.test_state_comparison_matrix",
)
OBLIGATION_CLAIMS = {"GD01-034": "partial"}
GATE_CLAIMS = {"G7": "partial"}
LIMITATIONS = (
    "One observation does not establish the complete required platform matrix.",
    "Platforms absent from candidate-bound observations remain untested.",
)


class AcceptanceFailure(RuntimeError):
    """Platform evidence could not be established truthfully."""


def _command(
    root: Path,
    arguments: Sequence[str],
) -> str:
    completed = subprocess.run(
        list(arguments),
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    if completed.returncode:
        raise AcceptanceFailure(
            completed.stderr.strip()
            or f"command failed: {' '.join(arguments)}"
        )
    return completed.stdout.strip()


def _git(
    root: Path,
    *arguments: str,
) -> str:
    return _command(root, ("git", *arguments))


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _claims(
    values: dict[str, str],
) -> dict[str, dict[str, str]]:
    return {
        identity: {"outcome": outcome}
        for identity, outcome in sorted(values.items())
    }


def validate_document(
    document: dict[str, Any],
) -> None:
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
    if set(document) != required:
        raise AcceptanceFailure(
            "platform observation fields do not match the schema"
        )
    if (
        document["schema"] != SCHEMA
        or document["outcome"] != "pass"
    ):
        raise AcceptanceFailure(
            "platform observation root is invalid"
        )
    if document["obligations"] != _claims(
        OBLIGATION_CLAIMS
    ):
        raise AcceptanceFailure(
            "platform obligation claims are invalid"
        )
    if document["gates"] != _claims(GATE_CLAIMS):
        raise AcceptanceFailure(
            "platform gate claims are invalid"
        )
    if document["limitations"] != list(LIMITATIONS):
        raise AcceptanceFailure(
            "platform limitations are invalid"
        )

    for field in (
        "platform",
        "python",
        "git",
        "filesystem",
        "semantic_probe",
    ):
        if (
            not isinstance(document[field], dict)
            or not document[field]
        ):
            raise AcceptanceFailure(
                f"platform observation lacks {field}"
            )

    sentinel = document["mutation_sentinel"]
    if (
        not isinstance(sentinel, dict)
        or sentinel.get("outcome") != "pass"
    ):
        raise AcceptanceFailure(
            "platform mutation sentinel is invalid"
        )
    if sentinel.get("before") != sentinel.get("after"):
        raise AcceptanceFailure(
            "platform mutation sentinel does not close"
        )


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    candidate = _git(
        root,
        "rev-parse",
        "HEAD",
    )
    tree = _git(
        root,
        "rev-parse",
        "HEAD^{tree}",
    )
    status = _git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        raise AcceptanceFailure(
            "platform observation requires a clean candidate"
        )

    probe_command = (
        sys.executable,
        "-m",
        "unittest",
        "-q",
        *SEMANTIC_PROBE_MODULES,
    )
    probe = subprocess.run(
        probe_command,
        cwd=root,
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=1_200,
        check=False,
    )
    if probe.returncode:
        raise AcceptanceFailure(
            "platform semantic probe failed; "
            f"stdout_sha256={_sha256(probe.stdout)}; "
            f"stderr_sha256={_sha256(probe.stderr)}"
        )
    before = {
        "candidate_commit": candidate,
        "source_tree_identity": tree,
        "status_sha256": _sha256(
            status.encode("utf-8")
        ),
    }

    document: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_commit": candidate,
        "source_tree_identity": tree,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "python": {
            "implementation": (
                platform.python_implementation()
            ),
            "version": platform.python_version(),
        },
        "git": {
            "version": _command(
                root,
                ("git", "--version"),
            )
        },
        "semantic_probe": {
            "modules": list(SEMANTIC_PROBE_MODULES),
            "exit_code": probe.returncode,
            "stdout_sha256": _sha256(probe.stdout),
            "stderr_sha256": _sha256(probe.stderr),
        },
        "filesystem": {
            "case_normalization": os.path.normcase(
                "GitDrift"
            ),
            "path_separator": os.sep,
            "symlink_supported": hasattr(
                os,
                "symlink",
            ),
        },
        "mutation_sentinel": {
            "before": before,
            "after": {
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
                    ).encode("utf-8")
                ),
            },
            "outcome": "pass",
        },
        "obligations": _claims(
            OBLIGATION_CLAIMS
        ),
        "gates": _claims(GATE_CLAIMS),
        "limitations": list(LIMITATIONS),
        "outcome": "pass",
    }
    validate_document(document)
    return document


def main(
    argv: Sequence[str] | None = None,
) -> int:
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
