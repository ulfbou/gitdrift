"""Compatibility imports for domain records.
Prefer importing from the owning domain modules.
"""

from .cases import Case
from .comparisons import (
    ComparisonKind,
    MatrixEntryStatus,
    StateComparisonMatrix,
    StateComparisonRow,
    construct_required_comparison_matrix,
)
from .completeness import (
    CompletenessDeclaration,
    CompletenessDimension,
)
from .evidence import (
    DerivationClass,
    EvidenceClass,
    EvidenceReference,
    Fact,
)
from .investigation import (
    DiagnosticRecord,
    Investigation,
    ReproductionManifest,
)
from .obligations import Obligation, ObligationEvaluation
from .states import (
    ArtifactSnapshot,
    Comparison,
    RawChange,
    RepositoryState,
    StateKind,
)

__all__ = [
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
    "RepositoryState",
    "ReproductionManifest",
    "StateComparisonMatrix",
    "StateComparisonRow",
    "StateKind",
    "construct_required_comparison_matrix",
]
