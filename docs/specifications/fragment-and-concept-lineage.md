# Fragment and concept lineage

## Purpose

This specification defines longitudinal identity below the file level and across multiple artifacts.

## Fragment

A `Fragment` is a bounded representation inside an artifact snapshot. Supported fragment kinds may include:

```text
Markdown section
code symbol
configuration entry
requirement
normative statement
test or gate
explicit byte or line region
```

A fragment identity includes its containing snapshot and extractor-defined address. Line numbers alone are locators and do not provide durable identity.

## Fragment relations

Fragment lineage may record unchanged, modified, moved, copied, split, merged, deleted, restored, replaced, or unresolved correspondence. Every relation references exact snapshots and extractor provenance.

Deterministic syntax identity and inferred semantic correspondence remain distinct. Text similarity or a shared heading is not sufficient to establish durable equivalence.

## Concept

A `Concept` identifies a semantic subject independently of any one wording, path, file, or runtime language. Concepts require explicit project identity or attributed discovery evidence. They are not created solely because strings are similar.

## Concept representations

A `ConceptRepresentation` connects a concept to one or more fragments at a state. Each representation declares a role:

```text
authority
normative specification
implementation
enforcement
explanation
navigation
historical evidence
generated derivation
```

Two similar fragments may have different roles. Role determines how a representation participates in authority, obligation, equivalence, and regression analysis.

## One concept across many artifacts

A concept may be distributed across a decision, specification, implementation, test, configuration file, and release gate. The concept representation records each fragment and the relation among their roles.

Fragment movement or healthy decomposition does not constitute semantic loss when all relevant obligations and authority relations remain satisfied.

## One artifact containing many concepts

An artifact may represent several unrelated or overlapping concepts. File-level change therefore cannot be assigned wholesale to one concept. Extraction and case construction preserve the bounded fragments and facts involved.

## Representation evolution

Across states, a representation may be transferred, transformed, duplicated, weakened, strengthened, contradicted, retired, or superseded. These are semantic relations referencing fragment evidence and applicable authority.

A concept lineage is represented by successive concept representations and their relations. It does not require one permanent canonical file.

## Ambiguity

When split, merge, replacement, equivalence, or concept identity cannot be established, Gitdrift records candidates, alternatives, counterevidence, and unresolved questions. It does not force all related text into a single lineage.

## Completeness

Completeness records supported artifact and fragment kinds, extractor versions, selected states and refs, unresolved correspondence, concept-discovery scope, and representations outside the analyzed repository or request.
