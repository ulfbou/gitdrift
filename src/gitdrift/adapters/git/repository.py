"""Read-only Git repository adapter."""
from __future__ import annotations

import hashlib
import os
import stat
import subprocess
from pathlib import Path

from gitdrift.domain import stable_id
from gitdrift.ports import (
    HeadEvidence,
    IgnoredPolicy,
    IndexEntry,
    IndexEvidence,
    UntrackedPolicy,
    WorkingTreeEntry,
    WorkingTreeEntryKind,
    WorkingTreeEvidence,
)

class GitRepositoryError(RuntimeError):
    """Git repository evidence could not be acquired safely."""

class IndexChangedError(GitRepositoryError):
    """The index changed while it was being captured."""

class WorkingTreeChangedError(GitRepositoryError):
    """The working tree or its capture base changed during capture."""

class GitRepositoryReader:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _git_bytes(
        self,
        *arguments: str,
        allowed: tuple[int, ...] = (0,),
    ) -> bytes:
        completed = subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", *arguments],
            cwd=self._root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode not in allowed:
            detail = completed.stderr.decode(
                "utf-8",
                errors="replace",
            ).strip()
            raise GitRepositoryError(detail or "Git command failed")
        return completed.stdout

    def _git(
        self,
        *arguments: str,
        allowed: tuple[int, ...] = (0,),
    ) -> str:
        try:
            return self._git_bytes(
                *arguments,
                allowed=allowed,
            ).decode("utf-8").strip()
        except UnicodeDecodeError as error:
            raise GitRepositoryError(
                "Git metadata is not valid UTF-8"
            ) from error

    def _repository_context(self) -> tuple[str, str]:
        repository_root = Path(
            self._git("rev-parse", "--show-toplevel")
        ).resolve()
        if repository_root != self._root:
            raise GitRepositoryError(
                "repository root does not match the explicit request"
            )
        object_format = self._git(
            "rev-parse",
            "--show-object-format",
        )
        return (
            f"git:{object_format}:{repository_root.as_posix()}",
            object_format,
        )

    def _index_path(self) -> Path:
        index_path = Path(
            self._git("rev-parse", "--git-path", "index")
        )
        if not index_path.is_absolute():
            index_path = self._root / index_path
        return index_path

    def _index_marker(self) -> str:
        try:
            payload = self._index_path().read_bytes()
        except FileNotFoundError:
            return "missing"
        except OSError as error:
            raise GitRepositoryError(
                f"cannot read Git index: {error}"
            ) from error
        return (
            f"sha256:{hashlib.sha256(payload).hexdigest()};"
            f"bytes:{len(payload)}"
        )

    def _head_or_none(self, suffix: str) -> str | None:
        value = self._git(
            "rev-parse",
            "--verify",
            f"HEAD^{{{suffix}}}",
            allowed=(0, 128),
        )
        return value or None

    def _head_marker(self) -> tuple[str | None, str | None]:
        return (
            self._head_or_none("commit"),
            self._head_or_none("tree"),
        )

    @staticmethod
    def _safe_path(raw: bytes) -> str:
        try:
            path = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise GitRepositoryError(
                "Git reported a non-UTF-8 path"
            ) from error
        portable = path.replace(chr(92), "/")
        if (
            not portable
            or portable.startswith("/")
            or ".." in portable.split("/")
        ):
            raise GitRepositoryError(
                f"unsafe workspace path: {path!r}"
            )
        return portable

    def _index_entries(self) -> tuple[IndexEntry, ...]:
        raw = self._git_bytes("ls-files", "--stage", "-z")
        entries: list[IndexEntry] = []
        for record in raw.split(b"\0"):
            if not record:
                continue
            try:
                metadata, path_bytes = record.split(b"\t", 1)
                mode_bytes, object_bytes, stage_bytes = (
                    metadata.split(b" ", 2)
                )
                path = self._safe_path(path_bytes)
                mode = mode_bytes.decode("ascii")
                object_id = object_bytes.decode("ascii")
                stage = int(stage_bytes.decode("ascii"))
            except (ValueError, UnicodeDecodeError) as error:
                raise GitRepositoryError(
                    "unsupported index entry encoding or shape"
                ) from error
            entries.append(
                IndexEntry(path, stage, mode, object_id)
            )
        return tuple(sorted(entries))

    def _status_marker(self) -> bytes:
        return self._git_bytes(
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--ignored=no",
        )

    def capture_head(self) -> HeadEvidence:
        repository_id, _ = self._repository_context()
        commit = self._head_or_none("commit")
        tree = self._head_or_none("tree")
        if commit is None or tree is None:
            raise GitRepositoryError(
                "HEAD does not identify a commit and tree"
            )
        locator = (
            self._git(
                "symbolic-ref",
                "-q",
                "HEAD",
                allowed=(0, 1),
            )
            or None
        )
        return HeadEvidence(
            repository_id,
            commit,
            tree,
            locator,
        )

    def capture_index(self) -> IndexEvidence:
        repository_id, object_format = (
            self._repository_context()
        )
        index_before = self._index_marker()
        head_before = self._head_marker()
        ordered = self._index_entries()
        head_after = self._head_marker()
        index_after = self._index_marker()

        if index_before != index_after:
            raise IndexChangedError(
                "Git index changed during capture"
            )
        if head_before != head_after:
            raise IndexChangedError(
                "HEAD changed during index capture"
            )

        base_commit, base_tree = head_before
        manifest_identity = stable_id(
            "index-manifest",
            {
                "repository_id": repository_id,
                "object_format": object_format,
                "base_commit_id": base_commit,
                "base_tree_id": base_tree,
                "entries": ordered,
            },
        )
        limitations = (
            (
                "HEAD is unborn or unavailable; "
                "index has no committed base.",
            )
            if base_commit is None
            else ()
        )
        return IndexEvidence(
            repository_id,
            object_format,
            base_commit,
            base_tree,
            ordered,
            manifest_identity,
            limitations,
        )

    def _visible_untracked(self) -> tuple[str, ...]:
        raw = self._git_bytes(
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
        )
        return tuple(
            sorted(
                self._safe_path(item)
                for item in raw.split(b"\0")
                if item
            )
        )

    def _ignored(self) -> frozenset[str]:
        raw = self._git_bytes(
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "-z",
            "--",
        )
        return frozenset(
            self._safe_path(item)
            for item in raw.split(b"\0")
            if item
        )

    def _selected_paths(
        self,
        *,
        index_entries: tuple[IndexEntry, ...],
        untracked_policy: UntrackedPolicy,
        ignored_policy: IgnoredPolicy,
        selected_paths: tuple[str, ...],
    ) -> tuple[str, ...]:
        selected = {
            self._safe_path(path.encode("utf-8"))
            for path in selected_paths
        }
        tracked = {
            entry.path
            for entry in index_entries
            if entry.stage == 0
        }
        visible_untracked = set(self._visible_untracked())
        ignored = set(self._ignored())

        paths = set(tracked)

        if untracked_policy is UntrackedPolicy.INCLUDE_ALL_VISIBLE:
            paths.update(visible_untracked)
        elif untracked_policy is UntrackedPolicy.INCLUDE_SELECTED:
            paths.update(selected & visible_untracked)

        if ignored_policy is IgnoredPolicy.INCLUDE_SELECTED:
            paths.update(selected & ignored)

        missing_selected = selected - paths
        if missing_selected:
            raise GitRepositoryError(
                "selected paths are unavailable under the active "
                "untracked and ignored policies: "
                + ", ".join(sorted(missing_selected))
            )

        return tuple(sorted(paths))

    def _capture_entry(
        self,
        path: str,
        index_entry: IndexEntry | None,
    ) -> WorkingTreeEntry:
        absolute = self._root / path
        index_mode = (
            index_entry.mode if index_entry is not None else None
        )
        index_object_id = (
            index_entry.object_id
            if index_entry is not None
            else None
        )

        try:
            metadata = absolute.lstat()
        except FileNotFoundError:
            if index_entry is None:
                raise WorkingTreeChangedError(
                    f"selected path disappeared during capture: {path}"
                )
            return WorkingTreeEntry(
                path=path,
                kind=WorkingTreeEntryKind.DELETED,
                mode=None,
                content_identity=None,
                size=None,
                index_mode=index_mode,
                index_object_id=index_object_id,
            )
        except OSError as error:
            return WorkingTreeEntry(
                path=path,
                kind=WorkingTreeEntryKind.UNREADABLE,
                mode=None,
                content_identity=None,
                size=None,
                index_mode=index_mode,
                index_object_id=index_object_id,
                limitations=(str(error),),
            )

        if stat.S_ISLNK(metadata.st_mode):
            try:
                target = os.readlink(absolute)
            except OSError as error:
                return WorkingTreeEntry(
                    path=path,
                    kind=WorkingTreeEntryKind.UNREADABLE,
                    mode="120000",
                    content_identity=None,
                    size=None,
                    index_mode=index_mode,
                    index_object_id=index_object_id,
                    limitations=(str(error),),
                )
            payload = os.fsencode(target)
            return WorkingTreeEntry(
                path=path,
                kind=WorkingTreeEntryKind.SYMLINK,
                mode="120000",
                content_identity=(
                    "sha256:"
                    + hashlib.sha256(payload).hexdigest()
                ),
                size=len(payload),
                index_mode=index_mode,
                index_object_id=index_object_id,
                symlink_target=target,
            )

        if (
            index_entry is not None
            and index_entry.mode == "160000"
        ):
            status = self._git(
                "status",
                "--porcelain=v1",
                "--ignore-submodules=none",
                "--",
                path,
            )
            return WorkingTreeEntry(
                path=path,
                kind=WorkingTreeEntryKind.GITLINK,
                mode="160000",
                content_identity=(
                    f"gitlink:{index_entry.object_id};"
                    f"status:{status}"
                ),
                size=None,
                index_mode=index_mode,
                index_object_id=index_object_id,
                limitations=(
                    "nested repository was not traversed",
                ),
            )

        if not stat.S_ISREG(metadata.st_mode):
            return WorkingTreeEntry(
                path=path,
                kind=WorkingTreeEntryKind.UNSUPPORTED,
                mode=None,
                content_identity=None,
                size=None,
                index_mode=index_mode,
                index_object_id=index_object_id,
                limitations=(
                    "unsupported working-tree file kind",
                ),
            )

        try:
            payload = absolute.read_bytes()
        except OSError as error:
            return WorkingTreeEntry(
                path=path,
                kind=WorkingTreeEntryKind.UNREADABLE,
                mode=None,
                content_identity=None,
                size=None,
                index_mode=index_mode,
                index_object_id=index_object_id,
                limitations=(str(error),),
            )

        mode = (
            "100755"
            if metadata.st_mode & stat.S_IXUSR
            else "100644"
        )
        return WorkingTreeEntry(
            path=path,
            kind=WorkingTreeEntryKind.REGULAR,
            mode=mode,
            content_identity=(
                "sha256:"
                + hashlib.sha256(payload).hexdigest()
            ),
            size=len(payload),
            index_mode=index_mode,
            index_object_id=index_object_id,
        )

    def capture_working_tree(
        self,
        *,
        untracked_policy: UntrackedPolicy = (
            UntrackedPolicy.EXCLUDE
        ),
        ignored_policy: IgnoredPolicy = (
            IgnoredPolicy.EXCLUDE
        ),
        selected_paths: tuple[str, ...] = (),
    ) -> WorkingTreeEvidence:
        repository_id, object_format = (
            self._repository_context()
        )

        index_before = self.capture_index()
        head_before = self._head_marker()
        status_before = self._status_marker()

        normal_index = {
            entry.path: entry
            for entry in index_before.entries
            if entry.stage == 0
        }
        unmerged = tuple(
            entry.path
            for entry in index_before.entries
            if entry.stage != 0
        )
        if unmerged:
            raise GitRepositoryError(
                "working-tree capture does not collapse "
                "unmerged index entries: "
                + ", ".join(sorted(set(unmerged)))
            )

        paths = self._selected_paths(
            index_entries=index_before.entries,
            untracked_policy=untracked_policy,
            ignored_policy=ignored_policy,
            selected_paths=selected_paths,
        )

        entries = tuple(
            self._capture_entry(
                path,
                normal_index.get(path),
            )
            for path in paths
        )

        status_after = self._status_marker()
        head_after = self._head_marker()
        index_after = self.capture_index()

        if index_before != index_after:
            raise WorkingTreeChangedError(
                "Git index changed during working-tree capture"
            )
        if head_before != head_after:
            raise WorkingTreeChangedError(
                "HEAD changed during working-tree capture"
            )
        if status_before != status_after:
            raise WorkingTreeChangedError(
                "working-tree selection changed during capture"
            )

        verification_entries = tuple(
            self._capture_entry(
                path,
                normal_index.get(path),
            )
            for path in paths
        )
        if entries != verification_entries:
            raise WorkingTreeChangedError(
                "selected working-tree content changed during capture"
            )

        manifest_identity = stable_id(
            "working-tree-manifest",
            {
                "repository_id": repository_id,
                "object_format": object_format,
                "base_commit_id": index_before.base_commit_id,
                "base_tree_id": index_before.base_tree_id,
                "index_manifest_identity": (
                    index_before.manifest_identity
                ),
                "untracked_policy": untracked_policy,
                "ignored_policy": ignored_policy,
                "selected_paths": tuple(
                    sorted(selected_paths)
                ),
                "entries": entries,
            },
        )

        return WorkingTreeEvidence(
            repository_id=repository_id,
            object_format=object_format,
            base_commit_id=index_before.base_commit_id,
            base_tree_id=index_before.base_tree_id,
            index_manifest_identity=(
                index_before.manifest_identity
            ),
            untracked_policy=untracked_policy,
            ignored_policy=ignored_policy,
            selected_paths=tuple(sorted(selected_paths)),
            entries=entries,
            manifest_identity=manifest_identity,
        )
