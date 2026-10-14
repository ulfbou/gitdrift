"""Versioned, read-only Python module maintainability policy."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from .model import ValidationFailure, ValidationScope

POLICY_ID = "gitdrift-python-module-maintainability-v1"
POLICY_PATH = Path("scripts/validation/module-maintainability.json")
VALIDATION_ROOT = Path("scripts/validation")


@dataclass(frozen=True, slots=True)
class ModuleLimit:
    role: str
    maximum_bytes: int
    maximum_lines: int


@dataclass(frozen=True, slots=True)
class ModuleMeasurement:
    path: Path
    role: str
    byte_count: int
    line_count: int
    maximum_bytes: int
    maximum_lines: int
    exception_state: str = "none"

    @property
    def exceeds_limit(self) -> bool:
        return (
            self.byte_count > self.maximum_bytes
            or self.line_count > self.maximum_lines
        )

    def diagnostic(self) -> str:
        return (
            f"path={self.path.as_posix()} "
            f"role={self.role} "
            f"bytes={self.byte_count} "
            f"maximum_bytes={self.maximum_bytes} "
            f"lines={self.line_count} "
            f"maximum_lines={self.maximum_lines} "
            f"exception={self.exception_state}"
        )


@dataclass(frozen=True, slots=True)
class ModuleException:
    path: Path
    maximum_bytes: int
    maximum_lines: int
    expires_after: str
    reason: str


@dataclass(frozen=True, slots=True)
class MaintainabilityPolicy:
    policy_id: str
    limits: Mapping[str, ModuleLimit]
    exceptions: Mapping[Path, ModuleException]


def _physical_line_count(payload: bytes) -> int:
    if not payload:
        return 0
    return payload.count(b"\n") + (0 if payload.endswith(b"\n") else 1)


def _safe_relative_path(value: object, *, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValidationFailure(f"{field} must be a non-empty string")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValidationFailure(f"{field} must be repository-relative: {value!r}")
    return path


def _positive_integer(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValidationFailure(f"{field} must be a positive integer")
    return value


def _string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationFailure(f"{field} must be a non-empty string")
    return value


def load_policy(root: Path) -> MaintainabilityPolicy:
    path = root / POLICY_PATH
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValidationFailure(
            f"cannot read maintainability policy {POLICY_PATH}: {error}"
        ) from error
    except json.JSONDecodeError as error:
        raise ValidationFailure(
            f"invalid maintainability policy {POLICY_PATH}: {error}"
        ) from error

    if not isinstance(document, dict):
        raise ValidationFailure("maintainability policy root must be an object")

    policy_id = document.get("policy_id")
    if policy_id != POLICY_ID:
        raise ValidationFailure(
            f"unsupported maintainability policy_id: {policy_id!r}"
        )

    raw_limits = document.get("limits")
    if not isinstance(raw_limits, dict):
        raise ValidationFailure("maintainability policy limits must be an object")

    required_roles = {"implementation", "repository-tooling", "test"}
    if set(raw_limits) != required_roles:
        raise ValidationFailure(
            "maintainability policy limits must define exactly: "
            + ", ".join(sorted(required_roles))
        )

    limits: dict[str, ModuleLimit] = {}
    for role, raw_limit in raw_limits.items():
        if not isinstance(raw_limit, dict):
            raise ValidationFailure(f"limit for {role} must be an object")
        limits[role] = ModuleLimit(
            role=role,
            maximum_bytes=_positive_integer(
                raw_limit.get("maximum_bytes"),
                field=f"limits.{role}.maximum_bytes",
            ),
            maximum_lines=_positive_integer(
                raw_limit.get("maximum_lines"),
                field=f"limits.{role}.maximum_lines",
            ),
        )

    raw_exceptions = document.get("exceptions")
    if not isinstance(raw_exceptions, list):
        raise ValidationFailure(
            "maintainability policy exceptions must be an array"
        )

    exceptions: dict[Path, ModuleException] = {}
    for index, raw_exception in enumerate(raw_exceptions):
        if not isinstance(raw_exception, dict):
            raise ValidationFailure(f"exceptions[{index}] must be an object")

        exception_path = _safe_relative_path(
            raw_exception.get("path"),
            field=f"exceptions[{index}].path",
        )
        if exception_path in exceptions:
            raise ValidationFailure(
                f"duplicate maintainability exception: {exception_path.as_posix()}"
            )
        if exception_path == VALIDATION_ROOT or VALIDATION_ROOT in exception_path.parents:
            raise ValidationFailure(
                "validation modules cannot receive maintainability exceptions: "
                f"{exception_path.as_posix()}"
            )

        exceptions[exception_path] = ModuleException(
            path=exception_path,
            maximum_bytes=_positive_integer(
                raw_exception.get("maximum_bytes"),
                field=f"exceptions[{index}].maximum_bytes",
            ),
            maximum_lines=_positive_integer(
                raw_exception.get("maximum_lines"),
                field=f"exceptions[{index}].maximum_lines",
            ),
            expires_after=_string(
                raw_exception.get("expires_after"),
                field=f"exceptions[{index}].expires_after",
            ),
            reason=_string(
                raw_exception.get("reason"),
                field=f"exceptions[{index}].reason",
            ),
        )

    return MaintainabilityPolicy(policy_id, limits, exceptions)


def classify_python_module(relative: Path) -> str | None:
    if relative.suffix != ".py":
        return None

    parts = relative.parts
    if not parts:
        return None

    if parts[0] == "src":
        return "implementation"

    if parts[0] == "scripts":
        return "repository-tooling"

    if parts[0] == "tests":
        if "fixtures" in parts[1:]:
            return None
        return "test"

    return None


def python_modules(root: Path, scope: ValidationScope) -> Iterable[Path]:
    for directory in ("src", "scripts", "tests"):
        base = root / directory
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            relative = path.relative_to(root)
            if scope.includes(relative):
                yield relative


def measure_module(
    root: Path,
    relative: Path,
    policy: MaintainabilityPolicy,
) -> ModuleMeasurement | None:
    role = classify_python_module(relative)
    if role is None:
        return None

    path = root / relative
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise ValidationFailure(
            f"cannot measure Python module {relative.as_posix()}: {error}"
        ) from error

    limit = policy.limits[role]
    maximum_bytes = limit.maximum_bytes
    maximum_lines = limit.maximum_lines
    exception_state = "none"

    exception = policy.exceptions.get(relative)
    if exception is not None:
        maximum_bytes = exception.maximum_bytes
        maximum_lines = exception.maximum_lines
        exception_state = (
            f"active;expires_after={exception.expires_after};"
            f"reason={exception.reason}"
        )

    return ModuleMeasurement(
        path=relative,
        role=role,
        byte_count=len(payload),
        line_count=_physical_line_count(payload),
        maximum_bytes=maximum_bytes,
        maximum_lines=maximum_lines,
        exception_state=exception_state,
    )


def module_maintainability(
    root: Path,
    scope: ValidationScope = ValidationScope(),
) -> None:
    policy = load_policy(root)
    failures: list[str] = []

    for relative in python_modules(root, scope):
        measurement = measure_module(root, relative, policy)
        if measurement is None:
            continue

        print(
            f"INFO module-maintainability policy={policy.policy_id} "
            f"{measurement.diagnostic()}"
        )
        if measurement.exceeds_limit:
            failures.append(measurement.diagnostic())

    unknown_exceptions = sorted(
        path
        for path in policy.exceptions
        if classify_python_module(path) is None
    )
    if unknown_exceptions:
        failures.extend(
            "exception does not identify a classified Python module: "
            + path.as_posix()
            for path in unknown_exceptions
        )

    missing_exceptions = sorted(
        path for path in policy.exceptions if not (root / path).is_file()
    )
    if missing_exceptions:
        failures.extend(
            "exception path does not exist: " + path.as_posix()
            for path in missing_exceptions
        )

    if failures:
        raise ValidationFailure(
            "Python module maintainability failed:\n" + "\n".join(failures)
        )
