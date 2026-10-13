# Dx.Domain divergence acceptance

## Purpose

This document defines the acceptance corpus for the divergence profile using reproducible `Dx.Domain` repository states. It does not embed mutable claims about current hosted branches.

## Fixture contract

Each fixture declares:

```text
repository identity and immutable object set
controlling state
selected local and remote refs
captured immutable tips
traversal and merge-base policy
extractors and obligation set
expected correspondence and classifications
completeness expectations
mutation sentinel
```

## Scenarios

### Many branches

Selected refs resolve to multiple equal, ancestor, descendant, and divergent tips. The result deduplicates immutable tips without losing their locators and reports selected-ref completeness.

### Partial convergence

Two branches share some semantically equivalent changes while retaining unmatched transitions and unresolved facts. Convergence does not erase distinct provenance.

### Release-line baseline

An explicitly selected release-line state acts as the controlling comparison boundary. No authority is inferred merely from the ref name.

### Patch-equivalent history

Distinct commits carry equivalent normalized patches. Gitdrift records patch equivalence separately from commit identity and semantic equivalence.

### Facts surviving on abandoned branches

A relevant fact is present on a selected alternate history but absent from controlling state. Activity, age, or abandonment does not determine its classification.

### Contradictory candidates

A candidate fact conflicts with an active controlling obligation. The result records both sides, authority, counterevidence, and unresolved supersession when applicable.

### Equivalent stronger representation

The controlling state contains an equivalent or stronger representation of a candidate fact. The candidate is not classified as a gold nugget merely because its wording or commit is unique.

### Gold nugget versus historical residue

One candidate satisfies the nugget rule while another is superseded or historical-only. The classifications remain evidence-backed and independently reproducible.

## Safety and read-only acceptance

The analysis performs no checkout, merge, rebase, reset, ref update, index update, working-tree modification, hosted-service mutation, or automatic recovery. Before and after repository sentinels remain equal except for an explicit output sink outside analyzed state.

## Acceptance rule

A scenario passes only when native output validates; refs and tips are captured immutably; traversal and correspondence methods are explicit; semantic and nugget classifications cite evidence and counterevidence; completeness is accurate; and the mutation sentinel passes.
