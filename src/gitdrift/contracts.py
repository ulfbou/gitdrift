"""Typed contract foundations shared by the library and process adapters."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping


class ExecutionStatus(StrEnum):
    COMPLETED = "completed"
    COMPLETED_UNRESOLVED = "completed-unresolved"
    COMPLETED_PARTIAL = "completed-partial"
    UNSUPPORTED = "unsupported"
    INVALID_REQUEST = "invalid-request"
    FAILED = "failed"


class Completeness(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    NOT_REQUESTED = "not-requested"
    NOT_APPLICABLE = "not-applicable"


class DiagnosticSeverity(StrEnum):
    INFORMATIONAL = "informational"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    severity: DiagnosticSeverity
    category: str
    message: str
    completeness_effects: Mapping[str, Completeness]

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "completeness_effects": {
                key: value.value for key, value in sorted(self.completeness_effects.items())
            },
        }


@dataclass(frozen=True, slots=True)
class CapabilityDocument:
    capability_schema_version: str
    package_version: str
    native_schema_versions: tuple[str, ...]
    available_profiles: tuple[str, ...]
    unavailable_profiles: tuple[str, ...]
    available_operations: tuple[str, ...]
    unavailable_operations: tuple[str, ...]
    output_formats: tuple[str, ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_schema_version": self.capability_schema_version,
            "package_version": self.package_version,
            "native_schema_versions": list(self.native_schema_versions),
            "profiles": {
                "available": list(self.available_profiles),
                "unavailable": list(self.unavailable_profiles),
            },
            "operations": {
                "available": list(self.available_operations),
                "unavailable": list(self.unavailable_operations),
            },
            "output_formats": list(self.output_formats),
            "limitations": list(self.limitations),
        }
