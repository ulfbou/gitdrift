# Product vision

## Purpose

Gitdrift helps humans and AI determine where repository knowledge evolved, diverged, weakened, disappeared, or reappeared.

Its central question is:

> At which transition, on which history path or repository state, did an established semantic obligation first cease to hold?

Gitdrift does not treat a large diff, a deleted file, or a divergent branch as proof of regression. It compiles repository evidence into judgment-ready cases containing supporting evidence, counterevidence, uncertainty, and exact reproduction boundaries.

## Product identity

Gitdrift is a Python library product with a thin DX-first CLI adapter.

The library provides reusable capabilities for:

- repository-state acquisition;
- transition and diff construction;
- file, region, symbol, fragment, and concept lineage;
- semantic fact extraction;
- obligation evaluation;
- regression and divergence case construction;
- evidence serialization and validation.

The CLI composes those capabilities into explicit analysis profiles. Structured output is the product; human-readable output is a projection.

## Foundational use cases

### State awareness

The initial use case is `dx-artifacts`, whose history may be predominantly linear while meaningful candidate states coexist at `HEAD`, an upstream tip, the index, and the working tree.

The tool must reveal:

- which states exist;
- which comparisons are meaningful;
- what changed structurally and semantically;
- which declared obligations may be affected;
- what is unique, overlapping, contradictory, or unresolved;
- what evidence is insufficient for a regression judgment.

### Branch archaeology and divergence

`Dx.Domain` provides the motivating multi-branch case. The tool must compare branch histories against a controlling state and locate semantic facts that are absent from, weaker than, contradictory to, or stronger than the release line.

A candidate gold nugget is a semantically relevant fact present in a candidate state but absent from the controlling state and not already represented there in an equivalent or stronger form.

### Repository evolution forensics

A file may grow through many small edits into a mixed-purpose blob. A coherent artifact may also split across documents, code, tests, configuration, and release gates. Gitdrift must therefore reconstruct artifact and concept lineages rather than assuming that a path is a stable identity.

Forensic depth includes:

- adjacent and cumulative transition analysis;
- accretion windows;
- one-to-many and many-to-one lineage candidates;
- restoration versus independent reintroduction;
- semantic dispersal, duplication, residue, and loss.

## Product boundaries

Gitdrift initially consumes only repository-local evidence:

- Git objects, refs, trees, blobs, and topology;
- index and working-tree state;
- parent-to-child diffs;
- repository-local configuration, documentation, code, tests, and gates;
- explicitly declared obligations and authorities.

The initial product excludes:

- issues, pull requests, milestones, labels, reviews, and project boards;
- automatic repository mutation, rebasing, patch application, or repair;
- organizational or developer-performance analysis;
- autonomous claims of intent;
- DX carrier production as the primary analysis output.

Forge metadata may later enrich explanations, but core findings must remain reproducible without it.

## Success criterion

Gitdrift succeeds when every conclusion can be traversed in both directions:

```text
judgment
  -> assessment
  -> obligation
  -> semantic fact delta
  -> artifact transition
  -> snapshots, patches, and Git objects
```

and:

```text
Git transition
  -> changed artifacts
  -> changed facts
  -> affected obligations
  -> cases
  -> judgment or bounded unresolved question
```

## Long-term promise

Gitdrift will not promise autonomous semantic truth. It will promise that no regression judgment is presented without its history, active obligation, supporting evidence, counterevidence, uncertainty, and exact reproduction boundary.
