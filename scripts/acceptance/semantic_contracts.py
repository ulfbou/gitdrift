#!/usr/bin/env python3
"""Produce exact-candidate evidence for semantic contracts GD01-009--017."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

from release_evidence_contracts import (
    SEMANTIC_CONTRACTS_OBLIGATIONS,
    SEMANTIC_CONTRACTS_SCHEMA,
)

OBLIGATION_TEST_CASES = {
    "GD01-009": (
        "tests.test_identity.IdentityTests.test_mutable_locator_does_not_control_state_identity",
        "tests.test_domain_records.DomainRecordTests.test_path_is_location_and_must_be_workspace_relative",
    ),
    "GD01-010": (
        "tests.test_markdown_extractor.MarkdownExtractorTests.test_capability_is_versioned_and_explicit",
        "tests.test_markdown_extractor.MarkdownExtractorTests.test_extracts_atx_and_setext_sections_in_order",
        "tests.test_markdown_extractor.MarkdownExtractorTests.test_invalid_utf8_preserves_exact_evidence",
        "tests.test_markdown_extractor.MarkdownExtractorTests.test_repeated_execution_is_deterministic",
    ),
    "GD01-011": (
        "tests.test_python_extractor.PythonSymbolExtractorTests.test_capability_is_versioned_and_explicit",
        "tests.test_python_extractor.PythonSymbolExtractorTests.test_extracts_nested_sync_and_async_symbols",
        "tests.test_python_extractor.PythonSymbolExtractorTests.test_malformed_python_is_not_false_absence",
        "tests.test_python_extractor.PythonSymbolExtractorTests.test_repeated_execution_is_deterministic",
    ),
    "GD01-012": (
        "tests.test_markdown_extractor.MarkdownExtractorTests.test_facts_retain_exact_input_evidence",
        "tests.test_markdown_extractor.MarkdownExtractorTests.test_unsupported_kind_is_not_semantic_absence",
        "tests.test_python_extractor.PythonSymbolExtractorTests.test_facts_retain_exact_input_evidence",
        "tests.test_python_extractor.PythonSymbolExtractorTests.test_unsupported_kind_is_not_false_absence",
        "tests.test_raw_change_evidence.RawChangeEvidenceTests.test_exact_evidence_is_retained_immutably",
    ),
    "GD01-013": (
        "tests.test_markdown_extractor.MarkdownExtractorTests.test_facts_retain_exact_input_evidence",
        "tests.test_python_extractor.PythonSymbolExtractorTests.test_facts_retain_exact_input_evidence",
        "tests.test_domain_records.DomainRecordTests.test_observed_and_derived_evidence_remain_distinct",
    ),
    "GD01-014": (
        "tests.test_obligation_evaluation.ObligationEvaluationTests.test_loader_retains_explicit_authority_scope_and_provenance",
        "tests.test_obligation_evaluation.ObligationEvaluationTests.test_exists_is_satisfied_only_by_matching_explicit_fact",
        "tests.test_obligation_evaluation.ObligationEvaluationTests.test_missing_authority_remains_unresolved",
    ),
    "GD01-015": (
        "tests.test_obligation_evaluation.ObligationEvaluationTests.test_change_or_similarity_cannot_create_regression",
        "tests.test_raw_change_evidence.RawChangeEvidenceTests.test_rename_candidate_retains_method_and_score",
        "tests.test_raw_change_evidence.RawChangeEvidenceTests.test_non_candidate_rejects_similarity_evidence",
    ),
    "GD01-016": (
        "tests.test_obligation_evaluation.ObligationEvaluationTests.test_missing_authority_remains_unresolved",
        "tests.test_obligation_evaluation.ObligationEvaluationTests.test_incomplete_search_cannot_prove_absence",
        "tests.test_obligation_evaluation.ObligationEvaluationTests.test_change_or_similarity_cannot_create_regression",
        "tests.test_case_construction.CaseConstructionTests.test_unknowns_prevent_final_judgment",
    ),
    "GD01-017": (
        "tests.test_case_construction.CaseConstructionTests.test_constructs_every_required_case_dimension",
        "tests.test_case_construction.CaseConstructionTests.test_inventory_must_close_evidence_references",
        "tests.test_case_construction.CaseConstructionTests.test_support_and_counterevidence_roles_cannot_collapse",
        "tests.test_case_construction.CaseConstructionTests.test_unknowns_prevent_final_judgment",
        "tests.test_case_construction.CaseConstructionTests.test_repeated_construction_is_deterministic",
    ),
}
GATE_CLAIMS = {"G3": "pass", "G4": "pass", "G5": "pass", "G6": "partial"}
LIMITATIONS = (
    "GD01-034 platform evidence is outside this boundary.",
    "G7 platform and resource composition is outside this boundary.",
    "G8 final release review is outside this boundary.",
)
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_GIT_ID = re.compile(r"[0-9a-f]{40}\Z")

class AcceptanceFailure(RuntimeError):
    """Semantic-contract evidence could not be established truthfully."""

def _ordered_test_cases() -> tuple[str, ...]:
    seen: set[str] = set(); result: list[str] = []
    for obligation in sorted(OBLIGATION_TEST_CASES):
        for identity in OBLIGATION_TEST_CASES[obligation]:
            if identity not in seen:
                seen.add(identity); result.append(identity)
    return tuple(result)

TEST_CASES = _ordered_test_cases()

def canonical_command() -> tuple[str, ...]:
    return (sys.executable, "-m", "unittest", "-v", *TEST_CASES)

def _claims(values: dict[str, str]) -> dict[str, dict[str, str]]:
    return {key: {"outcome": value} for key, value in sorted(values.items())}

def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(["git", *arguments], cwd=root, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
        errors="strict", timeout=30, check=False)
    if completed.returncode:
        raise AcceptanceFailure(completed.stderr.strip() or f"git {' '.join(arguments)} failed")
    return completed.stdout.strip()

def _run_tests(root: Path) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    source = str(root / "src")
    environment["PYTHONPATH"] = source + (os.pathsep + environment["PYTHONPATH"] if environment.get("PYTHONPATH") else "")
    try:
        return subprocess.run(canonical_command(), cwd=root, env=environment,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=1_200, check=False)
    except subprocess.TimeoutExpired as error:
        raise AcceptanceFailure("semantic-contract tests timed out") from error

def validate_document(document: dict[str, Any], *, expected_candidate: str | None = None,
                      expected_tree: str | None = None) -> None:
    fields = {"schema", "candidate_commit", "source_tree_identity", "test_cases", "command",
        "command_exit_code", "stdout_sha256", "stderr_sha256", "mutation_sentinel",
        "coverage", "obligations", "gates", "limitations", "outcome"}
    if set(document) != fields:
        raise AcceptanceFailure("semantic-contract evidence fields do not match the schema")
    if document["schema"] != SEMANTIC_CONTRACTS_SCHEMA or document["outcome"] != "pass":
        raise AcceptanceFailure("semantic-contract evidence root is invalid")
    candidate = document["candidate_commit"]; tree = document["source_tree_identity"]
    if not isinstance(candidate, str) or not _GIT_ID.fullmatch(candidate):
        raise AcceptanceFailure("semantic-contract candidate identity is invalid")
    if not isinstance(tree, str) or not _GIT_ID.fullmatch(tree):
        raise AcceptanceFailure("semantic-contract tree identity is invalid")
    if expected_candidate is not None and candidate != expected_candidate:
        raise AcceptanceFailure("semantic-contract candidate identity does not match")
    if expected_tree is not None and tree != expected_tree:
        raise AcceptanceFailure("semantic-contract tree identity does not match")
    if document["test_cases"] != list(TEST_CASES) or document["command"] != list(canonical_command()):
        raise AcceptanceFailure("semantic-contract command identity is invalid")
    if type(document["command_exit_code"]) is not int or document["command_exit_code"] != 0:
        raise AcceptanceFailure("semantic-contract evidence records failed tests")
    for field in ("stdout_sha256", "stderr_sha256"):
        if not isinstance(document[field], str) or not _SHA256.fullmatch(document[field]):
            raise AcceptanceFailure(f"semantic-contract {field} is invalid")
    sentinel = document["mutation_sentinel"]
    sentinel_fields = {"head_before", "head_after", "tree_before", "tree_after",
        "status_before_sha256", "status_after_sha256", "head_unchanged", "tree_unchanged", "status_unchanged"}
    if not isinstance(sentinel, dict) or set(sentinel) != sentinel_fields:
        raise AcceptanceFailure("semantic-contract mutation sentinel is invalid")
    if sentinel["head_before"] != candidate or sentinel["head_after"] != candidate:
        raise AcceptanceFailure("semantic-contract HEAD mutation sentinel is invalid")
    if sentinel["tree_before"] != tree or sentinel["tree_after"] != tree:
        raise AcceptanceFailure("semantic-contract tree mutation sentinel is invalid")
    if sentinel["status_before_sha256"] != sentinel["status_after_sha256"]:
        raise AcceptanceFailure("semantic-contract status mutation sentinel is invalid")
    if any(not sentinel[field] for field in ("head_unchanged", "tree_unchanged", "status_unchanged")):
        raise AcceptanceFailure("semantic-contract mutation sentinel did not pass")
    coverage = document["coverage"]
    if not isinstance(coverage, dict) or set(coverage) != set(OBLIGATION_TEST_CASES):
        raise AcceptanceFailure("semantic-contract coverage identities are invalid")
    for identity, test_cases in OBLIGATION_TEST_CASES.items():
        expected = {"outcome": "pass", "test_cases": list(test_cases)}
        if coverage[identity] != expected:
            raise AcceptanceFailure(f"semantic-contract coverage is invalid for {identity}")
    expected_obligations = _claims({identity: "pass" for identity in OBLIGATION_TEST_CASES})
    if document["obligations"] != expected_obligations:
        raise AcceptanceFailure("semantic-contract obligation claims are invalid")
    if document["gates"] != _claims(GATE_CLAIMS):
        raise AcceptanceFailure("semantic-contract gate claims are invalid")
    if document["limitations"] != list(LIMITATIONS):
        raise AcceptanceFailure("semantic-contract limitations are invalid")

def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    candidate = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    status_before = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status_before:
        raise AcceptanceFailure("semantic-contract acceptance requires a clean committed candidate")
    completed = _run_tests(root)
    head_after = _git(root, "rev-parse", "HEAD")
    tree_after = _git(root, "rev-parse", "HEAD^{tree}")
    status_after = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if completed.returncode:
        raise AcceptanceFailure("semantic-contract focused tests failed")
    if (head_after, tree_after, status_after) != (candidate, tree, status_before):
        raise AcceptanceFailure("semantic-contract focused tests changed the repository candidate")
    result = {
        "schema": SEMANTIC_CONTRACTS_SCHEMA, "candidate_commit": candidate,
        "source_tree_identity": tree, "test_cases": list(TEST_CASES),
        "command": list(canonical_command()), "command_exit_code": completed.returncode,
        "stdout_sha256": _sha256(completed.stdout), "stderr_sha256": _sha256(completed.stderr),
        "mutation_sentinel": {"head_before": candidate, "head_after": head_after,
            "tree_before": tree, "tree_after": tree_after,
            "status_before_sha256": _sha256(status_before.encode("utf-8")),
            "status_after_sha256": _sha256(status_after.encode("utf-8")),
            "head_unchanged": True, "tree_unchanged": True, "status_unchanged": True},
        "coverage": {identity: {"outcome": "pass", "test_cases": list(test_cases)}
            for identity, test_cases in sorted(OBLIGATION_TEST_CASES.items())},
        "obligations": _claims({identity: "pass" for identity in OBLIGATION_TEST_CASES}),
        "gates": _claims(GATE_CLAIMS), "limitations": list(LIMITATIONS), "outcome": "pass",
    }
    validate_document(result, expected_candidate=candidate, expected_tree=tree)
    return result

def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    return parser

def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        result = run(arguments.root)
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                    encoding="utf-8", newline="\n")
        return 0
    except AcceptanceFailure as error:
        print(str(error), file=sys.stderr); return 1

if __name__ == "__main__":
    raise SystemExit(main())
