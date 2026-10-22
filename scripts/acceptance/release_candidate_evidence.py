"""Application orchestration for exact-candidate release evidence."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

from release_evidence_contracts import (
    AGGREGATED_GATES,
    INSTALLED_OBLIGATIONS,
    INSTALLED_SCHEMA,
    REQUIRED_GATES,
    REQUIRED_OBLIGATIONS,
    SCHEMA,
    SYNTHETIC_SCHEMA,
    CommandSpec,
    EvidenceInputs,
    ReleaseEvidenceFailure,
)
from release_evidence_coverage import coverage_records, is_complete
from release_evidence_documents import load_evidence
from release_evidence_process import git, run_command


def _command_specs(
    synthetic_path: Path,
    installed_path: Path,
) -> tuple[CommandSpec, ...]:
    return (
        CommandSpec(
            "canonical-validation",
            (sys.executable, "scripts/validation/validate.py"),
        ),
        CommandSpec(
            "synthetic-state-awareness",
            (
                sys.executable,
                "scripts/acceptance/state_awareness_synthetic.py",
                "--output",
                str(synthetic_path),
            ),
        ),
        CommandSpec(
            "installed-distribution",
            (
                sys.executable,
                "scripts/acceptance/installed_distribution.py",
                "--output",
                str(installed_path),
            ),
        ),
    )


def _collect_inputs(
    root: Path,
    candidate: str,
    evidence_root: Path,
) -> EvidenceInputs:
    synthetic_path = evidence_root / "synthetic.json"
    installed_path = evidence_root / "installed.json"
    commands = tuple(
        run_command(root, specification)
        for specification in _command_specs(synthetic_path, installed_path)
    )
    failed = tuple(item.identity for item in commands if item.outcome == "fail")
    if failed:
        raise ReleaseEvidenceFailure(
            "mandatory evidence command failed: " + ", ".join(failed)
        )
    return EvidenceInputs(
        commands=commands,
        synthetic=load_evidence(synthetic_path, SYNTHETIC_SCHEMA, candidate),
        installed=load_evidence(installed_path, INSTALLED_SCHEMA, candidate),
    )


def aggregate(root: Path) -> dict[str, Any]:
    """Aggregate release evidence for one clean, committed candidate."""
    root = root.resolve()
    candidate = git(root, "rev-parse", "HEAD")
    if git(root, "status", "--porcelain=v1"):
        raise ReleaseEvidenceFailure(
            "release evidence requires a clean committed candidate"
        )
    with tempfile.TemporaryDirectory(
        prefix="gitdrift-release-evidence-"
    ) as directory:
        inputs = _collect_inputs(root, candidate, Path(directory))

    evidence_ids = tuple(item.identity for item in inputs.commands)
    covered_obligations = set(inputs.synthetic.get("obligations", ()))
    covered_obligations.update(INSTALLED_OBLIGATIONS)
    obligations = coverage_records(
        REQUIRED_OBLIGATIONS,
        covered_obligations,
        evidence_ids,
        "No exact-candidate executable evidence is aggregated yet.",
    )
    gates = coverage_records(
        REQUIRED_GATES,
        set(AGGREGATED_GATES),
        evidence_ids,
        "The required release-wide evidence tier is not aggregated yet.",
    )
    artifacts = inputs.installed.get("artifacts")
    return {
        "schema": SCHEMA,
        "candidate_commit": candidate,
        "source_tree_identity": git(root, "rev-parse", "HEAD^{tree}"),
        "commands": [item.to_dict() for item in inputs.commands],
        "generated_artifacts": artifacts if isinstance(artifacts, list) else [],
        "gates": gates,
        "obligations": obligations,
        "outcome": "pass" if is_complete(gates, obligations) else "blocked",
    }
