"""Bounded subprocess acquisition for release evidence."""
from __future__ import annotations

import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import BinaryIO

from release_evidence_contracts import (
    CommandEvidence,
    CommandSpec,
    ReleaseEvidenceFailure,
)


def _sha256(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    stream.seek(0)
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def git(root: Path, *arguments: str) -> str:
    try:
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
    except subprocess.TimeoutExpired as error:
        raise ReleaseEvidenceFailure(
            f"git {' '.join(arguments)} timed out"
        ) from error
    if completed.returncode:
        raise ReleaseEvidenceFailure(
            completed.stderr.strip() or f"git {' '.join(arguments)} failed"
        )
    return completed.stdout.strip()


def run_command(root: Path, specification: CommandSpec) -> CommandEvidence:
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            completed = subprocess.run(
                list(specification.arguments),
                cwd=root,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                timeout=specification.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise ReleaseEvidenceFailure(
                f"acceptance command timed out: {specification.identity}"
            ) from error
        return CommandEvidence(
            identity=specification.identity,
            command=specification.arguments,
            exit_code=completed.returncode,
            stdout_sha256=_sha256(stdout),
            stderr_sha256=_sha256(stderr),
        )
