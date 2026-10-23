#!/usr/bin/env python3
"""Produce candidate-bound evidence for existing contract-quality tests."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "gitdrift-contract-quality-acceptance-v1"
TEST_MODULES = (
    "tests.test_domain_records",
    "tests.test_git_state_comparison",
    "tests.test_identity",
    "tests.test_installed_distribution_acceptance",
    "tests.test_embedded_instruction_safety",
    "tests.test_markdown_extractor",
    "tests.test_native_investigation",
    "tests.test_native_compatibility",
    "tests.test_obligation_evaluation",
    "tests.test_python_extractor",
    "tests.test_raw_change_evidence",
    "tests.test_reference_closure",
    "tests.test_state_awareness_profile",
    "tests.test_working_tree_capture",
)
OBLIGATION_CLAIMS = {
    "GD01-024": "pass",
    "GD01-029": "pass",
    "GD01-032": "pass",
    "GD01-035": "pass",
}
GATE_CLAIMS = {
    "G5": "pass",
    "G6": "partial",
}
LIMITATIONS = (
    "G6 remains partial because complete resource-exhaustion evidence for GD01-031 is not part of this boundary.",
)


class AcceptanceFailure(RuntimeError):
    """The contract-quality evidence boundary could not pass truthfully."""


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
            completed.stderr.strip() or f"git {' '.join(arguments)} failed"
        )
    return completed.stdout.strip()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _run_tests(root: Path) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    source_path = str(root / "src")
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        source_path if not existing else os.pathsep.join((source_path, existing))
    )
    try:
        return subprocess.run(
            [sys.executable, "-m", "unittest", "-v", *TEST_MODULES],
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=1_200,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise AcceptanceFailure("contract-quality tests timed out") from error


def _claims(values: dict[str, str]) -> dict[str, dict[str, str]]:
    allowed = {"pass", "partial", "blocked"}
    if set(values.values()) - allowed:
        raise AcceptanceFailure(
            "contract-quality claims contain an invalid outcome"
        )
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
        "test_exit_code",
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
            "contract-quality evidence fields do not match the schema"
        )
    if document["schema"] != SCHEMA or document["outcome"] != "pass":
        raise AcceptanceFailure("contract-quality evidence root is invalid")
    if document["test_exit_code"] != 0:
        raise AcceptanceFailure(
            "contract-quality evidence records a failed test command"
        )
    if document["test_modules"] != list(TEST_MODULES):
        raise AcceptanceFailure(
            "contract-quality test-module identity is invalid"
        )
    if document["obligations"] != _claims(OBLIGATION_CLAIMS):
        raise AcceptanceFailure(
            "contract-quality obligation claims are invalid"
        )
    if document["gates"] != _claims(GATE_CLAIMS):
        raise AcceptanceFailure(
            "contract-quality gate claims are invalid"
        )
    if document["limitations"] != list(LIMITATIONS):
        raise AcceptanceFailure(
            "contract-quality limitations are invalid"
        )
    sentinel = document["mutation_sentinel"]
    if not isinstance(sentinel, dict) or sentinel.get("outcome") != "pass":
        raise AcceptanceFailure(
            "contract-quality mutation sentinel is invalid"
        )
    if sentinel.get("before") != sentinel.get("after"):
        raise AcceptanceFailure(
            "contract-quality mutation sentinel does not close"
        )


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    candidate = _git(root, "rev-parse", "HEAD")
    source_tree = _git(root, "rev-parse", "HEAD^{tree}")
    status_before = _git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status_before:
        raise AcceptanceFailure(
            "contract-quality acceptance requires a clean committed candidate"
        )

    completed = _run_tests(root)

    candidate_after = _git(root, "rev-parse", "HEAD")
    source_tree_after = _git(root, "rev-parse", "HEAD^{tree}")
    status_after = _git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    before = {
        "candidate_commit": candidate,
        "source_tree_identity": source_tree,
        "status_sha256": _sha256(status_before.encode("utf-8")),
    }
    after = {
        "candidate_commit": candidate_after,
        "source_tree_identity": source_tree_after,
        "status_sha256": _sha256(status_after.encode("utf-8")),
    }
    if before != after:
        raise AcceptanceFailure(
            "repository candidate changed during contract-quality tests"
        )
    if completed.returncode:
        raise AcceptanceFailure(
            "contract-quality test boundary failed; "
            f"stdout_sha256={_sha256(completed.stdout)}; "
            f"stderr_sha256={_sha256(completed.stderr)}"
        )

    document: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_commit": candidate,
        "source_tree_identity": source_tree,
        "test_modules": list(TEST_MODULES),
        "test_exit_code": completed.returncode,
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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        document = run(arguments.root)
        payload = (
            json.dumps(
                document,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n"
        )
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            payload,
            encoding="utf-8",
            newline="\n",
        )
        return 0
    except AcceptanceFailure as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
