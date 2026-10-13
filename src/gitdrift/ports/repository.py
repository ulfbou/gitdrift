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

class RepositoryReader(Protocol):
    def capture_head(self) -> HeadEvidence:
        """Capture HEAD without mutating repository state."""
