"""Supported public package boundary for the Gitdrift development skeleton."""

from .contracts import (
    CapabilityDocument,
    Completeness,
    Diagnostic,
    DiagnosticSeverity,
    ExecutionStatus,
)
from .discovery import discover_capabilities
from .version import NATIVE_SCHEMA_VERSION, __version__

__all__ = [
    "CapabilityDocument",
    "Completeness",
    "Diagnostic",
    "DiagnosticSeverity",
    "ExecutionStatus",
    "NATIVE_SCHEMA_VERSION",
    "__version__",
    "discover_capabilities",
]
