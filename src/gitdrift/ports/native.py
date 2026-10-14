"""Domain-owned native investigation and output-sink contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from gitdrift.domain import Investigation


NATIVE_SCHEMA_ID = "https://gitdrift.dev/schemas/investigation/v1"
NATIVE_SCHEMA_VERSION = "1.0.0"


class NativeContractError(ValueError):
    """Native data cannot be represented under the accepted contract."""


class NativeValidationError(NativeContractError):
    """Native investigation data does not conform to its schema."""


class OutputSinkError(RuntimeError):
    """A sink failed before accepting one complete artifact."""


@dataclass(frozen=True, slots=True)
class NativeArtifact:
    """One validated canonical native investigation artifact."""

    schema_id: str
    schema_version: str
    investigation_id: str
    payload: bytes


class NativeInvestigationSerializer(Protocol):
    """Validate and serialize one complete native investigation."""

    def serialize(self, investigation: Investigation) -> NativeArtifact:
        """Return complete deterministic schema-valid UTF-8 JSON bytes."""


class ByteSink(Protocol):
    """Accept one complete artifact or report failure."""

    def write_complete(self, payload: bytes) -> None:
        """Accept all bytes atomically at the sink contract boundary."""
