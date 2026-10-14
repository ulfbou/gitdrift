"""Domain-oriented repository acquisition ports."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

class UntrackedPolicy(StrEnum):
    """Selection policy for visible untracked files."""

    EXCLUDE = "exclude"
    INCLUDE_SELECTED = "include-selected"
    INCLUDE_ALL_VISIBLE = "include-all-visible"

class IgnoredPolicy(StrEnum):
    """Selection policy for ignored files."""

    EXCLUDE = "exclude"
    INCLUDE_SELECTED = "include-selected"

class WorkingTreeEntryKind(StrEnum):
    """Observed working-tree entry kind."""

    REGULAR = "regular"
    SYMLINK = "symlink"
    DELETED = "deleted"
    GITLINK = "gitlink"
    UNREADABLE = "unreadable"
    UNSUPPORTED = "unsupported"

@dataclass(frozen=True, slots=True)
class HeadEvidence:
    repository_id: str
    commit_id: str
    tree_id: str
    head_locator: str | None


@dataclass(frozen=True, slots=True)
class UpstreamEvidence:
    repository_id: str
    locator: str
    commit_id: str
    tree_id: str


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

@dataclass(frozen=True, slots=True, order=True)
class WorkingTreeEntry:
    """One exact or explicitly unavailable working-tree observation."""

    path: str
    kind: WorkingTreeEntryKind
    mode: str | None
    content_identity: str | None
    size: int | None
    index_mode: str | None = None
    index_object_id: str | None = None
    symlink_target: str | None = None
    limitations: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class WorkingTreeEvidence:
    """A reproducible working-tree capture bound to an index manifest."""

    repository_id: str
    object_format: str
    base_commit_id: str | None
    base_tree_id: str | None
    index_manifest_identity: str
    untracked_policy: UntrackedPolicy
    ignored_policy: IgnoredPolicy
    selected_paths: tuple[str, ...]
    entries: tuple[WorkingTreeEntry, ...]
    manifest_identity: str
    limitations: tuple[str, ...] = ()

class RepositoryReader(Protocol):
    def capture_head(self) -> HeadEvidence:
        """Capture HEAD without mutating repository state."""

    def capture_upstream(
        self,
    ) -> UpstreamEvidence | None:
        """Capture configured upstream without fetch or integration."""

    def capture_index(self) -> IndexEvidence:
        """Capture a stable index manifest without mutating repository state."""

    def capture_working_tree(
        self,
        *,
        untracked_policy: UntrackedPolicy = UntrackedPolicy.EXCLUDE,
        ignored_policy: IgnoredPolicy = IgnoredPolicy.EXCLUDE,
        selected_paths: tuple[str, ...] = (),
    ) -> WorkingTreeEvidence:
        """Capture a stable working-tree manifest without repository mutation."""
