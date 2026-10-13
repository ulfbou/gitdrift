# Gitdrift 0.1 acceptance checklist

## Purpose

This document is the controlling acceptance-ready checklist for the Gitdrift 0.1 milestone. It converts the state-awareness roadmap, specifications, profile contract, acceptance scenarios, and testing strategy into one reviewable release boundary.

This checklist distinguishes three states:

- **PR-ready**: one bounded change is reviewable and preserves the controlling contracts.
- **Milestone acceptance-ready**: every required 0.1 capability has implementation and executable evidence, with no unresolved release-blocking obligation.
- **Release-ready**: every mandatory release gate passes against the exact release candidate and the evidence set is complete.

Documentation alone cannot satisfy implementation or release-evidence items.

## Scope boundary

Gitdrift 0.1 implements the state-awareness vertical slice for explicit committed and provisional repository states. The supported analytical boundary is:

- capture `HEAD` as an immutable commit state;
- capture an optional configured upstream as an immutable tip plus mutable locator;
- capture `INDEX` reproducibly;
- capture `WORKTREE` reproducibly under explicit untracked and ignored-file policies;
- construct every required comparison whose endpoints exist;
- preserve exact repository evidence and raw path changes;
- extract only facts supported by implemented, declared extractors;
- evaluate explicitly supplied or accepted repository-local obligations;
- construct bounded cases with evidence, counterevidence, unknowns, completeness, and reproduction data;
- emit and validate canonical native JSON;
- perform no mutation of the analyzed repository.

The following remain outside the 0.1 implementation boundary:

- all-branch archaeology;
- complete file-history reconstruction;
- generalized rename, split, merge, restoration, or concept-lineage inference;
- divergence and gold-nugget analysis beyond contracts needed for future compatibility;
- AI-assisted assessment;
- forge integration;
- SARIF or DX evidence export;
- repository mutation or automatic fixes;
- composite pressure, purity, health, risk, or drift verdict scores.

## PR-ready checklist

A pull request advancing Gitdrift 0.1 is PR-ready only when all applicable items pass.

- [ ] The PR originates from a non-`master` branch and targets `master`.
- [ ] Scope, controlling baseline, validation, and limitations are stated.
- [ ] Applicable type, area, profile, and review-state labels are present.
- [ ] The PR belongs to `Gitdrift 0.1: repository-state alignment and provenance`.
- [ ] The change is one coherent increment and contains no unrelated capability.
- [ ] Changed behavior is mapped to obligation identifiers in the 0.1 obligation matrix.
- [ ] Established obligations are preserved or explicitly superseded by accepted authority.
- [ ] Tests cover the changed behavior and relevant failure paths.
- [ ] Documentation is updated when a public contract, supported capability, limitation, or diagnostic changes.
- [ ] Native output changes preserve schema, identity, reference, evidence-class, completeness, and compatibility rules.
- [ ] Repository read-only behavior is covered by a mutation sentinel where the change touches acquisition or analysis.
- [ ] Required validation passes from a clean checkout of the candidate commit.
- [ ] Generated evidence identifies the exact candidate commit and relevant tool, schema, extractor, obligation-set, and policy versions.
- [ ] No required check is skipped without an explicit release-blocking diagnostic.

## Milestone acceptance-ready checklist

The 0.1 milestone is acceptance-ready only when every item below is supported by executable evidence.

### Product and packaging

- [ ] Gitdrift is installable as a Python library distribution in the declared supported environments.
- [ ] The supported package exposes a narrow, typed, use-case-oriented API without requiring CLI process objects or standard streams.
- [ ] A thin CLI adapter can discover active capabilities and run the state-awareness profile from explicit inputs.
- [ ] Capability discovery reports implemented capabilities only and does not advertise deferred adapters or profiles.

### Repository-state acquisition

- [ ] `HEAD` capture records immutable commit and tree identities.
- [ ] Optional upstream capture records the ref locator and immutable captured target without fetching or integrating.
- [ ] Index capture records selected stage, mode, object, base, manifest, policy, and limitation data.
- [ ] Working-tree capture records selected exact content, modes, deletion state, untracked policy, ignored policy, and limitations.
- [ ] Relevant mutation during provisional capture is detected and represented according to the bounded retry or failure policy.
- [ ] Unsupported, unreadable, unmerged, binary, symlink, submodule, or oversized evidence is preserved or diagnosed without false semantic absence.

### Comparisons and evidence

