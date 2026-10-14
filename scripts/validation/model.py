"""Shared contracts for canonical repository validation."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

class ValidationFailure(RuntimeError):
    """A mandatory repository validation gate failed."""

@dataclass(frozen=True, slots=True, order=True)
class ChangedPath:
    path: Path
    status: str
    source_path: Path | None = None
    source: str = ""

@dataclass(frozen=True, slots=True)
class ValidationScope:
    changes: tuple[ChangedPath, ...] | None = None
    base_ref: str | None = None
    include_staged: bool = False
    include_unstaged: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.changes, (set, frozenset)):
            object.__setattr__(
                self, "changes",
                tuple(ChangedPath(path, "M", None, "explicit") for path in sorted(self.changes)),
            )

    @property
    def paths(self) -> frozenset[Path] | None:
        if self.changes is None:
            return None
        return frozenset(change.path for change in self.changes)

    def includes(self, path: Path) -> bool:
        return self.paths is None or path in self.paths

    def change_for(self, path: Path) -> ChangedPath | None:
        if self.changes is None:
            return None
        return next((change for change in self.changes if change.path == path), None)

@dataclass(frozen=True, slots=True)
class Gate:
    name: str
    action: Callable[[Path, ValidationScope], None]
