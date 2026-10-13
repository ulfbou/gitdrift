# Fact delta

## Purpose

This specification defines semantic fact changes across an explicit comparison or transition. Raw snapshots and patches remain evidence; fact deltas are attributed interpretations.

## Fact identity

A semantic fact records its stable subject, assertion kind, value, representation, state, producer, method, input evidence, confidence, and limitations. Identity does not depend on list position or rendered wording alone.

## Delta record

A fact delta contains:

```text
delta identity
comparison or transition identity
before facts
after facts
delta classification
supporting artifact changes
producer and method
confidence
alternatives and counterevidence
limitations and completeness
```

## Classifications

### Added

A fact is present after the comparison and no corresponding fact is established before it within scope.

### Removed

A corresponding fact is established before but not after. Removal is bounded by extraction and search completeness and does not by itself prove semantic regression.

### Modified

Corresponding facts retain a subject while assertion or value changes.

### Moved

A semantically corresponding fact changes representation location without established substantive change. Movement preserves both locations and correspondence evidence.

### Duplicated

One earlier representation corresponds to multiple later representations. Duplication may be harmless, strengthening, or a source of later contradiction; the delta itself does not decide.

### Strengthened

The later fact or representation provides greater obligation strength or protection without contradiction under identified authority.

### Weakened

The later fact or representation reduces obligation strength or protection under identified authority.

### Contradicted

The later fact conflicts with an applicable earlier or controlling fact and no accepted supersession resolves the conflict.

### Superseded

An authorized later fact replaces the earlier fact for the declared scope and activation boundary.

## Interpretation constraints

- Exact textual difference is not required for semantic change.
- Exact textual equality does not guarantee equivalent role or authority.
- A raw deletion is not automatically a removed fact.
- A moved or split representation is not automatically lost.
- Strength, weakness, contradiction, and supersession reference an obligation or authority relation.
- Unsupported extraction yields unresolved or unavailable semantic comparison, not absence.

## Provenance

Every fact delta is traceable to its before and after facts, fragments, snapshots, raw changes, extractor versions, correspondence methods, and completeness declaration.
