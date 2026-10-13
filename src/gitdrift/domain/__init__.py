"""Canonical immutable domain records and identity operations."""

from .identity import IDENTITY_SCHEME, canonical_bytes, stable_id
from .records import (
    ArtifactSnapshot,
    Case,
    Comparison,
    CompletenessDeclaration,
    CompletenessDimension,
    DerivationClass,
    DiagnosticRecord,
    EvidenceClass,
    EvidenceReference,
    Fact,
    Investigation,
    Obligation,
    ObligationEvaluation,
    RawChange,
    RepositoryState,
    ReproductionManifest,
    StateKind,
)
from .validation import ReferenceClosureError, validate_reference_closure

__all__ = [
    "IDENTITY_SCHEME", "ArtifactSnapshot", "Case", "Comparison",
    "CompletenessDeclaration", "CompletenessDimension", "DerivationClass",
    "DiagnosticRecord", "EvidenceClass", "EvidenceReference", "Fact",
    "Investigation", "Obligation", "ObligationEvaluation", "RawChange",
    "ReferenceClosureError", "RepositoryState", "ReproductionManifest",
    "StateKind", "canonical_bytes", "stable_id", "validate_reference_closure",
]
