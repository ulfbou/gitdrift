# Gitdrift documentation

Gitdrift is a DX-first repository evolution forensics tool. It reconstructs how repository states, files, fragments, concepts, and obligations change across Git history, then produces evidence-complete cases for human and AI judgment.

## Current documentation baseline

This baseline establishes the product and architecture before implementation begins:

- [Product vision](vision/product-vision.md)
- [Layered analysis architecture](architecture/layered-analysis-model.md)
- [Profiles and composition](architecture/profiles-and-composition.md)
- [Evidence before judgment](decisions/ADR-001-evidence-before-judgment.md)
- [Protected master and pull-request governance](decisions/ADR-002-protected-master-and-pr-governance.md)
- [Repository state model](specifications/repository-state-model.md)
- [Evidence and provenance](specifications/evidence-and-provenance.md)
- [State-awareness-first roadmap](roadmap/state-awareness-first.md)

## Controlling principles

1. Gitdrift reports evidence before judgment.
2. Repository states include commits, branch tips, the index, the working tree, synthetic comparisons, and explicit snapshots.
3. File and concept evolution are first-class; endpoint comparison is only one view.
4. Semantic regression is distinct from ordinary divergence and overlapping change.
5. Every derived claim retains provenance, confidence, limitations, and supporting evidence.
6. Native machine-readable data is canonical; human views are projections of the same evidence.
7. The core remains read-only. Export and transport are downstream concerns.
8. Issues, pull requests, milestones, and forge metadata are outside the initial evidence boundary.

## Status

These documents are an inception baseline. They define vocabulary, boundaries, and the first vertical slice. They intentionally do not freeze the complete CLI, plugin model, forensic algorithms, or DX evidence-export contract.
