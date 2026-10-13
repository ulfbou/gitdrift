# Provisional state capture

## Purpose

This specification defines reproducible, read-only capture of the Git index and working tree. These states do not have stable refs and therefore require explicit identities and manifests.

## Common capture record

Every provisional state records:

```text
state kind
capture identity
base commit and tree
index identity or manifest
workspace root identity
capture start and completion markers
path scope
untracked and ignored-file policies
file entries and content identities
file modes, symlinks, and submodules
unmerged or unsupported entries
configuration relevant to capture
mutation check
limitations
```

The capture identity derives from the normalized manifest and exact content identities, not from a timestamp or mutable branch name.

## Index capture

The index capture records each selected entry's path, stage, mode, and object identity. A normal index entry can be represented by its staged blob and mode. Unmerged entries retain all available stages and are not silently collapsed into a resolved file.

The captured index records the `HEAD` commit used as its base when available. An unborn branch or missing `HEAD` is represented explicitly.

## Working-tree capture

The working-tree capture records selected tracked files as exact bytes with path, mode, and symlink treatment. Deletions are represented as absent entries relative to the captured index or base, not discarded.

### Untracked files

The request declares one policy:

```text
exclude
include-selected
include-all-visible
```

Excluded untracked files are outside artifact coverage. Included files receive exact content identities and manifest entries.

### Ignored files

Ignored files are excluded by default. Inclusion requires an explicit policy and is recorded separately from untracked inclusion. The capture must not infer that ignored content is generated, irrelevant, or non-authoritative.

## Modes, symlinks, and submodules

File mode changes are evidence. Symlinks are captured as links and target text according to Git semantics, not followed into arbitrary filesystem content. Submodules retain the gitlink identity and working-directory status supported by the adapter; their nested repositories are not traversed unless separately requested.

## Race and mutation detection

Capture records observations needed to detect relevant mutation during acquisition. If selected index or working-tree content changes before capture completes, the state is not reported as reproducible. The adapter retries only under an explicit bounded policy or returns an incomplete capture diagnostic.

A capture must not modify tracked files, the index, refs, configuration, hooks, or repository metadata to obtain stability.

## Read-only guarantee

Read-only plumbing that creates temporary in-memory data or unreachable Git objects is permitted only when it does not alter refs, index entries, working-tree files, or configured repository behavior. Any persistent cache or explicit output uses a caller-selected sink outside the domain state.

## Completeness

Completeness reports path scope, policy exclusions, unreadable content, unsupported file kinds, submodule depth, unmerged entries, and race detection. Exact evidence already captured remains usable when another dimension is partial.
