# File-lineage profile

## Purpose

The file-lineage profile performs longitudinal analysis of selected artifacts and semantic subjects across commits, branches, merges, renames, splits, restorations, and provisional terminal states.

It extends the shared Gitdrift kernel without treating a workspace path as durable identity or replacing raw repository evidence with inferred lineage.

## Inputs

A request declares:

```text
repository identity
selected paths, artifacts, fragments, concepts, or obligations
start and end states
selected refs and history paths
traversal and parent policy
rename and copy options
extractors
obligation set
comparison windows
case-selection policy
```

Every mutable ref is captured immutably. Subject selection and traversal limits are preserved in reproduction metadata and completeness.

## Longitudinal analysis

The profile constructs parent-specific transitions and exact artifact snapshots over the selected history. It may relate instances through creation, modification, rename, copy, move, deletion, restoration, replacement, split, merge, and supersession candidates.

Deterministic Git relationships and inferred structural or semantic relationships remain distinguishable. Unresolved lineage is retained rather than forced into a single chain.

## Subject granularities

A selected subject may be:

- a path at a captured state;
- an artifact identity or lineage;
- a Markdown section or bounded region;
- a code symbol;
- a requirement or semantic fact;
- a concept representation; or
- an obligation.

Analysis may expand from a selected path to related instances, but the expansion method and exclusions remain explicit.

## Fact and obligation evolution

For each selected transition, supported extractors produce attributed facts. Fact deltas classify additions, removals, modifications, movement, duplication, strengthening, weakening, contradiction, and supersession without replacing raw patches.

Obligations are evaluated at the relevant states. A large rewrite may preserve all obligations, while a small normative change may weaken one.

## Regression localization

The profile may identify the last satisfied state and first violating transition for an active obligation. It distinguishes origin, integration, first observation on a selected branch, affected refs, restoration, and independent reintroduction where evidence supports those relations.

Regression localization requires explicit traversal, authority, counterevidence, and completeness. An unresolved lineage or supersession question prevents deterministic finalization when relevant.

## Cases

The profile may produce cases for:

- possible regression across a transition;
- loss during rename, split, merge, or replacement;
- restoration or independent reintroduction;
- fact survival on an alternate branch;
- conflicting lineage candidates;
- equivalent evolution through different histories; and
- insufficient evidence for localization.

## Output

The native investigation adds artifact and fragment lineages, fact deltas, obligation-evaluation chains, localization records, affected refs, cases, and completeness. Raw snapshots, patches, and parent relationships remain traceable from every derived conclusion.

## Exclusions

The profile does not mutate history, recover content automatically, select authority from branch naming, or treat path similarity, churn, file size, or change magnitude as proof of regression.
