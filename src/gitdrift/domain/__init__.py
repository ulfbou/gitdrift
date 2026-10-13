"""Canonical immutable domain records and identity operations."""

from .cases import Case
from .completeness import CompletenessDeclaration, CompletenessDimension
from .evidence import DerivationClass, EvidenceClass, EvidenceReference, Fact
from .identity import IDENTITY_SCHEME, canonical_bytes, stable_id
from .investigation import DiagnosticRecord, Investigation, ReproductionManifest
from .obligations import Obligation, ObligationEvaluation
from .states import (
    ArtifactSnapshot,
    Comparison,
    RawChange,
    RepositoryState,
    StateKind,
)
from .validation import ReferenceClosureError, validate_reference_closure

__all__ = [
    "IDENTITY_SCHEME",
    "ArtifactSnapshot",
    "Case",
    "Comparison",
    "CompletenessDeclaration",
    "CompletenessDimension",
    "DerivationClass",
    "DiagnosticRecord",
    "EvidenceClass",
    "EvidenceReference",
    "Fact",
    "Investigation",
    "Obligation",
    "ObligationEvaluation",
    "RawChange",
    "ReferenceClosureError",
    "RepositoryState",
    "ReproductionManifest",
    "StateKind",
    "canonical_bytes",
    "stable_id",
    "validate_reference_closure",
]
