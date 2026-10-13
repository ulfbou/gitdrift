# Gitdrift documentation

Gitdrift is a DX-first repository evolution forensics tool. It reconstructs how repository states, artifacts, fragments, concepts, and obligations change across Git history, then produces evidence-complete cases for human and AI judgment.

## Documentation map

### Foundation

- [Glossary](glossary.md)
- [Product vision](vision/product-vision.md)
- [Product principles](vision/product-principles.md)
- [Non goals](vision/non-goals.md)

### Architecture

- [Domain model](architecture/domain-model.md)
- [Layered analysis model](architecture/layered-analysis-model.md)
- [Library and adapter boundaries](architecture/library-and-adapter-boundaries.md)
- [Repository architecture for 0.1](architecture/repository-architecture-0.1.md)
- [Profiles and composition](architecture/profiles-and-composition.md)
- [Quality attributes](architecture/quality-attributes.md)
- [Trust boundaries](architecture/trust-boundaries.md)

### Decisions

- [ADR-001: Evidence before judgment](decisions/ADR-001-evidence-before-judgment.md)
- [ADR-002: Protected master and pr governance](decisions/ADR-002-protected-master-and-pr-governance.md)
- [ADR-003: Native json is canonical](decisions/ADR-003-native-json-is-canonical.md)
- [ADR-004: Profiles over product forks](decisions/ADR-004-profiles-over-product-forks.md)
- [ADR-005: Library core and thin cli](decisions/ADR-005-library-core-and-thin-cli.md)
- [ADR-006: External products are evidence boundaries](decisions/ADR-006-external-products-are-evidence-boundaries.md)

### Profiles

- [Divergence](profiles/divergence.md)
- [File lineage](profiles/file-lineage.md)
- [Repository evolution forensics](profiles/repository-evolution-forensics.md)
- [State awareness](profiles/state-awareness.md)

### Specifications

- [Accretion analysis](specifications/accretion-analysis.md)
- [Alternate chain correspondence](specifications/alternate-chain-correspondence.md)
- [Analysis pressure and purity](specifications/analysis-pressure-and-purity.md)
- [Artifact lineage](specifications/artifact-lineage.md)
- [Cache and derived data](specifications/cache-and-derived-data.md)
- [Capability discovery](specifications/capability-discovery.md)
- [Case model](specifications/case-model.md)
- [Cli contract](specifications/cli-contract.md)
- [Comparison windows](specifications/comparison-windows.md)
- [Cost and resource model](specifications/cost-and-resource-model.md)
- [Evidence and provenance](specifications/evidence-and-provenance.md)
- [Evidence selection and compression](specifications/evidence-selection-and-compression.md)
- [Fact delta](specifications/fact-delta.md)
- [Failure and diagnostic model](specifications/failure-and-diagnostic-model.md)
- [Fragment and concept lineage](specifications/fragment-and-concept-lineage.md)
- [Fragmentation analysis](specifications/fragmentation-analysis.md)
- [Gold nugget classification](specifications/gold-nugget-classification.md)
- [History traversal](specifications/history-traversal.md)
- [Identity and fingerprints](specifications/identity-and-fingerprints.md)
- [Library api](specifications/library-api.md)
- [Mechanical change policy](specifications/mechanical-change-policy.md)
- [Native investigation model](specifications/native-investigation-model.md)
- [Obligation and authority](specifications/obligation-and-authority.md)
- [Provisional state capture](specifications/provisional-state-capture.md)
- [Ref selection and controlling state](specifications/ref-selection-and-controlling-state.md)
- [Regression localization](specifications/regression-localization.md)
- [Repository state model](specifications/repository-state-model.md)
- [Semantic divergence](specifications/semantic-divergence.md)
- [State comparison matrix](specifications/state-comparison-matrix.md)
- [Transition and change set](specifications/transition-and-change-set.md)
- [Versioning and compatibility](specifications/versioning-and-compatibility.md)

### Contributor standards

- [Coding standards](contributors/coding-standards.md)
- [Documentation standards](contributors/documentation-standards.md)
- [Hosted integration validation](contributors/hosted-integration-validation.md)
- [Compatibility and deprecation policy](contributors/compatibility-and-deprecation-policy.md)

### Acceptance and testing

- [Accretion and fragmentation](acceptance/accretion-and-fragmentation.md)
- [Dx-artifacts state awareness](acceptance/dx-artifacts-state-awareness.md)
- [Dx.domain divergence](acceptance/dx-domain-divergence.md)
- [File history regression](acceptance/file-history-regression.md)
- [Acceptance strategy](testing/acceptance-strategy.md)

### Roadmap

- [State awareness first](roadmap/state-awareness-first.md)

### Planned Releases

#### Gitdrift 0.1

- [Gitdrift 0.1 Accept ready checklist](releases/0.1/acceptance-checklist.md)
- [Gitdrift 0.1 Obligation matrix](releases/0.1/obligation-matrix.md)
- [Gitdrift 0.1 Release Gates](releases/0.1/release-gates.md)

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
