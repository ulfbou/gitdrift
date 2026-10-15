"""Executable read-only state-awareness profile composition."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from gitdrift.adapters.git import (
    GitRepositoryReader,
    GitStateComparator,
)
from gitdrift.adapters.serialization import (
    CanonicalNativeJsonSerializer,
)
from gitdrift.application import (
    ComparisonMatrixRequest,
    compose_state_comparison_matrix,
)
from gitdrift.domain import (
    CompletenessDeclaration,
    CompletenessDimension,
    DiagnosticRecord,
    Investigation,
    ReproductionManifest,
    stable_id,
)
from gitdrift.contracts import ExecutionStatus
from gitdrift.ports import NativeArtifact
from gitdrift.version import (
    NATIVE_SCHEMA_VERSION,
    __version__,
)

_PROFILE_ID = "gitdrift-state-awareness"
_PROFILE_VERSION = "1.0.0"
_CAPABILITY_ID = "gitdrift-state-awareness-composition-v1"
_DEFAULT_BUDGETS = {
    "comparisons": 4,
}


@dataclass(frozen=True, slots=True)
class StateAwarenessRequest:
    """Explicit inputs for one read-only state-awareness execution."""

    repository: Path
    include_upstream: bool = True
    budgets: tuple[tuple[str, int], ...] = tuple(
        sorted(_DEFAULT_BUDGETS.items())
    )

    def __post_init__(self) -> None:
        root = self.repository.resolve()
        if not root.is_dir():
            raise ValueError(
                "state-awareness repository must be an existing directory"
            )

        names: set[str] = set()
        for name, limit in self.budgets:
            if (
                not isinstance(name, str)
                or not name
                or name in names
                or not isinstance(limit, int)
                or isinstance(limit, bool)
                or limit < 1
            ):
                raise ValueError(
                    "budgets require unique names and positive integer limits"
                )
            names.add(name)

        object.__setattr__(self, "repository", root)

    @property
    def configuration_identity(self) -> str:
        return stable_id(
            "state-awareness-configuration",
            {
                "profile_id": _PROFILE_ID,
                "profile_version": _PROFILE_VERSION,
                "include_upstream": self.include_upstream,
                "budgets": dict(self.budgets),
            },
        )


@dataclass(frozen=True, slots=True)
class StateAwarenessResult:
    """A validated native artifact and explicit execution diagnostics."""

    artifact: NativeArtifact
    status: ExecutionStatus
    diagnostics: tuple[DiagnosticRecord, ...]


class StateAwarenessProfile:
    """Compose accepted state capture, comparison, and native contracts."""

    profile_id = _PROFILE_ID
    profile_version = _PROFILE_VERSION

    def run(
        self,
        request: StateAwarenessRequest,
    ) -> StateAwarenessResult:
        budgets = dict(request.budgets)
        required_comparisons = 4
        comparison_budget = budgets.get("comparisons")

        if (
            comparison_budget is not None
            and comparison_budget < required_comparisons
        ):
            raise ValueError(
                "comparison budget cannot represent the complete "
                "required state-awareness matrix"
            )

        reader = GitRepositoryReader(request.repository)
        comparator = GitStateComparator(request.repository)

        composed = compose_state_comparison_matrix(
            ComparisonMatrixRequest(
                include_upstream=request.include_upstream,
            ),
            reader,
            comparator,
        )

        comparisons = tuple(
            execution.result.comparison
            for execution in composed.executions
            if execution.result is not None
        )
        changes = tuple(
            change
            for execution in composed.executions
            if execution.result is not None
            for change in execution.result.changes
        )

        unavailable_rows = tuple(
            execution.row
            for execution in composed.executions
            if execution.result is None
        )

        diagnostics = tuple(
            DiagnosticRecord(
                code="GD-STATE-COMPARISON-UNAVAILABLE",
                severity="informational",
                category="evidence-unavailable",
                affected_ids=tuple(
                    identity
                    for identity in (
                        row.left_state_id,
                        row.right_state_id,
                    )
                    if identity is not None
                ),
                completeness_effects={
                    CompletenessDimension.SELECTED_REFS: (
                        "not-applicable"
                        if row.kind.value == "head-and-upstream"
                        else "unavailable"
                    )
                },
            )
            for row in unavailable_rows
        )

        comparison_completeness = (
            "complete"
            if not unavailable_rows
            else "partial"
        )

        completeness = CompletenessDeclaration(
            {
                CompletenessDimension.STATE_CAPTURE: "complete",
                CompletenessDimension.ARTIFACT_COVERAGE: "complete",
                CompletenessDimension.SELECTED_REFS: (
                    "complete"
                    if not unavailable_rows
                    else "not-applicable"
                ),
                CompletenessDimension.SEMANTIC_EXTRACTION: (
                    "not-requested"
                ),
                CompletenessDimension.OBLIGATION_COVERAGE: (
                    "not-requested"
                ),
                CompletenessDimension.COUNTEREVIDENCE_SEARCH: (
                    "not-requested"
                ),
                CompletenessDimension.EXTERNAL_CONTEXT: (
                    "not-requested"
                ),
            },
            limitations=(
                ()
                if comparison_completeness == "complete"
                else (
                    "One or more comparison endpoints were unavailable; "
                    "the required matrix rows remain represented.",
                )
            ),
        )

        manifest = ReproductionManifest(
            repository_id=composed.states[0].repository_id,
            state_ids=tuple(
                state.id for state in composed.states
            ),
            configuration_identity=(
                request.configuration_identity
            ),
            capability_identity=_CAPABILITY_ID,
            native_schema_version=NATIVE_SCHEMA_VERSION,
            producer_version=__version__,
            budgets=budgets,
        )

        investigation = Investigation(
            manifest=manifest,
            states=composed.states,
            comparisons=comparisons,
            changes=changes,
            diagnostics=diagnostics,
            completeness=completeness,
        )

        artifact = CanonicalNativeJsonSerializer().serialize(
            investigation
        )

        return StateAwarenessResult(
            artifact=artifact,
            status=(
                ExecutionStatus.COMPLETED
                if not unavailable_rows
                else ExecutionStatus.COMPLETED_PARTIAL
            ),
            diagnostics=diagnostics,
        )
