# Regression localization

## Purpose

This specification defines how Gitdrift locates where an established obligation first ceased to hold and distinguishes introduction, integration, observation, restoration, and reintroduction.

## Preconditions

Localization requires:

```text
obligation identity and applicable authority
selected history path or graph scope
state evaluations
parent-specific transitions
traversal and parent policy
relevant fact and lineage evidence
counterevidence search
completeness declaration
```

Without these prerequisites, the result remains a localization candidate or unresolved case.

## Last satisfied state

The last satisfied state is the latest evaluated state before the violating boundary on the selected path where the obligation is satisfied or strengthened. Latest is relative to the declared traversal order, not wall-clock recency.

## First violating transition

The first violating transition connects the last satisfied region to a state evaluated as weakened, violated, or contradictory under the configured policy. It records both endpoint identities and, for merges, the relevant parent identity and parent number.

An absent or unresolved evaluation cannot be promoted to violation unless policy, authority, and completeness permit it.

## Origin commit

The origin commit is the earliest supported commit where the relevant violating fact or change was introduced on any analyzed ancestry path. It may differ from the commit where the violation entered a selected branch.

## Integration commit

The integration commit is the commit, often a merge or cherry-pick-equivalent transition, through which the violating state entered the selected delivered history. Correspondence evidence and parent specificity remain explicit.

## First observed branch commit

The first observed branch commit is the first commit on the declared branch traversal where the violating evaluation is visible. It does not necessarily establish origin.

## Affected refs

Affected refs are captured immutable tips whose analyzed states contain the violating evaluation or equivalent violating fact under the declared correspondence method. Mutable ref names are retained as locators.

## Restoration

Restoration occurs when a later state again satisfies the obligation through a supported relation to the earlier satisfied representation or fact. The violating interval remains historical evidence.

## Independent reintroduction

Independent reintroduction occurs when equivalent satisfying behavior or representation appears later without sufficient evidence of restoration lineage. Similar outcome does not erase distinct provenance.

## Confidence and completeness

Every localization record states which elements are deterministic and which are heuristic or unresolved. Completeness covers traversal, selected refs, parent edges, lineage resolution, extraction, obligation evaluation, and counterevidence.

## Safety constraints

Localization never rewrites history, bisects by mutating the analyzed worktree, or infers author intent. Branch names, timestamps, and commit messages may be retained as context but do not establish authority or causality alone.
