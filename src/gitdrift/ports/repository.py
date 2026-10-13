"""Domain-oriented repository acquisition ports."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True, slots=True)
class HeadEvidence:
    repository_id: str
    commit_id: str
    tree_id: str
    head_locator: str | None

@dataclass(frozen=True, slots=True, order=True)
class IndexEntry:
    path: str
    stage: int
    mode: str
    object_id: str

@dataclass(frozen=True, slots=True)
class IndexEvidence:
    repository_id: str
    object_format: str
    base_commit_id: str | None
    base_tree_id: str | None
    entries: tuple[IndexEntry, ...]
    manifest_identity: str
    limitations: tuple[str, ...] = ()

class RepositoryReader(Protocol):
    def capture_head(self) -> HeadEvidence:
        """Capture HEAD without mutating repository state."""

    def capture_index(self) -> IndexEvidence:
        """Capture a stable index manifest without mutating repository state."""
