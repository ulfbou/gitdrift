# Gitdrift 0.1 obligation matrix

## Purpose

This matrix is the controlling trace from Gitdrift 0.1 obligations to implementation surfaces, executable evidence, and release gates. An obligation is not complete because a document describes it. Mandatory obligations require passing executable evidence for the exact release candidate.

## Status vocabulary

- **Mandatory**: required for Gitdrift 0.1 release.
- **Conditional**: required when the declared platform, artifact, state, or capability is supported or selected.
- **Deferred**: preserved as an architectural constraint but not implemented in 0.1.

## Matrix

| ID | Obligation | Applicability | Implementation surface | Required evidence | Release gate |
|---|---|---|---|---|---|
| GD01-001 | Capture `HEAD` by immutable commit and tree identity. | Mandatory | Repository reader and state capture | Unit and Git-adapter conformance tests | G2, G4 |
| GD01-002 | Capture optional upstream as mutable locator plus immutable tip without implicit fetch or integration. | Conditional | Ref resolver and state capture | Upstream acceptance scenarios and mutation sentinel | G2, G4 |
| GD01-003 | Capture the index reproducibly, including base, stages, modes, objects, manifest, and limitations. | Mandatory | Provisional-state capture | Index fixtures, race tests, conformance tests | G2, G4 |
| GD01-004 | Capture the working tree reproducibly under explicit untracked and ignored-file policies. | Mandatory | Provisional-state capture | Worktree policy fixtures, race tests, conformance tests | G2, G4 |
| GD01-005 | Detect relevant state mutation during provisional capture. | Mandatory | Capture adapter | Mutation-during-capture acceptance test | G2, G4 |
| GD01-006 | Preserve unsupported, binary, unreadable, unmerged, symlink, submodule, and oversized evidence truthfully. | Conditional | Git adapter, evidence model, diagnostics | Adversarial and partial-analysis tests | G4, G6 |
| GD01-007 | Produce the required state-comparison matrix without implying unsupported ancestry. | Mandatory | State-awareness profile | Matrix unit tests and profile acceptance tests | G3, G4 |
| GD01-008 | Preserve exact raw change evidence and explicit diff configuration. | Mandatory | Transition and change-set layer | Git adapter conformance and golden evidence | G3, G4 |
| GD01-009 | Keep paths as locations rather than durable artifact identity. | Mandatory | Domain model and identity scheme | Identity property tests | G3, G5 |
| GD01-010 | Implement versioned Markdown section extraction. | Mandatory | Extractor adapter | Extractor conformance and malformed-input tests | G3, G4 |
| GD01-011 | Implement versioned Python symbol extraction. | Mandatory | Extractor adapter | Extractor conformance and malformed-input tests | G3, G4 |
| GD01-012 | Preserve exact evidence when no semantic extractor supports an artifact. | Mandatory | Evidence model and profile orchestration | Partial-extractor and unsupported-artifact scenarios | G4, G6 |
| GD01-013 | Retain producer, version, inputs, method, derivation class, confidence, and limitations on derived facts. | Mandatory | Fact model and serializers | Schema validation, reference tests, goldens | G3, G5 |
| GD01-014 | Evaluate only explicit or accepted repository-local obligations with authority and applicability data. | Mandatory | Obligation loader and evaluator | Evaluator unit tests and profile scenarios | G3, G4 |
| GD01-015 | Do not promote changed paths, churn, overlap, deletion, or similarity into regression verdicts. | Mandatory | Evaluators, case builder, policies | Negative tests and ambiguous-change scenarios | G4, G6 |
| GD01-016 | Represent unresolved authority, equivalence, supersession, or incomplete evidence as unresolved. | Mandatory | Evaluation and case model | Ambiguous-equivalence fixtures | G4, G6 |
| GD01-017 | Construct cases with observations, interpretations, obligations, assessments, alternatives, counterevidence, unknowns, completeness, reproduction, and evidence inventory. | Mandatory | Case builder | Case-model unit tests, schema validation, goldens | G3, G4, G5 |
| GD01-018 | Make native JSON the canonical serialized investigation. | Mandatory | Native serializer | Schema and golden-artifact tests | G3, G5 |
| GD01-019 | Version the native schema independently from the package. | Mandatory | Schema package and capability discovery | Compatibility tests | G3, G5 |
| GD01-020 | Ensure every native reference resolves or identifies retrievable evidence explicitly. | Mandatory | Identity, serializer, validator | Automated reference-closure validation | G3, G5 |
| GD01-021 | Keep evidence classes distinct through every transformation. | Mandatory | Domain model and serializer | Schema constraints and class-preservation tests | G3, G5 |
| GD01-022 | Declare completeness independently by relevant dimension and never strengthen partial child coverage. | Mandatory | Result aggregation and case model | Completeness property and mutation tests | G3, G4, G5 |
| GD01-023 | Separate analytical findings from execution diagnostics and process failure. | Mandatory | Diagnostics and CLI adapter | Diagnostic mapping and exit-status tests | G3, G6 |
| GD01-024 | Deliver complete artifact bytes to the selected sink or report sink failure. | Mandatory | Output-sink adapter | Sink conformance and interrupted-write tests | G3, G6 |
| GD01-025 | Keep the public library API typed, use-case-oriented, read-only, and independent of argparse and standard streams. | Mandatory | Public API | API contract tests and import inspection | G1, G3 |
| GD01-026 | Keep the CLI a thin adapter over the same application contracts. | Mandatory | CLI adapter | CLI-to-library equivalence tests | G1, G3 |
| GD01-027 | Report implemented capabilities only. | Mandatory | Capability discovery | Discovery schema and negative capability tests | G1, G3 |
| GD01-028 | Perform no mutation of refs, index, worktree, configuration, hooks, or hosted metadata. | Mandatory | All acquisition and analysis paths | Before/after mutation sentinels for every profile scenario | G4, G7 |
| GD01-029 | Produce semantically identical results for identical immutable inputs, configuration, versions, and capabilities. | Mandatory | Identity, ordering, serialization, orchestration | Repeated-run determinism suite | G5 |
| GD01-030 | Record exact reproduction inputs, including states, traversal, diff, extractors, obligations, schema, configuration, capabilities, and budgets. | Mandatory | Analysis manifest | Golden and reproduction tests | G4, G5 |
| GD01-031 | Bound resource use and represent truncation or exhaustion without false completeness. | Mandatory | Resource policy and diagnostics | Budget-exhaustion and partial-result tests | G6 |
| GD01-032 | Treat repository content and configuration as untrusted input and never execute embedded instructions. | Mandatory | Git, parser, extractor, and configuration adapters | Adversarial security tests | G6 |
| GD01-033 | Validate the state-awareness profile against reproducible synthetic fixtures and a pinned `dx-artifacts` corpus. | Mandatory | Acceptance harness | Profile and corpus evidence bundle | G4 |
| GD01-034 | Support every declared platform consistently or report explicit capability limitations. | Conditional | Packaging and adapters | Platform matrix and conformance results | G1, G7 |
| GD01-035 | Preserve compatibility rules for unknown fields, enum values, schema versions, and migrations. | Mandatory | Native reader, validator, compatibility layer | Compatibility suite | G5 |
| GD01-036 | Exclude forge integration, AI assessment, SARIF, DX export, repository mutation, automatic fixes, and composite verdict scoring from 0.1 capability claims. | Mandatory | Capability discovery, CLI, docs | Negative capability tests and release review | G1, G3, G8 |
| GD01-037 | Preserve future divergence, lineage, and forensics contracts without claiming their implementation. | Mandatory | Shared model boundaries and capability discovery | Architecture conformance and negative capability tests | G3, G8 |

## Evidence record requirements

Evidence satisfying a mandatory obligation records:

- obligation ID;
- exact candidate commit and source-tree identity;
- test, fixture, or harness identity;
- request and configuration identity;
- producer and relevant dependency versions;
- native schema version where applicable;
- pass, fail, partial, unavailable, or not-applicable result;
- diagnostics and limitations;
- generated artifact identities or digests where applicable.

A prose claim, unchecked box, mutable branch name, or successful unrelated test does not satisfy an obligation.

## Change control

A change to a mandatory obligation requires an explicit documentation change reviewed in the same PR or an earlier merged PR. Removal, weakening, deferral, or contradiction requires accepted authority and must update the acceptance checklist, this matrix, affected specifications, tests, and release gates together.
