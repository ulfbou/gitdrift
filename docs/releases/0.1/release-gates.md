# Gitdrift 0.1 release gates

## Purpose

These gates define the mechanically evaluated release boundary for Gitdrift 0.1. They apply to the exact release candidate commit and its generated artifacts. A gate passes only from executable evidence; documentation assertions do not substitute for execution.

## Gate outcomes

Each gate records one outcome:

- **pass**: every mandatory check in the gate succeeded;
- **fail**: at least one mandatory check failed;
- **blocked**: required evidence or capability was unavailable, invalid, or incomplete;
- **not-applicable**: permitted only for a conditional check whose applicability is false and recorded.

A blocked mandatory gate prevents release exactly as a failed gate does. Warnings may coexist with a pass only when they do not invalidate a mandatory obligation or required completeness.

## G0: Candidate integrity

Purpose: establish the exact state being evaluated.

Mandatory checks:

- the release candidate is an immutable commit reachable from the intended release PR;
- the worktree and index used to build artifacts are clean;
- version and schema identifiers are internally consistent;
- the evidence directory is empty or uniquely scoped before the run;
- every later gate records the same candidate identity;
- generated artifacts have recorded content identities or digests.

Failure conditions include a dirty candidate, mixed commit identities, overwritten evidence, or unverifiable artifact identity.

## G1: Packaging, installation, and discovery

Purpose: prove the distributable product and declared capability boundary.

Mandatory checks:

- build source and wheel distributions from the candidate;
- install each distribution in an isolated environment without repository-root imports;
- import the supported public package;
- exercise the narrow public API smoke surface;
- invoke CLI capability and schema discovery;
- verify that discovery reports the state-awareness capabilities actually implemented;
- verify that deferred capabilities are not advertised as available;
- verify package and native-schema versions are independently represented.

Evidence:

- build logs;
- artifact digests;
- isolated-install logs;
- discovery documents;
- smoke-test results.

## G2: Repository acquisition and provisional-state safety

Purpose: prove truthful, reproducible acquisition of committed and provisional states.

Mandatory checks:

- immutable `HEAD` capture;
- optional upstream capture without fetch or integration;
- index capture including modes, stages, objects, base, manifest, and limitations;
- working-tree capture under every supported untracked and ignored-file policy;
- detection of relevant changes during capture;
- explicit handling of absent upstream, unborn or unavailable state, unmerged entries, symlinks, submodules, binary data, unsupported content, and unreadable evidence as applicable;
- no repository mutation during acquisition.

Evidence:

- adapter-conformance results;
- state manifests;
- race fixtures;
- mutation sentinel results;
- diagnostics and completeness records.

## G3: Domain, API, schema, and adapter contracts

Purpose: prove that implemented boundaries preserve the accepted semantic model.

Mandatory checks:

- domain-unit suite;
- public API contract suite;
- CLI-to-library translation suite;
- Git adapter conformance suite;
- Markdown and Python extractor conformance suites;
- obligation evaluator and case-builder suites;
- native serializer, validator, and sink conformance suites;
- capability discovery contract suite;
- stable diagnostic-code and process-mapping suite;
- native JSON Schema validation for all generated native artifacts;
- automated reference-closure validation;
- negative tests preventing evidence-class collapse, implicit authority, false ancestry, false absence, and deferred capability claims.

Evidence:

- machine-readable test results;
- schema-validation reports;
- reference-closure reports;
- representative validated native artifacts.

## G4: State-awareness profile acceptance

Purpose: prove the complete 0.1 vertical slice.

Mandatory synthetic scenarios:

- aligned clean repository;
- no staged or unstaged changes;
- local branch behind captured upstream;
- staged architecture migration;
- unstaged changes;
- simultaneous upstream and staged candidates;
- staged and working-tree divergence;
- partial extractor support;
- ambiguous semantic equivalence;
- unsupported artifact preserved;
- provisional state changes during capture;
- invalid request or configuration;
- bounded resource exhaustion or truncation;
- zero repository mutation.

