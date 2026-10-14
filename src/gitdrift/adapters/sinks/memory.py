"""In-memory complete-byte sink."""

from __future__ import annotations

from gitdrift.ports.native import OutputSinkError


class MemoryByteSink:
    """Replace retained bytes only after validating the full payload."""

    def __init__(self, *, fail: bool = False) -> None:
        self._payload: bytes | None = None
        self._fail = fail

    @property
    def payload(self) -> bytes | None:
        return self._payload

    def write_complete(self, payload: bytes) -> None:
        if not isinstance(payload, bytes):
            raise OutputSinkError("sink payload must be complete bytes")
        if self._fail:
            raise OutputSinkError("configured sink failure")
        replacement = bytes(payload)
        self._payload = replacement