- [ ] `HEAD -> INDEX` is produced when both states exist.
- [ ] `INDEX -> WORKTREE` is produced when both states exist.
- [ ] `HEAD -> WORKTREE` is produced when both states exist.
- [ ] `HEAD <-> upstream` is produced when upstream is selected and available.
- [ ] Missing endpoints produce explicit unavailable or non-applicable matrix entries rather than disappearing rows.
- [ ] Comparisons do not imply ancestry unless ancestry is established separately.
- [ ] Raw changes retain endpoint, path, mode, object, binary, rename/copy, diff-option, and limitation evidence applicable to the comparison.
- [ ] Unsupported semantic extraction never deletes exact repository evidence.

### Facts, obligations, and cases

- [ ] Markdown section extraction is implemented and versioned.
- [ ] Python symbol extraction is implemented and versioned.
- [ ] Extracted facts retain producer, version, exact inputs, method, derivation class, confidence class, and limitations.
- [ ] Obligation definitions retain identity, subjects, relation, authority, scope, activation, retirement, supersession, and provenance.
- [ ] Evaluations retain state, applicable authority, supporting evidence, counterevidence, method, completeness, limitations, and unresolved questions.
- [ ] Changed paths or symbols select possibly affected obligations but do not independently establish regression.
- [ ] Cases separate observations, interpretations, obligations, assessments, alternatives, supporting evidence, counterevidence, unknowns, completeness, reproduction, and optional judgment.
- [ ] Ambiguous equivalence, authority, coverage, or supersession remains unresolved rather than being promoted by confidence alone.

### Native model and diagnostics

- [ ] The accepted native JSON Schema exists and has an independently versioned identity.
- [ ] Every emitted native investigation validates against its declared schema.
- [ ] Every internal reference resolves or uses an explicit retrievable evidence reference.
- [ ] Stable identity does not depend on presentation order, mutable ref names, timestamps, or display labels.
- [ ] Observed, computed, heuristic, AI-assisted, and human-supplied records cannot silently collapse into one evidence class.
- [ ] Root and child completeness declarations cannot represent partial analysis as complete.
- [ ] Diagnostics use stable codes and distinguish execution conditions from analytical findings.
- [ ] Successful findings and unresolved cases do not become process failures.
- [ ] Serialization or sink failure cannot be reported as a complete artifact.

### Acceptance scenarios

- [ ] Aligned clean repository.
- [ ] Local branch behind captured upstream.
- [ ] Staged architecture migration.
- [ ] Unstaged changes.
- [ ] Simultaneous upstream and staged candidates.
- [ ] Staged and working-tree divergence.
- [ ] Partial extractor support.
- [ ] Ambiguous semantic equivalence.
- [ ] Unsupported artifact preserved.
- [ ] Zero repository mutation.
- [ ] No staged or unstaged changes.
- [ ] Provisional state changes during capture.
- [ ] Invalid request or configuration.
- [ ] Resource exhaustion or truncation with truthful partial output where representable.

### Quality and compatibility

- [ ] Repeated runs over identical immutable inputs and configuration produce semantically identical native results.
- [ ] Golden native artifacts verify canonical serialization, reference closure, diagnostics, completeness, and reproduction.
- [ ] Property tests cover ordering-independent identity, endpoint direction, completeness monotonicity, reference closure, and raw-evidence preservation.
- [ ] Adapter conformance tests cover Git acquisition, parsers, extractors, serializers, schema validation, and output sinks.
- [ ] Cross-platform tests cover every declared supported platform and disclose platform-specific limitations as capabilities or diagnostics.
- [ ] Adversarial tests cover untrusted paths, content, configuration, oversized inputs, malformed data, and bounded resource use.
- [ ] Compatibility tests cover supported reader/writer/schema combinations and reject unknown required semantics.
- [ ] The `dx-artifacts` acceptance corpus is pinned by immutable repository identity or constructed reproducibly; mutable hosted state is not an unqualified expected fact.

## Acceptance decision

The milestone may be declared acceptance-ready only when:

1. every applicable checklist item is checked;
2. every mandatory obligation in the matrix has passing evidence;
3. every required release gate has a recorded pass for the exact candidate;
4. no unresolved diagnostic can invalidate identity, reference integrity, read-only safety, schema validity, evidence classification, or required completeness;
5. every accepted limitation is explicit and does not contradict the 0.1 scope boundary.

A partial result may satisfy an individual scenario only when that scenario expects partial execution and verifies accurate diagnostics and completeness. Partial execution cannot satisfy a gate requiring complete coverage.
