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
    CONTRACT_QUALITY_SCHEMA,
    RESOURCE_BOUNDS_SCHEMA,
    CORPUS_SCHEMA,
    INSTALLED_OBLIGATIONS,
    INSTALLED_SCHEMA,
    REQUIRED_GATES,
    REQUIRED_OBLIGATIONS,
    SCHEMA,
    SEMANTIC_CONTRACTS_OBLIGATIONS,
    SEMANTIC_CONTRACTS_SCHEMA,
    SYNTHETIC_SCHEMA,
    CommandSpec,
    EvidenceInputs,
    ReleaseEvidenceFailure,
    PLATFORM_MATRIX_SCHEMA,
)
from release_evidence_coverage import coverage_records, is_complete
from release_evidence_documents import (
    load_evidence,
    validate_g7_composition,
    validate_platform_matrix,
    validated_pass_claims,
)
from release_evidence_process import git, run_command

CORPUS_ROOT_ENV = "GITDRIFT_DX_ARTIFACTS_CORPUS_ROOT"
PLATFORM_MATRIX_PATH_ENV = "GITDRIFT_PLATFORM_MATRIX_PATH"
CORPUS_COMMIT = "0d49b22ddecab894d39bee30ecb49bf1353d7788"
CORPUS_TREE = "d463bb9cb56ba84d8e0b1584332cfd1a1565b075"


def _command_specs(
    synthetic_path: Path,
    semantic_contracts_path: Path,
    installed_path: Path,
    corpus_path: Path,
    contract_quality_path: Path,
    resource_bounds_path: Path,
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
            "semantic-contracts",
            (
                sys.executable,
                "scripts/acceptance/semantic_contracts.py",
                "--output",
                str(semantic_contracts_path),
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
            "contract-quality",
            (
                sys.executable,
                "scripts/acceptance/contract_quality.py",
                "--output",
                str(contract_quality_path),
            ),
        ),
        CommandSpec(
            "resource-bounds",
            (
                sys.executable,
                "scripts/acceptance/resource_bounds.py",
                "--output",
                str(resource_bounds_path),
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
    source_tree: str,
    evidence_root: Path,
    corpus_root: Path,
    platform_matrix_path: Path,
) -> EvidenceInputs:
    synthetic_path = evidence_root / "synthetic.json"
    semantic_contracts_path = evidence_root / "semantic-contracts.json"
    installed_path = evidence_root / "installed.json"
    corpus_path = evidence_root / "corpus.json"
    contract_quality_path = evidence_root / "contract-quality.json"
    resource_bounds_path = evidence_root / "resource-bounds.json"
    commands = tuple(
        run_command(root, specification)
        for specification in _command_specs(
            synthetic_path,
            semantic_contracts_path,
            installed_path,
            corpus_path,
            contract_quality_path,
            resource_bounds_path,
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
        semantic_contracts=load_evidence(
            semantic_contracts_path,
            SEMANTIC_CONTRACTS_SCHEMA,
            candidate,
        ),
        installed=load_evidence(installed_path, INSTALLED_SCHEMA, candidate),
        corpus=load_evidence(corpus_path, CORPUS_SCHEMA, candidate),
        contract_quality=load_evidence(
            contract_quality_path, CONTRACT_QUALITY_SCHEMA, candidate
        ),
        resource_bounds=load_evidence(
            resource_bounds_path, RESOURCE_BOUNDS_SCHEMA, candidate
        ),
        platform_matrix=validate_platform_matrix(
            load_evidence(
                platform_matrix_path,
                PLATFORM_MATRIX_SCHEMA,
                candidate,
            ),
            candidate=candidate,
            source_tree=source_tree,
        ),
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
    platform_matrix_value = os.environ.get(
        PLATFORM_MATRIX_PATH_ENV
    )
    if not platform_matrix_value:
        raise ReleaseEvidenceFailure(
            f"{PLATFORM_MATRIX_PATH_ENV} must identify "
            "the exact-candidate platform matrix"
        )
    platform_matrix_path = Path(platform_matrix_value).resolve()
    source_tree = git(root, "rev-parse", "HEAD^{tree}")
    with tempfile.TemporaryDirectory(
        prefix="gitdrift-release-evidence-"
    ) as directory:
        inputs = _collect_inputs(
            root,
            candidate,
            source_tree,
            Path(directory),
            corpus_root,
            platform_matrix_path,
        )
    evidence_ids = tuple(item.identity for item in inputs.commands)
    covered_obligations = set(inputs.synthetic.get("obligations", ()))
    covered_obligations.update(INSTALLED_OBLIGATIONS)
    covered_obligations.update(CORPUS_OBLIGATIONS)
    semantic_claims = validated_pass_claims(
        inputs.semantic_contracts,
        "obligations",
        REQUIRED_OBLIGATIONS,
    )
    if semantic_claims != set(SEMANTIC_CONTRACTS_OBLIGATIONS):
        raise ReleaseEvidenceFailure(
            "semantic-contract evidence authority must equal GD01-009 through GD01-017"
        )
    covered_obligations.update(semantic_claims)
    for document in (inputs.contract_quality, inputs.resource_bounds):
        covered_obligations.update(
            validated_pass_claims(
                document,
                "obligations",
                REQUIRED_OBLIGATIONS,
            )
        )
    platform_obligations, platform_gates = (
        validate_g7_composition(
            inputs.platform_matrix,
            inputs.resource_bounds,
            candidate=candidate,
            source_tree=source_tree,
        )
    )
    covered_obligations.update(platform_obligations)
    obligations = coverage_records(
        REQUIRED_OBLIGATIONS,
        covered_obligations,
        evidence_ids,
        "No exact-candidate executable evidence is aggregated yet.",
    )
    covered_gates = set(AGGREGATED_GATES)
    for document in (inputs.contract_quality, inputs.resource_bounds):
        covered_gates.update(
            validated_pass_claims(document, "gates", REQUIRED_GATES)
        )
    covered_gates.update(platform_gates)
    gates = coverage_records(
        REQUIRED_GATES,
        covered_gates,
        evidence_ids,
        "The required release-wide evidence tier is not aggregated yet.",
    )
    artifacts = inputs.installed.get("artifacts")
    return {
        "schema": SCHEMA,
        "candidate_commit": candidate,
        "source_tree_identity": source_tree,
        "commands": [item.to_dict() for item in inputs.commands],
        "generated_artifacts": artifacts if isinstance(artifacts, list) else [],
        "corpus_evidence": inputs.corpus,
        "gates": gates,
        "obligations": obligations,
        "outcome": "pass" if is_complete(gates, obligations) else "blocked",
    }
