# Gitdrift documentation

Gitdrift is a DX-first repository evolution forensics tool. It reconstructs how repository states, artifacts, fragments, concepts, and obligations change across Git history, then produces evidence-complete cases for human and AI judgment.

## Current documentation baseline

### Product and architecture

- [Product vision](vision/product-vision.md)
- [Layered analysis architecture](architecture/layered-analysis-model.md)
- [Profiles and composition](architecture/profiles-and-composition.md)
- [Domain model](architecture/domain-model.md)
- [Library and adapter boundaries](architecture/library-and-adapter-boundaries.md)

### Decisions

- [Evidence before judgment](decisions/ADR-001-evidence-before-judgment.md)
- [Protected master and pull-request governance](decisions/ADR-002-protected-master-and-pr-governance.md)
- [Native JSON is canonical](decisions/ADR-003-native-json-is-canonical.md)
- [Profiles over product forks](decisions/ADR-004-profiles-over-product-forks.md)
- [Library core and thin CLI](decisions/ADR-005-library-core-and-thin-cli.md)
- [External products are evidence boundaries](decisions/ADR-006-external-products-are-evidence-boundaries.md)

### Core and state-awareness specifications

- [Repository state model](specifications/repository-state-model.md)
- [Provisional state capture](specifications/provisional-state-capture.md)
- [Transition and change set](specifications/transition-and-change-set.md)
- [State comparison matrix](specifications/state-comparison-matrix.md)
- [Evidence and provenance](specifications/evidence-and-provenance.md)
- [Obligation and authority](specifications/obligation-and-authority.md)
- [Case model](specifications/case-model.md)
- [Native investigation model](specifications/native-investigation-model.md)
- [Capability discovery](specifications/capability-discovery.md)
- [Library API](specifications/library-api.md)
- [CLI contract](specifications/cli-contract.md)

### Divergence specifications

- [Ref selection and controlling state](specifications/ref-selection-and-controlling-state.md)
- [History traversal](specifications/history-traversal.md)
- [Alternate-chain correspondence](specifications/alternate-chain-correspondence.md)
- [Semantic divergence](specifications/semantic-divergence.md)
- [Gold-nugget classification](specifications/gold-nugget-classification.md)

### Profiles and acceptance

- [State awareness](profiles/state-awareness.md)
- [Divergence](profiles/divergence.md)
- [dx-artifacts state-awareness acceptance](acceptance/dx-artifacts-state-awareness.md)
- [Dx.Domain divergence acceptance](acceptance/dx-domain-divergence.md)
- [State-awareness-first roadmap](roadmap/state-awareness-first.md)

## Controlling principles

1. Gitdrift reports evidence before judgment.
2. Mutable refs are locators; captured immutable targets control analysis.
3. A controlling state is selected explicitly and gains no authority from its branch name, age, or distance.
4. File and concept evolution are first-class; endpoint comparison is only one view.
5. Ordinary divergence, overlapping change, semantic divergence, and semantic regression remain distinct.
6. Every derived claim retains provenance, confidence, limitations, and supporting evidence.
7. Native Gitdrift JSON is canonical; human views and interoperability formats are projections.
8. The core remains read-only. Export and transport are downstream concerns.
9. Deterministic, heuristic, AI-assisted, and human-supplied claims remain distinguishable.
10. External products are analyzed evidence boundaries, not Gitdrift runtime dependencies.

## Status

The current contracts define the semantic kernel, state-awareness and divergence profiles, native investigation boundary, and library-to-adapter separation. File-lineage depth, forensic inference, judgment policies, hosted integrations, and DX evidence export remain later work.
