"""Application boundary for validated native artifact delivery."""

from __future__ import annotations

from dataclasses import dataclass

from gitdrift.domain import Investigation
from gitdrift.ports.native import (
    ByteSink,
    NativeArtifact,
    NativeInvestigationSerializer,
)


@dataclass(frozen=True, slots=True)
class NativeDeliveryResult:
    """The exact validated artifact accepted by the selected sink."""

    artifact: NativeArtifact


def serialize_and_deliver(
    investigation: Investigation,
    serializer: NativeInvestigationSerializer,
    sink: ByteSink,
) -> NativeDeliveryResult:
    """Serialize first, then offer one complete immutable payload."""

    artifact = serializer.serialize(investigation)
    sink.write_complete(artifact.payload)
    return NativeDeliveryResult(artifact)
