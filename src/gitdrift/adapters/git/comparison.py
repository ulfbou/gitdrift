"""Read-only Git execution of provisional state comparisons."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from gitdrift.application import (
    capture_head,
    capture_index,
    capture_working_tree,
)
from gitdrift.domain import Comparison, RawChange
from gitdrift.ports import (
    DiffOptions,
    StateComparisonResult,
)

from .repository import GitRepositoryError, GitRepositoryReader


@dataclass(frozen=True, slots=True)
class _Endpoint:
    state_id: str
    marker: str


class GitStateComparator:
    """Execute deterministic comparisons without mutating repository state."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._reader = GitRepositoryReader(self._root)

    def _git_bytes(
        self,
        *arguments: str,
        allowed: tuple[int, ...] = (0,),
    ) -> bytes:
        result = subprocess.run(
            [
                "git",
                "-c",
                "core.hooksPath=/dev/null",
                "-c",
                "diff.external=",
                "-c",
                "diff.noprefix=false",
                "-c",
                "core.attributesfile=/dev/null",
                *arguments,
            ],
            cwd=self._root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode not in allowed:
            detail = result.stderr.decode(
                "utf-8",
                errors="replace",
            ).strip()
            raise GitRepositoryError(
                detail or "Git comparison failed"
            )
        return result.stdout

    @staticmethod
    def _safe_path(raw: bytes) -> str:
        try:
            value = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise GitRepositoryError(
                "Git reported a non-UTF-8 comparison path"
            ) from error

        portable = value.replace(chr(92), "/")
        if (
            not portable
            or portable.startswith("/")
            or ".." in portable.split("/")
        ):
            raise GitRepositoryError(
                f"unsafe comparison path: {value!r}"
            )
        return portable

    @staticmethod
    def _status(value: str) -> str:
        return {
            "A": "addition",
            "D": "deletion",
            "M": "modification",
            "T": "type-change",
            "U": "unmerged",
        }.get(value, "unsupported")

    @staticmethod
    def _identity(value: str) -> str | None:
        if set(value) == {"0"}:
            return None
        return f"git-object:{value}"

    @staticmethod
    def _binary_treatment(
        patch: bytes,
        source_path: str | None,
        destination_path: str | None,
    ) -> str:
        marker = b"Binary files "
        if marker in patch or b"GIT binary patch" in patch:
            return "binary-preserved"
        if source_path is None or destination_path is None:
            return "path-presence"
        return "text-patch"

    def _arguments(
        self,
        base: tuple[str, ...],
        options: DiffOptions,
    ) -> list[str]:
        arguments = [
            *base,
            "--no-ext-diff",
            "--no-textconv",
            "--full-index",
            f"--diff-algorithm={options.algorithm}",
            "--submodule=" + options.submodule,
        ]

        if "--patch" in base:
            arguments.append("--binary")

        if options.whitespace == "ignore-all":
            arguments.append("--ignore-all-space")
        elif options.whitespace == "ignore-change":
            arguments.append("--ignore-space-change")
        elif options.whitespace != "retain":
            raise ValueError(
                f"unsupported whitespace option: "
                f"{options.whitespace}"
            )

        if options.binary != "preserve":
            raise ValueError(
                f"unsupported binary option: {options.binary}"
            )

        if options.rename_detection or options.copy_detection:
            raise ValueError(
                "rename and copy detection are not supported "
                "by this deterministic increment"
            )

        arguments.append("--")
        arguments.extend(options.pathspecs)
        return arguments

    def _raw_records(
        self,
        base: tuple[str, ...],
        comparison: Comparison,
        options: DiffOptions,
    ) -> tuple[RawChange, ...]:
        raw = self._git_bytes(
            *self._arguments(
                (*base, "--raw", "-z"),
                options,
            )
        )
        patch = self._git_bytes(
            *self._arguments(
                (*base, "--patch"),
                options,
            )
        )
        patch_identity = (
            "sha256:" + hashlib.sha256(patch).hexdigest()
        )

        fields = raw.split(b"\0")
        if fields and fields[-1] == b"":
            fields.pop()

        changes: list[RawChange] = []
        index = 0

        while index < len(fields):
            header = fields[index]
            index += 1
            if not header.startswith(b":"):
                raise GitRepositoryError(
                    "Git raw diff returned an invalid record"
                )

            try:
                metadata = header[1:].decode("ascii").split()
                (
                    source_mode,
                    destination_mode,
                    source_object,
                    destination_object,
                    status_token,
                ) = metadata
            except (UnicodeDecodeError, ValueError) as error:
                raise GitRepositoryError(
                    "Git raw diff metadata is invalid"
                ) from error

            status_code = status_token[:1]
            if status_code in {"R", "C"}:
                raise GitRepositoryError(
                    "rename/copy output was not requested"
                )

            if index >= len(fields):
                raise GitRepositoryError(
                    "Git raw diff omitted a path"
                )

            path = self._safe_path(fields[index])
            index += 1
            status = self._status(status_code)

            source_path = None if status == "addition" else path
            destination_path = (
                None if status == "deletion" else path
            )

            limitations = ()
            if status == "unsupported":
                limitations = (
                    f"unsupported Git raw status: {status_token}",
                )
            elif status == "unmerged":
                limitations = (
                    "unmerged entry requires stage-specific evidence",
                )

            changes.append(
                RawChange(
                    comparison_id=comparison.id,
                    status=status,
                    source_path=source_path,
                    destination_path=destination_path,
                    source_identity=self._identity(
                        source_object
                    ),
                    destination_identity=self._identity(
                        destination_object
                    ),
                    source_mode=(
                        None
                        if source_mode == "000000"
                        else source_mode
                    ),
                    destination_mode=(
                        None
                        if destination_mode == "000000"
                        else destination_mode
                    ),
                    patch_identity=patch_identity,
                    binary_treatment=self._binary_treatment(
                        patch,
                        source_path,
                        destination_path,
                    ),
                    submodule_identity=(
                        self._identity(destination_object)
                        if destination_mode == "160000"
                        else None
                    ),
                    diff_options=options.to_mapping(),
                    limitations=limitations,
                )
            )

        return tuple(changes)

    def _execute(
        self,
        *,
        kind: str,
        question: str,
        command: tuple[str, ...],
        left: Callable[[], _Endpoint],
        right: Callable[[], _Endpoint],
        options: DiffOptions,
    ) -> StateComparisonResult:
        before_left = left()
        before_right = right()

        comparison = Comparison(
            left_state_id=before_left.state_id,
            right_state_id=before_right.state_id,
            kind=kind,
            question=question,
            diff_options=options.to_mapping(),
            ancestry_established=False,
        )
        changes = self._raw_records(
            command,
            comparison,
            options,
        )

        after_left = left()
        after_right = right()
        if before_left != after_left or before_right != after_right:
            raise GitRepositoryError(
                "comparison endpoint changed during execution"
            )

        return StateComparisonResult(comparison, changes)

    def _head(self) -> _Endpoint:
        state = capture_head(self._reader)
        return _Endpoint(state.id, state.content_identity)

    def _index(self) -> _Endpoint:
        state = capture_index(self._reader)
        return _Endpoint(state.id, state.content_identity)

    def _working_tree(self) -> _Endpoint:
        state = capture_working_tree(self._reader)
        return _Endpoint(state.id, state.content_identity)

    def compare_head_to_index(
        self,
        *,
        options: DiffOptions = DiffOptions(),
    ) -> StateComparisonResult:
        return self._execute(
            kind="head-to-index",
            question=(
                "What is staged relative to the captured HEAD state?"
            ),
            command=("diff", "--cached", "HEAD"),
            left=self._head,
            right=self._index,
            options=options,
        )

    def compare_index_to_working_tree(
        self,
        *,
        options: DiffOptions = DiffOptions(),
    ) -> StateComparisonResult:
        return self._execute(
            kind="index-to-worktree",
            question=(
                "What differs from the captured index "
                "in the working tree?"
            ),
            command=("diff",),
            left=self._index,
            right=self._working_tree,
            options=options,
        )

    def compare_head_to_working_tree(
        self,
        *,
        options: DiffOptions = DiffOptions(),
    ) -> StateComparisonResult:
        return self._execute(
            kind="head-to-worktree",
            question=(
                "What is the cumulative local difference from HEAD?"
            ),
            command=("diff", "HEAD"),
            left=self._head,
            right=self._working_tree,
            options=options,
        )
