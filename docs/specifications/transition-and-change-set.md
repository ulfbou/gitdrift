# Transition and change set

## Purpose

This specification defines repository transitions, analytical comparisons, raw changes, interpreted deltas, and the configuration required to reproduce them.

## Transition contract

A `Transition` contains:

```text
transition identity
from-state identity
to-state identity
transition kind
ancestry claim, if any
parent identity and parent number, when applicable
traversal configuration
diff configuration
change-set identity
completeness and limitations
```

The ordered endpoints state comparison direction. They do not imply ancestry unless the transition kind establishes it.

## Transition kinds

### Parent-to-child

Relates one commit parent to its child. For a merge commit, each parent produces a distinct transition with its parent identity and parent number.

### Ref-to-ref

Compares immutable tips captured from two refs. It is a state comparison and does not by itself represent a commit transition.

### HEAD to INDEX

Compares the captured `HEAD` commit state with the captured index state and isolates staged changes.

### INDEX to WORKTREE

Compares the captured index with the captured working tree under an explicit untracked and ignored-file policy and isolates unstaged changes.

### HEAD to WORKTREE

Compares the captured `HEAD` state with the captured working tree. It is a cumulative local-state comparison and must not replace the two provisional transitions above.

### Alternate-chain

Relates selected states or transitions on alternate histories. Correspondence, patch equivalence, and semantic equivalence remain separately classified claims.

### Synthetic

Represents an explicitly defined analytical comparison. It must not be presented as a repository commit or natural ancestry transition.

## Change set

A change set is the deterministic repository-evidence result for one transition. Each path change records, where applicable:

```text
status
source path
destination path
source object identity
destination object identity
source file mode
destination file mode
raw patch or retrievable patch identity
binary or text classification
rename or copy score and method
submodule identity
limitations
```

Statuses must distinguish at least addition, deletion, modification, type change, rename candidate, copy candidate, and unmerged or unsupported states when encountered.

## Raw changes and interpreted deltas

A `RawChange` reports what the configured repository comparison proves. A structural or semantic delta is a derived interpretation referencing raw changes and snapshots.

- A deletion is not automatically semantic loss.
- A rename or copy score is evidence for a structural candidate, not semantic equivalence.
- A semantic fact delta never replaces the raw patch or snapshot evidence.
- Unsupported artifacts remain exact evidence even when no semantic delta can be extracted.

## Traversal configuration

Every history-derived transition set records:

```text
selected start and end states
history mode
parent policy
path or subject filters
ref selection
merge-base policy
rename and copy detection configuration
ignored-revision or mechanical-change policy
ordering
limits and truncation
```

Simplified history, first-parent history, full ancestry, and lineage-selected history are distinct modes. A regression conclusion may not silently rely on a simplified traversal.

## Diff configuration

Every change set records options that can alter the result, including:

```text
comparison endpoints
pathspecs
rename and copy detection
similarity thresholds
diff algorithm
whitespace handling
binary handling
submodule handling
text conversion or attributes
```

Defaults are explicit in the reproduction manifest rather than inherited invisibly from ambient user configuration.

## Mechanical-change suppression

Raw transitions and changes are never deleted from evidence. A semantic projection may suppress a declared mechanical-change candidate when:

1. the suppression policy is identified;
2. the excluded evidence remains retrievable;
3. the projection records the exclusion rationale;
4. completeness reflects the exclusion when relevant; and
5. the suppression can be reversed without reacquiring repository evidence.

Suppression affects a projection, not the underlying transition or evidence identity.

## Completeness

A transition reports unavailable objects, unsupported modes, unmerged entries, omitted paths, truncated history, and provisional-state capture failures. No change set may claim complete absence outside its recorded scope.
