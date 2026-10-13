# Native investigation model

## Purpose

This specification defines the first serializable Gitdrift investigation shape. It precedes the JSON Schema but is precise enough for schema construction to be mechanical.

## Root document

A native investigation contains:

```text
schema
investigation identity
analysis manifest
states
comparisons
transitions
artifact changes
facts
obligations
evaluations
cases
completeness
diagnostics
```

Collections are identified records, not positional tuples. Stable identity never depends on array order.

## Schema and investigation identity

`schema` identifies the native model family and independent schema version. The investigation identity derives from the canonical manifest and selected immutable or captured inputs, subject to the schema's normalization rules.

## Analysis manifest

The manifest records repository identity, captured ref targets, provisional-state manifests, profile and request, path or subject scope, traversal and diff configuration, extractors and versions, obligation-set identity, configuration digest, and execution capabilities.

## States

Each state records state identity, kind, immutable content identity or capture manifest, locators observed at capture, base state where applicable, and capture limitations.

## Comparisons and transitions

A comparison references ordered state identities, its question and kind, the applicable change set, and limitations. A transition additionally records an established historical relation such as parent-to-child. The model does not serialize every comparison as ancestry.

## Artifact changes

Artifact changes retain raw status, source and destination paths, object identities, modes, patch identity, binary treatment, and rename or copy evidence. Derived structural relations reference these records.

## Facts

Facts identify subject, value or assertion, representation, producer, method, input evidence, derivation class, confidence class, and limitations. Fact deltas reference before and after facts plus supporting changes.

## Obligations and evaluations

Obligations retain identity, subjects, relation, authority, scope, activation, retirement, supersession rules, and provenance. Evaluations reference one obligation and state with value, evidence, counterevidence, method, completeness, and unresolved questions.

## Cases

Cases follow `case-model.md` and reference shared records by stable identity. A case may embed bounded projection details but must not create conflicting copies of canonical evidence records.

## Completeness

Root completeness summarizes dimension-specific declarations while states, comparisons, extractors, evaluations, and cases may carry narrower declarations. A summary cannot strengthen a partial child declaration.

## Diagnostics

Diagnostics report execution, input, unsupported capability, capture, validation, and serialization conditions. Findings belong in evaluations or cases, not diagnostics merely because they may require review.

Each diagnostic records severity, stable code, message, affected identities, and evidence reference where applicable. Human-readable messages are not stable machine identifiers.

## Serialization invariants

1. Native JSON is authoritative.
2. Every reference resolves within the document or through an explicit retrievable evidence reference.
3. Observed evidence and derived assertions retain distinct classes.
4. Mutable locators never replace immutable targets.
5. Partial or omitted analysis is explicit.
6. Unknown enum values are not silently coerced.
7. Renderers and transports cannot change judgment semantics.
8. Execution failure is distinct from a successfully represented finding.

## Schema boundary

The first JSON Schema will define exact property names, required fields, formats, extensibility, and compatibility behavior. This specification controls meaning until that schema is accepted and must not be weakened by serializer convenience.
