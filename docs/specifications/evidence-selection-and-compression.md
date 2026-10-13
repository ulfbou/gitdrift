# Evidence selection and compression

## Purpose

This specification defines how large histories become bounded investigations and cases without hiding omitted evidence or changing semantic identity.

## Selection record

Every selected evidence set records:

```text
selection identity
question and subject
source investigation or traversal
inclusion rules
included evidence identities
omitted evidence inventory
ordering
digests and retrieval identities
completeness effects
producer and configuration
```

## Inclusion rationale

Evidence may be included because it establishes state identity, transition, lineage, fact, obligation, assessment, alternative, counterevidence, or reproduction. Inclusion rationale is machine-readable and may name more than one role.

## Omitted evidence

Omission is explicit. The inventory identifies omitted ranges, transitions, artifacts, or records with counts only when mechanically established, plus digests or retrieval identities where available.

Omitted evidence is not described as irrelevant unless an attributed policy supports that classification.

## Digest and retrieval identity

Selected snapshots, patches, and records retain immutable content digests or repository object identities. External retrieval requirements, unavailable objects, and access limitations are recorded.

## Compression forms

A bounded case may use selected snapshots, selected patches, fact summaries, lineage projections, or grouped diagnostics. Summaries reference source evidence and never become observed evidence merely through compression.

## Completeness effects

Selection and compression update applicable completeness dimensions. A compact case cannot claim repository-wide absence, equivalence, or exhaustive counterevidence when omitted scope could affect the conclusion.

## Re-expansion

Where source evidence remains available, the selection record provides enough identity and configuration to reproduce or expand the bounded view. Failure to retrieve source evidence is explicit.

## Transport independence

Selection occurs in the native evidence model. Markdown, SARIF, JSON Lines, and future DX transport may carry a selection but cannot redefine its meaning or silently discard the omission inventory.
