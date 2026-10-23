from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Any

SCHEMA = "gitdrift-gate-runner-contract-v1"
TEST_MODULES = (
    "tests.test_gate_runner_entrypoint",
    "tests.test_gate_runner_host",
    "tests.test_gate_runner_docker_integration",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git(root: pathlib.Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def repository_state(root: pathlib.Path) -> dict[str, str]:
    return {
        "candidate_commit": git(root, "rev-parse", "HEAD"),
        "source_tree_identity": git(root, "rev-parse", "HEAD^{tree}"),
        "status_sha256": sha256_text(
            git(
                root,
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            )
        ),
    }


def build_document(root: pathlib.Path) -> dict[str, Any]:
    before = repository_state(root)
    command = (
        sys.executable,
        "-m",
        "unittest",
        "-v",
        *TEST_MODULES,
    )
    completed = subprocess.run(
        command,
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    after = repository_state(root)
    mutation_outcome = "pass" if before == after else "fail"
    outcome = (
        "pass"
        if completed.returncode == 0 and mutation_outcome == "pass"
        else "fail"
    )
    return {
        "schema": SCHEMA,
        "candidate_commit": before["candidate_commit"],
        "source_tree_identity": before["source_tree_identity"],
        "command": list(command),
        "test_modules": list(TEST_MODULES),
        "command_exit_code": completed.returncode,
        "stdout_sha256": sha256_text(completed.stdout),
        "stderr_sha256": sha256_text(completed.stderr),
        "mutation_sentinel": {
            "before": before,
            "after": after,
            "outcome": mutation_outcome,
        },
        "limitations": [
            "Docker integration tests are skipped unless "
            "GITDRIFT_DOCKER_INTEGRATION=1.",
            "Windows Docker execution additionally requires the Windows "
            "engine and pinned MinGit inputs.",
            "Native Windows observation remains a separate platform boundary.",
        ],
        "outcome": outcome,
    }


def validate_document(document: dict[str, Any]) -> None:
    if document.get("schema") != SCHEMA:
        raise ValueError("schema mismatch")
    if document.get("command_exit_code") != 0:
        raise ValueError("gate-runner contract tests failed")
    mutation = document.get("mutation_sentinel")
    if not isinstance(mutation, dict):
        raise ValueError("mutation sentinel is missing")
    if mutation.get("outcome") != "pass":
        raise ValueError("mutation sentinel did not pass")
    if mutation.get("before") != mutation.get("after"):
        raise ValueError("repository changed during validation")
    if document.get("outcome") != "pass":
        raise ValueError("contract validation did not pass")
    for key in ("stdout_sha256", "stderr_sha256"):
        value = document.get(key)
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError(f"{key} is invalid")


def write_json(path: pathlib.Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".working")
    temporary.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--root", default=".")
    result.add_argument("--output", required=True)
    return result


def main() -> int:
    arguments = parser().parse_args()
    root = pathlib.Path(arguments.root).resolve()
    document = build_document(root)
    try:
        validate_document(document)
    except ValueError as error:
        write_json(pathlib.Path(arguments.output), document)
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 1
    write_json(pathlib.Path(arguments.output), document)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
