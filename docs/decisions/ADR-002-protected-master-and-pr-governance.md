# ADR-002: Protected master and pull-request governance

## Status

Accepted.

## Context

Commit `40d42ab` established the initial Gitdrift documentation baseline directly on `master`. After that bootstrap boundary, direct changes to `master` would bypass the review and release metadata needed to preserve controlling state and make architectural evolution traceable.

## Decision

After bootstrap commit `40d42ab`, every change to `master` must be merged through a pull request.

Every pull request must:

1. originate from a non-`master` branch;
2. state its scope and controlling baseline;
3. identify validation performed and unresolved limitations;
4. carry the labels applicable to its change type, area, and review state;
5. belong to the milestone whose acceptance boundary it advances;
6. preserve or explicitly supersede established obligations;
7. avoid mixing unrelated product increments.

Repository automation must be idempotent. Re-running governance automation must update the intended labels, milestone, branch, and pull request rather than create duplicates.

## Initial taxonomy

The inception taxonomy contains:

```text
type:documentation
area:architecture
profile:state-awareness
status:needs-review
```

The first milestone is:

```text
Gitdrift 0.1: repository-state alignment and provenance
```

Additional taxonomy must be introduced only when an actual workstream requires it.

## Consequences

- `master` remains the controlling integrated state.
- Candidate work remains explicitly reviewable until merged.
- Labels classify the nature and review state of work.
- Milestones express acceptance boundaries rather than acting as generic calendars.
- Pull requests become the integration boundary, not the source of semantic truth.
- Gitdrift's core analysis continues to rely on repository evidence; forge metadata remains outside the initial analysis engine.
