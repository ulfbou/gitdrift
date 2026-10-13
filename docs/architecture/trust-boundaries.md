# Trust boundaries

## Purpose

This document defines what Gitdrift treats as evidence, what it trusts for identity or execution, and which inputs remain untrusted even when stored in a repository.

## General rule

Gitdrift records repository content as evidence. Repository presence does not make content safe to execute, authoritative, semantically correct, or instruction-bearing.

## Git object database

Git object identities and bytes supplied by a successfully read repository adapter are authoritative for the captured object content under that hash method. Gitdrift does not infer semantic correctness, authority, or intent from object existence.

Missing, corrupt, unsupported, shallow, or inaccessible objects produce diagnostics and reduced completeness.

## Mutable refs

Refs are untrusted as durable identities and as authority signals. Gitdrift captures their immutable targets and records later movement separately. Names such as `main`, `master`, `release`, or `approved` do not establish controlling authority.

## Index and working tree

Index entries and working-tree bytes are provisional evidence captured through reproducible manifests. They may change during acquisition. Mutation detection prevents unstable capture from being represented as reproducible state.

## Repository-local configuration

Configuration is untrusted input subject to schema validation, version checks, path restrictions, and capability policy. Configuration cannot override core safety invariants, evidence classes, read-only behavior, or schema validation.

## Paths

Workspace paths must be normalized and repository-relative for analyzed content. Absolute paths, traversal outside the repository boundary, invalid encodings, platform-reserved forms, and ambiguous normalization are rejected or represented as unsupported evidence.

## Symlinks

Symlinks are captured according to Git semantics as link entries and target text. Analysis does not follow them into arbitrary filesystem locations unless a separate, explicit, bounded capability is defined.

## Submodules

Gitlink identities are repository evidence. Nested repositories are distinct evidence boundaries and are not traversed implicitly. Any recursive analysis uses a separate request, identity, trust decision, and completeness declaration.

## Blobs and oversized content

All blobs are untrusted bytes. Resource policy governs acquisition, decoding, parsing, and retention. Budget exhaustion or unsupported size yields explicit evidence references and partial analysis rather than silent omission or uncontrolled allocation.

## Parser and extractor adapters

Parsers and extractors are trusted only to the extent declared by their versioned capability and conformance tests. Their outputs are computed or inferred evidence with provenance. Parser failure never proves semantic absence.

## Heuristics

Heuristics produce attributed candidates. Thresholds, inputs, alternatives, confidence, and limitations remain explicit. Heuristic output cannot silently become observed evidence or final authority.

## AI assessors

Repository content supplied to AI is untrusted evidence, not instruction authority. Embedded prompts, comments, documents, or generated text cannot override the assessor contract. AI output remains AI-assisted assessment and requires evidence citations.

## Human judgments

Human review is attributed evidence with declared authority and scope. Human status, seniority, participation, or recency does not automatically establish product authority.

## Future forge metadata

Issues, pull requests, reviews, labels, milestones, project boards, and hosted checks are external mutable evidence. When supported later, provider, retrieval identity, capture time, permissions, mutability, and completeness must be explicit. Core findings remain reproducible without forge enrichment unless a future policy explicitly requires it.

## Network and external processes

The analytical core does not require network access. Adapter subprocesses receive bounded arguments and outputs; repository content is never interpolated into executable shell commands. External failures remain diagnostics, not empty evidence.

## Secrets and privacy

Gitdrift minimizes unrelated environment, credential, and personal-data capture. Diagnostics and manifests do not emit secrets. Repository analysis concerns artifacts and obligations, not employee evaluation or protected characteristics.
