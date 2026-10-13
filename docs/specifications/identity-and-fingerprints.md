# Identity and fingerprints

## Purpose

This specification defines stable identity and fingerprints across states, transitions, artifacts, lineages, facts, obligations, assessments, cases, and evidence.

## Principles

Identity derives from canonical semantic inputs whenever possible. It never depends solely on display order, generated sequence numbers, mutable ref names, presentation formatting, timestamps, or human-readable labels.

Every identity records its scheme and version. A fingerprint is evidence for comparison or lookup and is not automatically durable domain identity.

## Repository states

Commit states use repository object format and immutable commit identity plus repository identity where collision domains require it. Captured provisional states derive identity from normalized manifests, base identities, policies, and exact content fingerprints.

Changing a mutable locator without changing the captured target does not change state identity. Changing captured content, mode, policy-relevant inclusion, or normalized manifest does.

## Transitions and comparisons

Identity includes ordered endpoint identities, transition or comparison kind, parent identity and number where applicable, and semantic diff or traversal options that define the result.

Changing presentation order does not change identity. Reversing endpoints or changing result-defining options does.

## Artifact instances and snapshots

A snapshot identity includes state, normalized workspace-relative path, content identity, and relevant mode or kind. An artifact instance may also reference a project-defined or lineage identity.

A path rename changes snapshot location and identity but does not necessarily create a new artifact lineage identity.

## Lineages

A lineage identity is project-defined or derived from a canonical set of supported roots and relation evidence under a versioned scheme. New relation evidence may create a revised lineage record rather than silently rewriting historical identity.

## Facts

Fact identity includes stable subject, assertion kind, normalized value, state or applicable scope, representation role where material, producer method, and identity-scheme version. Rewording that preserves normalized semantics may retain semantic correspondence without retaining record identity.

## Obligations

Obligation identity is explicitly assigned or derived from normalized subjects, required relation, scope, authority references, activation, retirement, and identity-scheme version. Moving its source file alone does not change obligation identity when the project identity and semantics remain stable.

## Evidence

Evidence identity includes evidence class, immutable subject identity, payload or retrieval identity, producer, and method where derived. Derived evidence never reuses the identity of its inputs.

## Assessments and judgments

Assessment identity includes assessor class and identity, version, bounded question, inputs, method, and output digest. Judgment identity additionally includes policy identity and version plus the case identity.

## Cases

Case identity includes question, subject, selected evidence and interpretation identities, obligation and assessment identities, completeness, selection identity, and schema version. Rendering changes do not change case identity; materially different included evidence or completeness does.

## Fingerprints

Fingerprints may support content comparison, cache lookup, patch equivalence, normalized fact matching, or configuration identity. Every fingerprint declares algorithm, normalization, input scope, and collision limitations.

## Canonicalization

Canonicalization is schema-versioned and deterministic. Unknown fields or unsupported normalization prevent identity computation rather than being silently discarded when they may affect semantics.

## Corrections and supersession

Corrections create new records and identities linked to replaced records. Historical evidence is immutable. Supersession changes applicability or authority relationships, not the bytes or identity of prior evidence.
