# History traversal

## Purpose

This specification defines history traversal modes, ancestry evidence, merge-base selection, reachability, and parent-specific merge transitions.

## Traversal modes

### Full ancestry

Traverses all selected parent edges within the declared boundary. It preserves merges and alternate ancestry relevant to the investigation.

### First parent

Traverses the first-parent chain of a selected tip. It answers when a state entered that delivered branch history but does not establish the original source of every change.

### Simplified history

Uses path or content simplification to reduce visible history. It is suitable for navigation and candidate selection only when its omissions are recorded.

### Lineage-selected history

Traverses states selected by an artifact, fragment, concept, or obligation lineage policy. Selection criteria and omitted transitions remain explicit.

## Traversal record

Every traversal records:

```text
start states
boundary states
history mode
parent policy
path or subject filters
ordering
limits
rename and copy options
ignored-revision policy
visited commits and edges
omitted or truncated scope
```

## Merge bases

Merge-base selection records all best common ancestors returned by the configured method. Multiple merge bases are valid evidence and must not be collapsed silently into one arbitrary baseline.

If a synthetic merge base is later constructed for an algorithm, it is identified as synthetic and does not become a repository commit.

## Fork-point heuristic

Fork-point may use reflog or other heuristic evidence to propose an earlier branch point. It is classified as heuristic, records its method and unavailable evidence, and never silently replaces merge-base evidence.

## Reachability

Reachability records whether one captured commit is equal to, an ancestor of, a descendant of, or divergent from another under the selected commit graph. Unknown or unavailable objects produce unresolved reachability rather than assumed divergence.

## Parent-specific merges

A merge commit yields one parent-to-child transition per parent. Findings identify the relevant parent number and parent identity. A fact preserved relative to one parent but lost relative to another remains represented as two distinct assessments.

## Regression constraint

No semantic regression conclusion may rely invisibly on simplified path history. Regression localization declares the traversal mode, parent policy, coverage, and the transitions actually evaluated.

## Completeness

Traversal completeness reports shallow boundaries, missing objects, excluded refs, filters, ignored revisions, traversal limits, and unsupported history modes. A complete traversal within a narrow path scope is not repository-wide completeness.
