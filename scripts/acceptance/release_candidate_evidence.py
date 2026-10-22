"""Application orchestration for exact-candidate release evidence."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from release_evidence_contracts import (
    AGGREGATED_GATES,
    CORPUS_OBLIGATIONS,
    CORPUS_SCHEMA,
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

CORPUS_ROOT_ENV = "GITDRIFT_DX_ARTIFACTS_CORPUS_ROOT"
CORPUS_COMMIT = "0d49b22ddecab894d39bee30ecb49bf1353d7788"
CORPUS_TREE = "d463bb9cb56ba84d8e0b1584332cfd1a1565b075"


def _command_specs(
    synthetic_path: Path,
    installed_path: Path,
    corpus_path: Path,
    corpus_root: Path,
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
        CommandSpec(
            "dx-artifacts-corpus",
            (
                sys.executable,
                "scripts/acceptance/state_awareness_corpus.py",
                "--corpus-root",
                str(corpus_root),
                "--corpus-commit",
                CORPUS_COMMIT,
                "--corpus-tree",
                CORPUS_TREE,
                "--output",
                str(corpus_path),
            ),
        ),
    )


def _collect_inputs(
    root: Path,
    candidate: str,
    evidence_root: Path,
    corpus_root: Path,
) -> EvidenceInputs:
    synthetic_path = evidence_root / "synthetic.json"
    installed_path = evidence_root / "installed.json"
    corpus_path = evidence_root / "corpus.json"
    commands = tuple(
        run_command(root, specification)
        for specification in _command_specs(
            synthetic_path,
            installed_path,
            corpus_path,
            corpus_root,
        )
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
        corpus=load_evidence(corpus_path, CORPUS_SCHEMA, candidate),
    )


def aggregate(root: Path) -> dict[str, Any]:
    """Aggregate release evidence for one clean, committed candidate."""
    root = root.resolve()
    candidate = git(root, "rev-parse", "HEAD")
    if git(root, "status", "--porcelain=v1"):
        raise ReleaseEvidenceFailure(
            "release evidence requires a clean committed candidate"
        )
    corpus_value = os.environ.get(CORPUS_ROOT_ENV)
    if not corpus_value:
        raise ReleaseEvidenceFailure(
            f"{CORPUS_ROOT_ENV} must identify the pinned corpus worktree"
        )
    corpus_root = Path(corpus_value).resolve()
    with tempfile.TemporaryDirectory(
        prefix="gitdrift-release-evidence-"
    ) as directory:
        inputs = _collect_inputs(
            root,
            candidate,
            Path(directory),
            corpus_root,
        )
    evidence_ids = tuple(item.identity for item in inputs.commands)
    covered_obligations = set(inputs.synthetic.get("obligations", ()))
    covered_obligations.update(INSTALLED_OBLIGATIONS)
    covered_obligations.update(CORPUS_OBLIGATIONS)
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
        "corpus_evidence": inputs.corpus,
        "gates": gates,
        "obligations": obligations,
        "outcome": "pass" if is_complete(gates, obligations) else "blocked",
    }
