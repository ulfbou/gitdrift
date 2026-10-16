#!/usr/bin/env python3
"""Run the synthetic state-awareness acceptance boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


SCHEMA = "gitdrift-state-awareness-synthetic-acceptance-v1"

TEST_MODULES = (
    "tests.test_head_capture",
    "tests.test_upstream_capture",
    "tests.test_index_capture",
    "tests.test_working_tree_capture",
    "tests.test_state_comparison_matrix",
    "tests.test_git_state_comparison",
    "tests.test_state_comparison_composition",
    "tests.test_state_awareness_profile",
    "tests.test_state_awareness_cli",
    "tests.test_native_investigation",
    "tests.test_discovery",
)

SCENARIOS = (
    "aligned-clean-repository",
    "no-staged-or-unstaged-changes",
    "local-branch-behind-captured-upstream",
    "staged-candidate",
    "unstaged-candidate",
    "simultaneous-upstream-and-staged-candidates",
    "staged-and-working-tree-divergence",
    "absent-or-unselected-upstream",
    "deterministic-repeated-execution",
    "zero-repository-mutation",
)

OBLIGATIONS = (
    "GD01-001",
    "GD01-002",
    "GD01-003",
    "GD01-004",
    "GD01-005",
    "GD01-006",
    "GD01-007",
    "GD01-008",
    "GD01-018",
    "GD01-019",
    "GD01-020",
    "GD01-021",
    "GD01-022",
    "GD01-023",
    "GD01-027",
    "GD01-028",
    "GD01-029",
    "GD01-030",
    "GD01-036",
    "GD01-037",
)

RELEASE_GATES = (
    "G2",
    "G3",
    "G4",
    "G5",
    "G7",
    "G8",
)


class AcceptanceFailure(RuntimeError):
    """The synthetic acceptance boundary failed."""


def _run(
    arguments: Sequence[str],
    *,
    root: Path,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    source_path = str(root / "src")
    existing = environment.get("PYTHONPATH")

    environment["PYTHONPATH"] = (
        source_path
        if not existing
        else os.pathsep.join((source_path, existing))
    )

    return subprocess.run(
        list(arguments),
        cwd=root,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )


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


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()

    candidate_commit = _git(root, "rev-parse", "HEAD")
    status_before = _git(
        root,
        "status",
        "--porcelain=v1",
    )

    if status_before:
        raise AcceptanceFailure(
            "synthetic acceptance requires "
            "a clean committed candidate"
        )

    completed = _run(
        (
            sys.executable,
            "-m",
            "unittest",
            "-v",
            *TEST_MODULES,
        ),
        root=root,
    )

    status_after = _git(
        root,
        "status",
        "--porcelain=v1",
    )
    head_after = _git(root, "rev-parse", "HEAD")

    if status_after != status_before:
        raise AcceptanceFailure(
            "acceptance execution changed "
            "repository candidate state"
        )

    if head_after != candidate_commit:
        raise AcceptanceFailure(
            "acceptance execution changed candidate HEAD"
        )

    combined_output = (
        completed.stdout + "\n" + completed.stderr
    ).encode("utf-8")

    outcome = (
        "pass"
        if completed.returncode == 0
        else "fail"
    )

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_commit": candidate_commit,
        "test_modules": list(TEST_MODULES),
        "scenarios": [
            {
                "id": scenario,
                "outcome": outcome,
            }
            for scenario in SCENARIOS
        ],
        "obligations": list(OBLIGATIONS),
        "release_gates": list(RELEASE_GATES),
        "mutation_sentinel": {
            "head_unchanged": (
                head_after == candidate_commit
            ),
            "repository_status_unchanged": (
                status_after == status_before
            ),
        },
        "test_output_sha256": _sha256(
            combined_output
        ),
        "test_exit_code": completed.returncode,
        "outcome": outcome,
    }

    if completed.returncode:
        raise AcceptanceFailure(
            "synthetic state-awareness "
            "test boundary failed"
        )

    return result


def _parser() -> argparse.ArgumentParser:
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
    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    arguments = _parser().parse_args(argv)

    try:
        result = run(arguments.root)
        payload = (
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n"
        )

        arguments.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        arguments.output.write_text(
            payload,
            encoding="utf-8",
            newline="\n",
        )
    except AcceptanceFailure as error:
        print(str(error), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
