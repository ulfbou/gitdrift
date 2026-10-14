"""Application use cases."""

from .capture import (
    capture_head,
    capture_index,
    capture_upstream,
    capture_working_tree,
)
from .comparison import (
    ComparisonMatrixExecution,
    ComparisonMatrixRequest,
    ComparisonMatrixResult,
    compose_state_comparison_matrix,
)

__all__ = [
    "ComparisonMatrixExecution",
    "ComparisonMatrixRequest",
    "ComparisonMatrixResult",
    "capture_head",
    "capture_index",
    "capture_upstream",
    "capture_working_tree",
    "compose_state_comparison_matrix",
]
