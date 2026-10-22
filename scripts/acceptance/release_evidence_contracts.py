"""Immutable contracts for exact-candidate release evidence."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Sequence

SCHEMA = "gitdrift-release-candidate-evidence-v1"
SYNTHETIC_SCHEMA = "gitdrift-state-awareness-synthetic-acceptance-v1"
INSTALLED_SCHEMA = "gitdrift-installed-distribution-acceptance-v1"
CORPUS_SCHEMA = "gitdrift-dx-artifacts-corpus-acceptance-v1"
REQUIRED_GATES = tuple(f"G{index}" for index in range(9))
REQUIRED_OBLIGATIONS = tuple(f"GD01-{index:03d}" for index in range(1, 38))
INSTALLED_OBLIGATIONS = frozenset({"GD01-025", "GD01-026", "GD01-027"})
CORPUS_OBLIGATIONS = frozenset({"GD01-033"})
AGGREGATED_GATES = frozenset({"G0", "G1", "G2", "G3", "G4"})


class ReleaseEvidenceFailure(RuntimeError):
    """Release evidence could not be established truthfully."""


@dataclass(frozen=True, slots=True)
class CommandSpec:
    """One bounded acceptance command and its evidence identity."""

    identity: str
    arguments: tuple[str, ...]
    timeout_seconds: int = 1_200


@dataclass(frozen=True, slots=True)
class CommandEvidence:
    """Bounded command evidence without embedded process output."""

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


@dataclass(frozen=True, slots=True)
class EvidenceInputs:
    """Validated evidence produced for one exact candidate."""

    commands: tuple[CommandEvidence, ...]
    synthetic: dict[str, Any]
    installed: dict[str, Any]
    corpus: dict[str, Any]


def evidence_record(
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
