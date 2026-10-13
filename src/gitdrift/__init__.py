"""Supported public package boundary for the Gitdrift development skeleton."""

from .contracts import (
    CapabilityDocument,
    Completeness,
    Diagnostic,
    DiagnosticSeverity,
    ExecutionStatus,
)
from .discovery import discover_capabilities
from .domain import IDENTITY_SCHEME, Investigation, stable_id, validate_reference_closure
from .version import NATIVE_SCHEMA_VERSION, __version__

__all__ = [
    "CapabilityDocument",
    "Completeness",
    "Diagnostic",
    "DiagnosticSeverity",
    "ExecutionStatus",
    "IDENTITY_SCHEME",
    "Investigation",
    "NATIVE_SCHEMA_VERSION",
    "__version__",
    "discover_capabilities",
    "stable_id",
    "validate_reference_closure",
]
