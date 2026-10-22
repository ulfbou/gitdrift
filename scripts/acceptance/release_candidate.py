#!/usr/bin/env python3
"""Aggregate exact-candidate Gitdrift 0.1 release evidence without overclaiming."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "gitdrift-release-candidate-evidence-v1"
REQUIRED_GATES = tuple(f"G{index}" for index in range(9))
REQUIRED_OBLIGATIONS = tuple(f"GD01-{index:03d}" for index in range(1, 38))

class ReleaseEvidenceFailure(RuntimeError):
    """Release evidence could not be established truthfully."""

@dataclass(frozen=True, slots=True)
class CommandEvidence:
    identity: str
    command: tuple[str, ...]
    exit_code: int
    stdout_sha256: str
    stderr_sha256: str

    @property
    def outcome(self) -> str:
        return "pass" if self.exit_code == 0 else "fail"

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity": self.identity,
            "command": list(self.command),
            "exit_code": self.exit_code,
            "stdout_sha256": self.stdout_sha256,
            "stderr_sha256": self.stderr_sha256,
            "outcome": self.outcome,
        }

def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

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
        raise ReleaseEvidenceFailure(
            completed.stderr.strip() or f"git {' '.join(arguments)} failed"
        )
    return completed.stdout.strip()

def _run(root: Path, identity: str, command: Sequence[str]) -> CommandEvidence:
    completed = subprocess.run(
        list(command),
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return CommandEvidence(
        identity=identity,
        command=tuple(command),
        exit_code=completed.returncode,
        stdout_sha256=_sha256(completed.stdout),
        stderr_sha256=_sha256(completed.stderr),
    )

def _load(path: Path, expected_schema: str, candidate: str) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReleaseEvidenceFailure(f"cannot load evidence {path}: {error}") from error
    if not isinstance(document, dict):
        raise ReleaseEvidenceFailure(f"evidence root is not an object: {path}")
    if document.get("schema") != expected_schema:
        raise ReleaseEvidenceFailure(f"unexpected evidence schema: {path}")
    if document.get("candidate_commit") != candidate:
        raise ReleaseEvidenceFailure(f"mixed candidate identity in evidence: {path}")
    if document.get("outcome") != "pass":
        raise ReleaseEvidenceFailure(f"evidence does not report pass: {path}")
    return document

def _record(
    outcome: str,
    evidence_ids: Sequence[str],
    limitation: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "outcome": outcome,
        "evidence_ids": list(evidence_ids),
    }
    if limitation is not None:
        result["limitation"] = limitation
    return result

def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    candidate = _git(root, "rev-parse", "HEAD")
    if _git(root, "status", "--porcelain=v1"):
        raise ReleaseEvidenceFailure(
            "release evidence requires a clean committed candidate"
        )

    with tempfile.TemporaryDirectory(
        prefix="gitdrift-release-evidence-"
    ) as directory:
        evidence_root = Path(directory)
        synthetic_path = evidence_root / "synthetic.json"
        installed_path = evidence_root / "installed.json"
        commands = (
            _run(
                root,
                "canonical-validation",
                (
                    sys.executable,
                    "scripts/validation/validate.py",
                ),
            ),
            _run(
                root,
                "synthetic-state-awareness",
                (
                    sys.executable,
                    "scripts/acceptance/state_awareness_synthetic.py",
                    "--output",
                    str(synthetic_path),
                ),
            ),
            _run(
                root,
                "installed-distribution",
                (
                    sys.executable,
                    "scripts/acceptance/installed_distribution.py",
                    "--output",
                    str(installed_path),
                ),
            ),
        )
        failed = tuple(
            item.identity
            for item in commands
            if item.exit_code != 0
        )
        if failed:
            raise ReleaseEvidenceFailure(
                "mandatory evidence command failed: "
                + ", ".join(failed)
            )
        synthetic = _load(
            synthetic_path,
            "gitdrift-state-awareness-synthetic-acceptance-v1",
            candidate,
        )
        installed = _load(
            installed_path,
            "gitdrift-installed-distribution-acceptance-v1",
            candidate,
        )

        evidence_ids = tuple(item.identity for item in commands)
        mapped_obligations = set(
            synthetic.get("obligations", ())
        )
        mapped_obligations.update(
            {
                "GD01-025",
                "GD01-026",
                "GD01-027",
            }
        )
        obligations = {
            obligation: _record(
                (
                    "pass"
                    if obligation in mapped_obligations
                    else "blocked"
                ),
                (
                    evidence_ids
                    if obligation in mapped_obligations
                    else ()
                ),
                (
                    None
                    if obligation in mapped_obligations
                    else (
                        "No exact-candidate executable evidence "
                        "is aggregated yet."
                    )
                ),
            )
            for obligation in REQUIRED_OBLIGATIONS
        }
        gate_passes = {
            "G0",
            "G1",
            "G2",
            "G3",
            "G4",
        }
        gates = {
            gate: _record(
                "pass" if gate in gate_passes else "blocked",
                evidence_ids if gate in gate_passes else (),
                (
                    None
                    if gate in gate_passes
                    else (
                        "The required release-wide evidence tier "
                        "is not aggregated yet."
                    )
                ),
            )
            for gate in REQUIRED_GATES
        }
        overall = (
            "pass"
            if all(
                item["outcome"] == "pass"
                for item in gates.values()
            )
            and all(
                item["outcome"] == "pass"
                for item in obligations.values()
            )
            else "blocked"
        )
        artifacts = installed.get("artifacts")
        return {
            "schema": SCHEMA,
            "candidate_commit": candidate,
            "source_tree_identity": _git(
                root,
                "rev-parse",
                "HEAD^{tree}",
            ),
            "commands": [
                item.to_dict()
                for item in commands
            ],
            "generated_artifacts": (
                artifacts
                if isinstance(artifacts, list)
                else []
            ),
            "gates": gates,
            "obligations": obligations,
            "outcome": overall,
        }

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

def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        result = run(arguments.root)
        arguments.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        arguments.output.write_text(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return 0 if result["outcome"] == "pass" else 2
    except ReleaseEvidenceFailure as error:
        print(str(error), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
