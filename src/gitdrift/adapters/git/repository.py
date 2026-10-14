"""Read-only Git repository adapter."""
from __future__ import annotations
import hashlib
import subprocess
from pathlib import Path
from gitdrift.domain import stable_id
from gitdrift.ports import HeadEvidence, IndexEntry, IndexEvidence

class GitRepositoryError(RuntimeError):
    """Git repository evidence could not be acquired safely."""

class IndexChangedError(GitRepositoryError):
    """The index changed while it was being captured."""

class GitRepositoryReader:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _git_bytes(self, *arguments: str, allowed: tuple[int, ...] = (0,)) -> bytes:
        completed = subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", *arguments],
            cwd=self._root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode not in allowed:
            detail = completed.stderr.decode("utf-8", errors="replace").strip()
            raise GitRepositoryError(detail or "Git command failed")
        return completed.stdout

    def _git(self, *arguments: str, allowed: tuple[int, ...] = (0,)) -> str:
        try:
            return self._git_bytes(*arguments, allowed=allowed).decode("utf-8").strip()
        except UnicodeDecodeError as error:
            raise GitRepositoryError("Git metadata is not valid UTF-8") from error

    def _repository_context(self) -> tuple[str, str]:
        repository_root = Path(self._git("rev-parse", "--show-toplevel")).resolve()
        if repository_root != self._root:
            raise GitRepositoryError("repository root does not match the explicit request")
        object_format = self._git("rev-parse", "--show-object-format")
        return f"git:{object_format}:{repository_root.as_posix()}", object_format

    def _index_marker(self) -> str:
        index_path = Path(self._git("rev-parse", "--git-path", "index"))
        if not index_path.is_absolute():
            index_path = self._root / index_path
        try:
            payload = index_path.read_bytes()
        except FileNotFoundError:
            return "missing"
        except OSError as error:
            raise GitRepositoryError(f"cannot read Git index: {error}") from error
        return f"sha256:{hashlib.sha256(payload).hexdigest()};bytes:{len(payload)}"

    def _head_or_none(self, suffix: str) -> str | None:
        value = self._git(
            "rev-parse",
            "--verify",
            f"HEAD^{{{suffix}}}",
            allowed=(0, 128),
        )
        return value or None

    def _head_marker(self) -> tuple[str | None, str | None]:
        return self._head_or_none("commit"), self._head_or_none("tree")

    def capture_head(self) -> HeadEvidence:
        repository_id, _ = self._repository_context()
        commit = self._head_or_none("commit")
        tree = self._head_or_none("tree")
        if commit is None or tree is None:
            raise GitRepositoryError("HEAD does not identify a commit and tree")
        locator = self._git("symbolic-ref", "-q", "HEAD", allowed=(0, 1)) or None
        return HeadEvidence(repository_id, commit, tree, locator)

    def capture_index(self) -> IndexEvidence:
        repository_id, object_format = self._repository_context()
        index_before = self._index_marker()
        head_before = self._head_marker()
        raw = self._git_bytes("ls-files", "--stage", "-z")
        head_after = self._head_marker()
        index_after = self._index_marker()
        if index_before != index_after:
            raise IndexChangedError("Git index changed during capture")
        if head_before != head_after:
            raise IndexChangedError("HEAD changed during index capture")
        base_commit, base_tree = head_before

        entries: list[IndexEntry] = []
        for record in raw.split(b"\0"):
            if not record:
                continue
            try:
                metadata, path_bytes = record.split(b"\t", 1)
                mode_bytes, object_bytes, stage_bytes = metadata.split(b" ", 2)
                path = path_bytes.decode("utf-8")
                mode = mode_bytes.decode("ascii")
                object_id = object_bytes.decode("ascii")
                stage = int(stage_bytes.decode("ascii"))
            except (ValueError, UnicodeDecodeError) as error:
                raise GitRepositoryError("unsupported index entry encoding or shape") from error
            if path.startswith("/") or ".." in path.replace("\\", "/").split("/"):
                raise GitRepositoryError("index contains an unsafe workspace path")
            entries.append(IndexEntry(path, stage, mode, object_id))

        ordered = tuple(sorted(entries))
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
            ("HEAD is unborn or unavailable; index has no committed base.",)
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
