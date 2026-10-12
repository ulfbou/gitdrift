# Profiles and composition

## Purpose

Profiles select traversal scope, analysis depth, case-selection rules, and presentation without creating separate domain models.

The three planned profiles share the same repository evidence, transition, lineage, semantic fact, obligation, case, and serialization components.

## State-awareness profile

This is the first vertical slice and is proven against `dx-artifacts`.

Typical states:

```text
HEAD
configured upstream tip
INDEX
WORKTREE
```

Primary questions:

- What analyzable states exist?
- What immutable objects or captured snapshots identify them?
- What changed between the relevant state pairs?
- Which paths, sections, and supported symbols overlap?
- Which declared obligations are affected?
- What is unique, equivalent, contradictory, or unresolved?
- What evidence is missing for final judgment?

The profile must remain useful in a predominantly linear commit history.

## Divergence profile

This profile extends the same kernel for `Dx.Domain` and other multi-branch repositories.

Additional capabilities:

- enumerate selected local and remote refs;
- identify merge bases and reachability relationships;
- compare alternate commit and artifact chains;
- detect patch-equivalent or semantically equivalent evolution;
- trace branch-specific facts and obligations;
- classify candidate gold nuggets;
- distinguish convergence from unresolved divergence.

A unique commit is not automatically valuable, and a valuable fact need not correspond to a unique commit.

## Forensics profile

This profile increases historical depth and structural inference.

Additional capabilities:

- full artifact evolution graphs;
- region, symbol, fragment, and concept lineages;
- adjacent and cumulative comparison windows;
- accretion analysis for frequently changed files;
- one-to-many and many-to-one lineage candidates;
- semantic fragmentation, residue, loss, duplication, and divergence;
- restoration versus independent reintroduction.

The forensics profile remains centered on repository artifacts, semantic obligations, and regression judgments. Generalized organizational analytics and cross-repository research mining are outside its boundary.

## Composition rule

Profiles orchestrate capabilities through application services:

```text
request
  -> state acquisition
  -> transition selection
  -> structural analysis
  -> supported semantic extraction
  -> obligation evaluation
  -> case construction
  -> schema-validated result
```

A profile may stop after any layer and declare the omitted layers in its completeness record.

## Why profiles rather than sibling products

The perspectives differ, but their reusable components and evidence contracts are the same. Splitting them now would duplicate identities, transition semantics, provenance, confidence, and serialization rules.

A package or repository should split only when independent versioning, dependencies, release cadence, or runtime boundaries are demonstrated by implementation evidence.

## Runtime and product boundaries

Gitdrift does not consume `dx-artifacts` or `Dx.Domain` as runtime submodules.

- `dx-artifacts` is an independent Python carrier-format library product.
- `Dx.Domain` is an independent .NET 10 product.
- both are analyzed repositories and useful acceptance corpora;
- future interoperability occurs through language-neutral schemas, native JSON, SARIF, subprocess boundaries, or optional DX evidence carriers.

Cross-product reuse occurs through stable data contracts, not shared implementation.
