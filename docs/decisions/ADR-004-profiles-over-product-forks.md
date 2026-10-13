# ADR-004: Profiles over product forks

## Status

Accepted.

## Context

State awareness, branch divergence, and repository evolution forensics differ in traversal scope, historical depth, structural inference, case selection, and presentation. They nevertheless depend on the same identities and contracts for repository states, transitions, artifacts, facts, obligations, evidence, cases, completeness, and serialization.

Creating separate products now would duplicate these semantics before implementation provides evidence for independent lifecycle boundaries.

## Decision

Gitdrift will implement state awareness, divergence, and forensics as profiles over one semantic-analysis kernel.

A profile selects and orchestrates capabilities through application services. It may configure traversal, capture, extractors, obligation evaluation, case selection, completeness, and output projection. It may not bypass layer contracts or redefine shared entity meaning.

The initial sequence is:

1. state awareness proves committed and provisional state analysis;
2. divergence extends the kernel to multiple refs and alternate chains;
3. forensics extends historical and lineage depth.

A package or repository may split only when implementation evidence demonstrates a boundary requiring independent versioning, dependencies, release cadence, runtime, scaling, or security controls.

## Consequences

### Positive

- profiles share evidence and provenance semantics;
- state awareness builds reusable kernel capabilities rather than a disposable feature;
- divergence and forensics can deepen analysis without replacing identities;
- native investigations remain composable across profiles.

### Costs

- the shared contracts require early discipline;
- optional capabilities must declare availability and completeness;
- profile orchestration must avoid becoming an untyped universal analysis function.

## Rejected alternatives

### Separate state-awareness product

Rejected because committed, index, and working-tree states are part of the same repository-state model required by later profiles.

### Separate divergence product

Rejected because ref selection and alternate-chain analysis reuse transitions, facts, obligations, and cases.

### Separate generalized forensics product now

Rejected because the intended forensic work remains centered on repository artifacts, semantic obligations, and regression judgments. General organizational or host forensics remains outside Gitdrift.
