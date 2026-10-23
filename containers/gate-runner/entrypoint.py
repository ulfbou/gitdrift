from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
from collections.abc import Sequence
from typing import Any

RUNNER_CONTRACT = "gitdrift-gate-runner-v1"


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("gate command must be a non-empty array")
    if not all(isinstance(item, str) and item for item in value):
        raise ValueError("gate command contains an invalid element")
    return tuple(value)


def load_manifest(path: pathlib.Path) -> dict[str, tuple[str, ...]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema") != "gitdrift-gate-manifest-v1":
        raise ValueError("unsupported gate manifest schema")
    if document.get("runner_contract") != RUNNER_CONTRACT:
        raise ValueError("gate manifest runner contract mismatch")
    gates = document.get("gates")
    if not isinstance(gates, dict) or not gates:
        raise ValueError("gate manifest must declare gates")
    result: dict[str, tuple[str, ...]] = {}
    for name, value in gates.items():
        if not isinstance(name, str) or not name:
            raise ValueError("gate name must be non-empty text")
        if not isinstance(value, dict):
            raise ValueError(f"gate {name!r} must be an object")
        result[name] = command_text(value.get("command"))
    return result


def run(command: Sequence[str], *, cwd: pathlib.Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        tuple(command), cwd=cwd, check=check,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )


def git(root: pathlib.Path, *arguments: str) -> str:
    return run(("git", "-C", str(root), *arguments)).stdout.strip()


def environment() -> dict[str, Any]:
    return {
        "runner_contract": RUNNER_CONTRACT,
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "platform_machine": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "git_version": run(("git", "--version")).stdout.strip(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
    }


def prepare_candidate(
    *, request_dir: pathlib.Path, workspace: pathlib.Path,
    expected_commit: str, expected_tree: str, expected_bundle_sha256: str,
) -> dict[str, str]:
    bundle = request_dir / "candidate.bundle"
    if not bundle.is_file():
        raise RuntimeError(f"candidate bundle is missing: {bundle}")
    actual_hash = sha256_file(bundle)
    if actual_hash != expected_bundle_sha256:
        raise RuntimeError(
            "candidate bundle SHA-256 mismatch: "
            f"expected={expected_bundle_sha256} actual={actual_hash}"
        )
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    run(("git", "clone", "--no-checkout", str(bundle), str(workspace)))
    run(("git", "-C", str(workspace), "checkout", "--detach", expected_commit))
    actual_commit = git(workspace, "rev-parse", "HEAD")
    actual_tree = git(workspace, "rev-parse", "HEAD^{tree}")
    status = git(workspace, "status", "--porcelain=v1", "--untracked-files=all")
    if actual_commit != expected_commit:
        raise RuntimeError(f"candidate commit mismatch: expected={expected_commit} actual={actual_commit}")
    if actual_tree != expected_tree:
        raise RuntimeError(f"candidate tree mismatch: expected={expected_tree} actual={actual_tree}")
    if status:
        raise RuntimeError("candidate workspace is not clean before execution")
    return {"commit": actual_commit, "tree": actual_tree, "bundle_sha256": actual_hash}


def inspect_runner(manifest: pathlib.Path) -> int:
    gates = load_manifest(manifest)
    print(json.dumps({
        "schema": "gitdrift-gate-runner-inspection-v1",
        **environment(),
        "known_gates": sorted(gates),
        "candidate_embedded": False,
        "outcome": "pass",
    }, indent=2, sort_keys=True))
    return 0


def execute_gate(arguments: argparse.Namespace) -> int:
    manifest = pathlib.Path(arguments.manifest)
    gates = load_manifest(manifest)
    command_template = gates[arguments.gate]
    workspace = pathlib.Path(arguments.workspace)
    evidence = pathlib.Path(arguments.evidence)
    request_dir = pathlib.Path(arguments.request)
    evidence.mkdir(parents=True, exist_ok=True)
    candidate = prepare_candidate(
        request_dir=request_dir,
        workspace=workspace,
        expected_commit=arguments.candidate_commit,
        expected_tree=arguments.candidate_tree,
        expected_bundle_sha256=arguments.bundle_sha256,
    )
    replacements = {"{python}": sys.executable, "{workspace}": str(workspace), "{evidence}": str(evidence)}
    command = tuple(replacements.get(part, part) for part in command_template)
    before = git(workspace, "status", "--porcelain=v1", "--untracked-files=all")
    completed = run(command, cwd=workspace, check=False)
    after = git(workspace, "status", "--porcelain=v1", "--untracked-files=all")
    before_hash = hashlib.sha256(before.encode()).hexdigest()
    after_hash = hashlib.sha256(after.encode()).hexdigest()
    mutation_outcome = "pass" if not before and not after and before_hash == after_hash else "fail"
    artifacts = [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(evidence.iterdir())
        if path.is_file() and path.name != "gate-execution.json"
    ]
    outcome = "pass" if completed.returncode == 0 and mutation_outcome == "pass" else "fail"
    envelope = {
        "schema": "gitdrift-gate-execution-v1",
        "runner": environment(), "gate": arguments.gate, "candidate": candidate,
        "execution": {
            "command": list(command), "exit_code": completed.returncode,
            "stdout_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
            "stderr_sha256": hashlib.sha256(completed.stderr.encode()).hexdigest(),
        },
        "artifacts": artifacts,
        "mutation_sentinel": {
            "before_status_sha256": before_hash,
            "after_status_sha256": after_hash,
            "outcome": mutation_outcome,
        },
        "outcome": outcome,
    }
    (evidence / "gate-execution.json").write_text(
        json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode if mutation_outcome == "pass" else 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--manifest", default=str(pathlib.Path(__file__).with_name("gates.json")))
    subparsers = result.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("inspect")
    execute = subparsers.add_parser("run")
    execute.add_argument("--gate", required=True)
    execute.add_argument("--candidate-commit", required=True)
    execute.add_argument("--candidate-tree", required=True)
    execute.add_argument("--bundle-sha256", required=True)
    execute.add_argument("--request", required=True)
    execute.add_argument("--workspace", required=True)
    execute.add_argument("--evidence", required=True)
    return result


def main() -> int:
    arguments = parser().parse_args()
    gates = load_manifest(pathlib.Path(arguments.manifest))
    if arguments.operation == "inspect":
        return inspect_runner(pathlib.Path(arguments.manifest))
    if arguments.gate not in gates:
        raise SystemExit(f"unknown gate: {arguments.gate}")
    return execute_gate(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