Mandatory corpus check:

- run the accepted state-awareness request set against an immutable or reproducibly constructed `dx-artifacts` corpus identity.

Every scenario must verify expected states, comparisons, raw evidence, facts, obligation evaluations, cases, diagnostics, completeness, reproduction data, native-schema validity, and mutation sentinel applicable to the scenario.

## G5: Determinism, identity, compatibility, and golden evidence

Purpose: prove stable machine contracts.

Mandatory checks:

- repeated-run semantic equality for identical inputs;
- canonical ordering and serialization rules;
- identity independence from presentation order and mutable locators;
- comparison endpoint direction retained in identity;
- no strengthening of partial completeness;
- reference closure;
- raw evidence preserved under every supported semantic projection;
- golden native JSON comparison using semantic rather than incidental formatting equality;
- supported reader/writer/schema compatibility combinations;
- explicit rejection or partial-capability handling for unknown required semantics;
- migration provenance where migration is supported.

Evidence:

- determinism comparison reports;
- property-test results;
- golden artifact identities;
- compatibility matrix results.

## G6: Failure, partial analysis, resource, and adversarial behavior

Purpose: prove that incomplete or hostile conditions cannot become false analytical certainty.

Mandatory checks:

- unsupported artifact and capability handling;
- parser and extractor failure;
- missing or inaccessible evidence;
- malformed request and configuration;
- state-capture race;
- schema incompatibility;
- serialization and sink failure;
- every enforceable resource-budget exhaustion path;
- oversized and malformed content;
- hostile paths, symlinks, embedded instructions, and prompt-like repository content;
- bounded diagnostics without secrets or uncontrolled unrelated environment data;
- truthful partial native output when safe representation remains possible;
- explicit failure when identity, reference integrity, required-root serialization, or truthful completeness cannot be preserved.

Evidence:

- adversarial-suite results;
- partial-analysis artifacts;
- diagnostic-code reports;
- sink-integrity results.

## G7: Platform and read-only conformance

Purpose: prove declared environmental support and the core safety invariant.

Mandatory checks:

- execute applicable mandatory suites on every declared supported platform and Python version;
- verify path normalization, line endings, executable modes, symlinks, subprocess encoding, and filesystem limitations applicable to each platform;
- verify before/after identities for refs, `HEAD`, index, selected working-tree files, configuration, hooks, and relevant Git objects;
- verify output is written only to the explicit sink outside analyzed state or to a deliberately excluded path;
- represent platform-specific limitations through capability discovery and diagnostics.

A platform may be excluded only by narrowing the declared support boundary before release; an unrecorded platform failure cannot be waived as a warning.

## G8: Documentation, obligation closure, and release review

Purpose: prove that the candidate, evidence, and published contracts agree.

Mandatory checks:

- every mandatory obligation in the 0.1 matrix maps to at least one passing evidence record;
- no evidence record references a different candidate commit;
- every acceptance-checklist item is resolved;
- public API, CLI, schema, capability, limitation, and compatibility documentation matches implemented behavior;
- deferred capabilities are not described as available;
- release notes distinguish implemented behavior, limitations, deferred scope, and compatibility;
- local Markdown links resolve;
- no accepted obligation is weakened or contradicted without explicit supersession;
- all required gates G0 through G7 pass.

Evidence:

- obligation-closure report;
- completed acceptance checklist;
- documentation validation report;
- release-review record;
- gate summary.

## Final release rule

Gitdrift 0.1 is release-ready only when:

1. G0 through G8 pass for the same immutable candidate;
2. every mandatory GD01 obligation has passing executable evidence;
3. every conditional obligation is either passed or recorded not-applicable with its applicability evidence;
4. no mandatory check is failed, blocked, skipped, or represented only by prose;
5. all emitted native and release artifacts validate and retain recorded identities;
6. the release review finds no contradiction between implementation, capability discovery, schemas, acceptance evidence, and documentation.

The release gate must return nonzero status when this final rule is not satisfied. It must not modify the analyzed repository to obtain a passing result.
