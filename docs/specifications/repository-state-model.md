# Repository state model

## Scope

This specification defines the initial vocabulary for immutable or captured repository states and transitions. It does not define the complete serialized schema.

## Repository state

A `RepositoryState` is a content-addressable or reproducibly captured view of relevant repository content.

Initial state kinds:

```text
Commit
BranchTip
Index
WorkingTree
ExplicitSnapshot
SyntheticComparison
```

A branch tip resolves to a commit identity at capture time. The report retains both the ref locator and immutable commit identity.

The index and working tree are provisional states. They require captured identities and manifests because they are not inherently stable Git refs.

A synthetic comparison is an analytical state or relation. It must never be presented as a repository commit.

## Transition

A `Transition` relates two states and records the comparison semantics used.

Transition kinds include:

```text
parent-to-child
ref-to-ref
head-to-index
index-to-worktree
head-to-worktree
alternate-chain
synthetic
```

A merge commit has a distinct transition from each parent. Findings must identify the relevant parent relationship.

## Artifact snapshot

An `ArtifactSnapshot` includes:

```text
state identity
workspace-relative path
content identity
file mode or artifact kind when available
exact bytes or a retrievable evidence reference
```

A path is a location, not a durable artifact identity.

## Artifact lineage

An `ArtifactLineage` relates artifact instances across states. Supported relationship classes begin with:

```text
same-path modification
rename candidate
copy candidate
move candidate
restoration candidate
replacement candidate
split candidate
merge candidate
```

Deterministic Git relationships and inferred relationships remain distinguishable.

## Fragment and concept representation

A `Fragment` identifies a region, symbol, section, or other bounded representation inside an artifact snapshot.

A `ConceptRepresentation` connects a semantic concept to one or more fragments at a state and classifies each fragment's role:

```text
authority
normative specification
implementation
enforcement
explanation
navigation
historical evidence
generated derivation
```

The same concept may be represented in one file at one state and dispersed across many artifacts at another.

## Evidence identity

Every state, transition, snapshot, fragment relationship, fact, and assessment receives a stable identifier derived from immutable inputs where possible.

Stable identity must not depend on display order. Mutable ref names are recorded as locators, not sole identities.

## Completeness

Every result declares relevant completeness dimensions, including:

```text
graph traversal
selected refs
state capture
lineage resolution
semantic extraction
obligation coverage
external context
```

Allowed values must distinguish at least complete, partial, unavailable, not-requested, and not-applicable.

## Read-only invariant

State acquisition and analysis do not modify refs, commits, the index, the working tree, configuration, or tracked files. Any future export writes only to an explicit output sink.
