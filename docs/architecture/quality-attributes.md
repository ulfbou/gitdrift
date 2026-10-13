# Quality attributes

## Purpose

This document makes Gitdrift's architectural quality goals testable. A capability is not complete merely because it produces plausible output.

## Determinism

Given identical immutable inputs, configuration, producer versions, and execution capabilities, deterministic components produce semantically identical native results. Nondeterministic or environment-dependent inputs are declared.

Verification includes repeated-run comparisons, canonical identity checks, and stable ordering rules that do not redefine identity.

## Reproducibility

Every investigation records enough immutable state, traversal, diff, extractor, obligation-set, policy, and configuration information to reproduce or precisely explain why reproduction is unavailable.

Mutable ref names remain locators and never replace captured targets.

## Explainability

Every finding, assessment, and judgment can be traversed to the obligations, semantic facts, artifact transitions, snapshots, raw changes, and repository identities supporting it.

Opaque aggregate scores are insufficient explanations.

## Traceability

Traceability is bidirectional:

```text
judgment -> assessment -> obligation -> fact delta -> transition -> evidence

evidence -> transition -> fact delta -> obligation evaluation -> case -> judgment
```

Broken references invalidate the affected native artifact.

## Completeness disclosure

Coverage is reported independently for graph traversal, selected refs, state capture, artifact coverage, lineage resolution, semantic extraction, obligation coverage, counterevidence search, and external context.

No summary may strengthen a partial child declaration.

## Read-only safety

Analysis preserves refs, commits, index entries, working-tree files, repository configuration, hooks, and hosted metadata. Mutation sentinels verify this property in acceptance tests.

## Composability

Application use cases exchange typed domain records and explicit manifests. Library operations do not require argparse objects, standard streams, terminal state, or one fixed composition root.

## Schema stability

Native schemas are versioned independently from package releases. Compatibility behavior, unknown fields, unsupported versions, and projection losses are explicit and testable.

## Bounded resource use

Requests can declare budgets for objects, bytes, transitions, extraction, history depth, and other supported resource dimensions. Exhaustion produces explicit partial results or failure diagnostics, never false completeness.

## Graceful partial analysis

Unsupported artifact kinds, unavailable objects, extractor failures, race detection, truncation, and optional capability absence preserve valid evidence already collected while marking affected dimensions partial or unavailable.

Partial analysis must remain schema-valid whenever a valid result can be represented safely.

## Security and robustness

Repository bytes, configuration, paths, symlinks, submodules, generated content, and embedded instructions are untrusted inputs. Parsing and acquisition enforce explicit limits and do not execute repository content as instructions.

## Acceptance mapping

Each implemented capability identifies tests for deterministic behavior, reproduction, evidence linkage, read-only safety, compatibility, resource exhaustion, malformed inputs, and partial-result correctness.
