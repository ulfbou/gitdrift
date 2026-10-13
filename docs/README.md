# Gitdrift documentation

Gitdrift is a DX-first repository evolution forensics tool. It reconstructs how repository states, files, fragments, concepts, and obligations change across Git history, then produces evidence-complete cases for human and AI judgment.

## Current documentation baseline

### Product and architecture

- [Product vision](vision/product-vision.md)
- [Layered analysis architecture](architecture/layered-analysis-model.md)
- [Profiles and composition](architecture/profiles-and-composition.md)
- architecture/domain-model.md
- architecture/library-and-adapter-boundaries.md

### Decisions

- [Evidence before judgment](decisions/ADR-001-evidence-before-judgment.md)
- [Protected master and pull-request governance](decisions/ADR-002-protected-master-and-pr-governance.md)
- decisions/ADR-003-native-json-is-canonical.md
- decisions/ADR-004-profiles-over-product-forks.md
- decisions/ADR-005-library-core-and-thin-cli.md
- decisions/ADR-006-external-products-are-evidence-boundaries.md

### Core specifications

- [Repository state model](specifications/repository-state-model.md)
- specifications/provisional-state-capture.md
- specifications/transition-and-change-set.md
- specifications/state-comparison-matrix.md
- [Evidence and provenance](specifications/evidence-and-provenance.md)
- specifications/obligation-and-authority.md
- specifications/case-model.md
- specifications/native-investigation-model.md
- specifications/capability-discovery.md
- specifications/library-api.md
- specifications/cli-contract.md

### Profiles and acceptance

- profiles/state-awareness.md
- acceptance/dx-artifacts-state-awareness.md
- [State-awareness-first roadmap](roadmap/state-awareness-first.md)

## Controlling principles

1. Gitdrift reports evidence before judgment.
2. Repository states include commits, branch tips, the index, the working tree, synthetic comparisons, and explicit snapshots.
3. File and concept evolution are first-class; endpoint comparison is only one view.
4. Semantic regression is distinct from ordinary divergence and overlapping change.
5. Every derived claim retains provenance, confidence, limitations, and supporting evidence.
6. Native Gitdrift JSON is canonical; human views and interoperability formats are projections.
7. The core remains read-only. Export and transport are downstream concerns.
8. Issues, pull requests, milestones, and forge metadata are outside the initial evidence boundary.
9. Identity is distinct from mutable location, display order, and ref names.
10. Deterministic, heuristic, AI-assisted, and human-supplied claims remain distinguishable.
11. The Python library owns product semantics; the CLI is a replaceable adapter.
12. External products are analyzed evidence boundaries, not Gitdrift runtime dependencies.

## Status

The current contracts define the semantic kernel, state-awareness profile, native investigation boundary, and initial library-to-adapter separation. They intentionally do not freeze divergence algorithms, forensic inference, plugin SDKs, hosted integrations, or DX evidence export.
