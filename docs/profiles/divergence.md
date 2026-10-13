# Divergence profile

## Purpose

The divergence profile compares selected repository histories and states against an explicitly selected controlling state. It extends the shared Gitdrift kernel with multi-ref traversal, alternate-chain correspondence, semantic divergence, and candidate gold-nugget classification.

`Dx.Domain` is the first acceptance corpus for this profile. It is not a runtime dependency.

## Inputs

A divergence request declares:

```text
repository identity
controlling-state selection
candidate-ref selection
local and remote ref policy
capture point
history traversal policy
merge-base policy
patch-correspondence options
artifact and subject scope
extractors
obligation set
case-selection policy
```

No default branch name, newest tip, longest history, or most recently changed state becomes controlling authority implicitly.

## Captured states and refs

Every selected ref is captured as both a mutable locator and an immutable tip. The result records refs excluded by policy, refs that failed to resolve, and whether selected-ref enumeration is complete.

The controlling state may be a commit, captured branch tip, or explicit snapshot supported by the request. Candidate refs do not gain authority by being ahead, unique, active, or named as releases or features.

## Graph analysis

The profile records reachability, common ancestry, selected merge bases, parent-specific merge transitions, and configured history modes. More than one merge base and unresolved fork-point evidence remain explicit.

Simplified history may support navigation or candidate selection. It may not silently control regression localization or repository-wide absence claims.

## Alternate-chain analysis

Alternate chains are compared from declared or mechanically selected common ancestry under [alternate-chain correspondence](../specifications/alternate-chain-correspondence.md). Commit correspondence, patch equivalence, artifact correspondence, and semantic correspondence remain separate claims with separate evidence and confidence.

Unmatched commits or transitions remain evidence. They are not automatically valuable, harmful, or irrelevant.

## Semantic comparison

For each selected subject, the profile distinguishes ordinary graph divergence, overlapping change, semantic divergence, semantic regression, convergence, and unresolved divergence.

Obligations are evaluated independently at the controlling and candidate states. A candidate state may be equivalent, stronger, weaker, contradictory, superseded, historical-only, or unresolved relative to controlling obligations and facts.

## Gold-nugget selection

A candidate gold nugget is a semantically relevant fact present in a candidate state, absent from the controlling state, and not already represented there equivalently or more strongly.

The profile classifies candidates according to [gold-nugget classification](../specifications/gold-nugget-classification.md). Unique commits, files, or wording are selectors for examination, not proof of a nugget.

## Cases

Cases may be created for:

- possible semantic regression relative to controlling obligations;
- contradictory authority or representation;
- unresolved correspondence or supersession;
- candidate nuggets;
- convergence with distinct provenance;
- semantic facts surviving only on alternate histories; and
- incomplete evidence preventing judgment.

## Completeness

Completeness is declared independently for selected refs, graph traversal, merge-base resolution, alternate-chain correspondence, artifact coverage, semantic extraction, obligation coverage, and counterevidence search.

## Output

The result extends the native investigation with captured refs, reachability, merge bases, alternate chains, correspondence records, divergence classifications, candidate nuggets, cases, and completeness. Native JSON remains canonical.

## Exclusions

The profile does not infer authority from forge metadata, mutate branches, integrate commits, recover content automatically, or finalize semantic truth without the configured evidence and judgment prerequisites.
