"""Canonical immutable domain records and identity operations."""

from .cases import Case
from .comparisons import (
    ComparisonKind,
    MatrixEntryStatus,
    StateComparisonMatrix,
    StateComparisonRow,
    construct_required_comparison_matrix,
)
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
    "ComparisonKind",
    "CompletenessDeclaration",
    "CompletenessDimension",
    "DerivationClass",
    "DiagnosticRecord",
    "EvidenceClass",
    "EvidenceReference",
    "Fact",
    "Investigation",
    "MatrixEntryStatus",
    "Obligation",
    "ObligationEvaluation",
    "RawChange",
    "ReferenceClosureError",
    "RepositoryState",
    "ReproductionManifest",
    "StateComparisonMatrix",
    "StateComparisonRow",
    "StateKind",
    "canonical_bytes",
    "construct_required_comparison_matrix",
    "stable_id",
    "validate_reference_closure",
]
