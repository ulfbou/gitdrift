#!/usr/bin/env python3
"""Produce exact-candidate acceptance evidence for the pinned dx-artifacts corpus."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

from jsonschema import Draft202012Validator
from gitdrift.adapters.serialization import load_native_schema
from gitdrift.profiles import StateAwarenessProfile, StateAwarenessRequest

SCHEMA = "gitdrift-dx-artifacts-corpus-acceptance-v1"
OBLIGATIONS = ("GD01-033",)
GATES = ("G4",)


class AcceptanceFailure(RuntimeError):
    """The external-corpus acceptance boundary could not pass truthfully."""


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


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _snapshot(root: Path) -> dict[str, str]:
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    if status.returncode:
        raise AcceptanceFailure("repository status capture failed")
    return {
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "status_sha256": _sha256(status.stdout),
        "config_sha256": _sha256(
            _git(root, "config", "--local", "--list", "--null").encode("utf-8")
        ),
        "refs_sha256": _sha256(
            _git(root, "show-ref").encode("utf-8")
        ),
    }


def _verify_corpus(root: Path, commit: str, tree: str) -> dict[str, str]:
    root = root.resolve()
    if not root.is_dir():
        raise AcceptanceFailure("corpus root does not exist")
    actual_commit = _git(root, "rev-parse", "HEAD")
    actual_tree = _git(root, "rev-parse", "HEAD^{tree}")
    branch = _git(root, "branch", "--show-current")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if actual_commit != commit:
        raise AcceptanceFailure("corpus commit does not match the pinned identity")
    if actual_tree != tree:
        raise AcceptanceFailure("corpus tree does not match the pinned identity")
    if branch:
        raise AcceptanceFailure("corpus checkout must be detached")
    if status:
        raise AcceptanceFailure("corpus checkout must be clean")
    origin = _git(root, "remote", "get-url", "origin")
    return {
        "repository": origin,
        "commit": actual_commit,
        "tree": actual_tree,
    }


def _run_profile(corpus_root: Path) -> tuple[dict[str, Any], bytes]:
    result = StateAwarenessProfile().run(
        StateAwarenessRequest(corpus_root, include_upstream=False)
    )
    payload = result.artifact.payload
    payload_bytes = payload if isinstance(payload, bytes) else payload.encode("utf-8")
    try:
        document = json.loads(payload_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AcceptanceFailure("state-awareness output is not valid JSON") from error
    Draft202012Validator(load_native_schema()).validate(document)
    return document, payload_bytes


def run(
    gitdrift_root: Path,
    corpus_root: Path,
    corpus_commit: str,
    corpus_tree: str,
) -> dict[str, Any]:
    gitdrift_root = gitdrift_root.resolve()
    corpus_root = corpus_root.resolve()
    candidate_commit = _git(gitdrift_root, "rev-parse", "HEAD")
    source_tree = _git(gitdrift_root, "rev-parse", "HEAD^{tree}")
    if _git(gitdrift_root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise AcceptanceFailure("corpus acceptance requires a clean Gitdrift candidate")
    corpus_identity = _verify_corpus(corpus_root, corpus_commit, corpus_tree)
    gitdrift_before = _snapshot(gitdrift_root)
    corpus_before = _snapshot(corpus_root)
    first_document, first_payload = _run_profile(corpus_root)
    second_document, second_payload = _run_profile(corpus_root)
    gitdrift_after = _snapshot(gitdrift_root)
    corpus_after = _snapshot(corpus_root)
    if first_document != second_document or first_payload != second_payload:
        raise AcceptanceFailure("repeated corpus executions are not deterministic")
    if gitdrift_before != gitdrift_after:
        raise AcceptanceFailure("Gitdrift candidate changed during corpus acceptance")
    if corpus_before != corpus_after:
        raise AcceptanceFailure("corpus changed during acceptance")
    request = {
        "include_upstream": False,
        "corpus_commit": corpus_commit,
        "corpus_tree": corpus_tree,
    }
    return {
        "schema": SCHEMA,
        "candidate_commit": candidate_commit,
        "source_tree_identity": source_tree,
        "corpus": corpus_identity,
        "request_sha256": _sha256(
            json.dumps(request, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ),
        "native_output_sha256": _sha256(first_payload),
        "native_schema": first_document.get("schema"),
        "mutation_sentinel": {
            "gitdrift": gitdrift_after,
            "corpus": corpus_after,
            "outcome": "pass",
        },
        "obligations": list(OBLIGATIONS),
        "gates": list(GATES),
        "limitations": ["configured upstream was explicitly not requested"],
        "outcome": "pass",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--corpus-root", type=Path, required=True)
    parser.add_argument("--corpus-commit", required=True)
    parser.add_argument("--corpus-tree", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        document = run(
            arguments.root,
            arguments.corpus_root,
            arguments.corpus_commit,
            arguments.corpus_tree,
        )
        payload = json.dumps(
            document,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n"
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
