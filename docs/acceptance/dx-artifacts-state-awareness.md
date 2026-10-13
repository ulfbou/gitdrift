# dx-artifacts state-awareness acceptance

## Purpose

This document defines evidence-based acceptance scenarios for the state-awareness profile using `dx-artifacts` as an independent acceptance corpus. Fixtures use immutable repository identities or mechanically created states and do not embed mutable claims about the current external repository.

## Fixture requirements

Each scenario declares:

```text
repository source and immutable base
captured refs
index construction
working-tree construction
untracked and ignored-file policies
obligation set
expected comparisons
expected facts and cases
expected completeness
mutation sentinel
```

Expected results refer to immutable identities or fixture-relative symbolic names resolved by setup.

## Scenarios

### Aligned clean repository

`HEAD`, index, and working tree are content-equivalent and the optional upstream is either equal or explicitly absent. The result is schema-valid, records applicable no-change comparisons, and performs no mutation.

### Local branch behind upstream

The upstream tip descends from `HEAD`. Gitdrift captures both tips, reports the relationship and comparison, and does not fetch-integrate, fast-forward, merge, or rebase.

### Staged architecture migration

The index differs from `HEAD` across architecture, documentation, tests, or gates. The profile isolates `HEAD -> INDEX`, extracts supported facts, evaluates declared obligations, and preserves unsupported artifacts as exact evidence.

### Unstaged changes

The worktree differs from the index. The profile distinguishes `INDEX -> WORKTREE` from `HEAD -> WORKTREE` and applies the declared untracked and ignored-file policies.

### Simultaneous upstream and staged candidates

Both upstream and index differ from `HEAD`. The profile compares each independently with `HEAD` and, when requested, compares upstream with index without integrating either candidate.

### Staged and working-tree divergence

The index and working tree contain different changes affecting the same path, fact, or obligation. The result preserves both provisional states and creates an unresolved or contradictory case only where evidence supports it.

### Partial extractor support

At least one selected artifact kind lacks a semantic extractor. Exact bytes and raw changes remain evidence, semantic extraction is partial, and absence claims are bounded accordingly.

### Ambiguous semantic equivalence

Two representations may satisfy the same obligation but deterministic equivalence is unavailable. The profile records supporting evidence, counterevidence, limitations, and a bounded unresolved question rather than finalizing regression.

### Unsupported artifact preserved

A changed unsupported or binary artifact remains addressable by exact content identity and path metadata. It is not dropped because semantic extraction is unavailable.

### Zero repository mutation

Before and after identities for refs, `HEAD`, index, working-tree files, and relevant configuration are equal. Explicit output artifacts are excluded from the analyzed repository or written only to the configured sink.

## Acceptance rule

A scenario passes only when native output validates, required comparisons are present, evidence and derived claims remain distinguishable, completeness is accurate, and the mutation sentinel passes.
