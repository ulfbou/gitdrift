"""Changed-path discovery for canonical validation."""
from __future__ import annotations
import subprocess
from pathlib import Path
from .model import ChangedPath, ValidationFailure, ValidationScope

_DIFF_FILTER = "ACDMRTUXB"

def _safe_path(raw: bytes) -> Path:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValidationFailure("Git reported a non-UTF-8 path") from error
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        raise ValidationFailure(f"unsafe changed path: {text!r}")
    return path

def _git(root: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, check=False,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise ValidationFailure(
            completed.stderr.decode("utf-8", "replace").strip()
            or f"git {' '.join(arguments)} failed"
        )
    return completed.stdout

def _diff_changes(root: Path, *arguments: str, source: str) -> list[ChangedPath]:
    fields = _git(
        root, "diff", "--name-status", "-z", f"--diff-filter={_DIFF_FILTER}",
        *arguments, "--",
    ).split(b"\0")
    if fields and not fields[-1]:
        fields.pop()
    changes: list[ChangedPath] = []
    index = 0
    while index < len(fields):
        status_text = fields[index].decode("ascii", "strict")
        index += 1
        code = status_text[:1]
        if code in {"R", "C"}:
            if index + 1 >= len(fields):
                raise ValidationFailure("Git reported a malformed rename/copy record")
            source_path = _safe_path(fields[index])
            path = _safe_path(fields[index + 1])
            index += 2
        else:
            if index >= len(fields):
                raise ValidationFailure("Git reported a malformed changed-path record")
            source_path = None
            path = _safe_path(fields[index])
            index += 1
        changes.append(ChangedPath(path, code, source_path, source))
    return changes

def _untracked(root: Path) -> list[ChangedPath]:
    return [
        ChangedPath(_safe_path(raw), "A", None, "untracked")
        for raw in _git(root, "ls-files", "--others", "--exclude-standard", "-z", "--").split(b"\0")
        if raw
    ]

def changed_paths(
    root: Path, *, base_ref: str | None, include_staged: bool,
    include_unstaged: bool,
) -> ValidationScope:
    scoped = base_ref is not None or include_staged or include_unstaged
    if not scoped:
        return ValidationScope()
    by_path: dict[Path, ChangedPath] = {}
    if base_ref is not None:
        for change in _diff_changes(root, f"{base_ref}...HEAD", source="base-ref"):
            by_path[change.path] = change
    if include_staged:
        for change in _diff_changes(root, "--cached", source="staged"):
            by_path[change.path] = change
    if include_unstaged:
        for change in _diff_changes(root, source="unstaged"):
            by_path[change.path] = change
        for change in _untracked(root):
            by_path[change.path] = change
    return ValidationScope(
        tuple(sorted(by_path.values(), key=lambda change: change.path.as_posix())),
        base_ref, include_staged, include_unstaged,
    )
