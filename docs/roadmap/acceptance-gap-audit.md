# Gitdrift 0.1 acceptance gap audit

## Status

Candidate-state audit for sequencing implementation. This document does not satisfy an acceptance obligation and does not replace executable release evidence.

## Audit basis

The audit compares the current implementation surface with the mandatory obligations in the [0.1 obligation matrix](../releases/0.1/obligation-matrix.md), the [acceptance checklist](../releases/0.1/acceptance-checklist.md), and the [release gates](../releases/0.1/release-gates.md).

Implemented foundations currently include immutable domain records, stable identity, reference-closure validation, truthful capability discovery, repository validation, hosted-governance verification, and read-only immutable `HEAD` capture through a domain-owned repository port and Git adapter.

No analytical profile is acceptance-ready. Capability discovery must continue to report state awareness and all deferred profiles as unavailable until their complete required compositions exist.

## Acceptance gap groups

### Repository acquisition

- Immutable `HEAD` commit and tree capture is implemented as the first bounded part of GD01-001.
- Repository identity remains local-adapter evidence and requires later compatibility treatment before release closure.
- Reproducible index capture is implemented with base identities, complete stage/mode/object entries, deterministic manifests, unmerged-stage preservation, and index-race rejection.
- Optional upstream capture, working-tree capture, broader race policies, and unsupported repository-state handling remain missing.
- Full Git-adapter conformance and mutation-sentinel coverage required by G2 and G4 remain missing.

### Comparisons and exact evidence

- The domain has comparison and raw-change records.
- No adapter constructs `HEAD -> INDEX`, `INDEX -> WORKTREE`, `HEAD -> WORKTREE`, or `HEAD <-> upstream` results.
- Exact snapshot acquisition, diff configuration capture, raw patch evidence, missing-endpoint matrix entries, and comparison completeness remain missing.

### Semantic extraction

- Evidence and fact record foundations exist.
- Markdown section and Python symbol extractors, extractor capability declarations, malformed-input behavior, unsupported-artifact preservation through an executable profile, and extractor conformance remain missing.

### Obligations and cases

- Obligation, evaluation, completeness, and case records exist.
- Obligation loading, authority validation, deterministic evaluation, counterevidence search, unresolved-case construction, and negative verdict tests remain missing.

### Native investigation contract

- The aggregate investigation and reference-closure check exist.
- The accepted JSON Schema resource, canonical serializer, validator adapter, sink contract, complete-byte delivery, golden artifacts, compatibility behavior, and schema-based discovery remain missing.

### Profile and process adapters

- Capability discovery and its CLI command exist.
- The state-awareness request/result contract, profile orchestration, CLI execution path, explicit input manifest, diagnostics mapping, and process exit mapping remain missing.

### Acceptance and release evidence

- The canonical validator covers compilation, unit tests, selected architecture rules, public exports, compatibility aliases, documentation links, and `git diff --check`.
- The validator currently requires the source package to be importable by the environment; fresh-carrier execution needs an explicit installation or source import boundary.
- Packaging, isolated installs, schema validation, property tests, adversarial tests, resource exhaustion, cross-platform evidence, deterministic reruns, the pinned `dx-artifacts` corpus, and G0 through G8 evidence aggregation remain missing.
- Hosted `master` enforcement is a repository-governance boundary, not an analytical runtime capability. Its verifier must be run against live hosted state before enforcement is claimed.

## Sequencing conclusion

The next repository objective is reproducible working-tree capture. It completes the provisional-state acquisition boundary needed before the required state-comparison matrix can be implemented.
