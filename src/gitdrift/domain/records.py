"""Compatibility imports for domain records.
Prefer importing from the owning domain modules.
"""

from .cases import Case
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
    "RepositoryState",
    "ReproductionManifest",
    "StateKind",
]
