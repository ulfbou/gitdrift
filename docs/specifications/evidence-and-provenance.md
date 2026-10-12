# Evidence and provenance

## Purpose

This specification defines the minimum information required for a machine-readable Gitdrift assertion to remain inspectable, reproducible, and safe for human or AI use.

## Evidence classes

Gitdrift distinguishes:

```text
observed
computed
heuristic
AI-assisted
human-supplied
```

An observed record is read directly from repository state. A computed record follows a deterministic declared transformation. A heuristic record depends on thresholds or inference. AI-assisted and human-supplied records retain their assessor identity and inputs.

No derived class may be serialized as observed evidence.

## Evidence record

An evidence record identifies:

```text
stable evidence ID
evidence class
producer and producer version
input evidence IDs
repository and state identity
artifact path or logical subject when applicable
method and configuration
payload or retrievable content identity
limitations
```

Mutable ref names may be retained as locators, but immutable commit, tree, blob, or captured-state identities control reproduction.

## Derived assertion

Every derived assertion must include:

```text
assertion ID
assertion kind
producer
input evidence IDs
method
confidence class
limitations
supporting evidence
counterevidence when available
```

Confidence does not replace evidence completeness. A high-confidence assertion over partial traversal remains partial.

## Reproduction manifest

Every investigation includes a reproduction manifest containing at least:

```text
repository identity
resolved refs and immutable targets
captured provisional states
selected traversal and parent policy
rename and copy options
path or subject scope
extractors and versions
obligation set identity
configuration digest
schema version
```

## Completeness declaration

Completeness is declared independently for:

```text
graph traversal
selected refs
state capture
artifact coverage
lineage resolution
semantic extraction
obligation coverage
counterevidence search
external context
```

Initial values are:

```text
complete
partial
unavailable
not-requested
not-applicable
```

A result may not claim repository-wide absence when the relevant coverage dimension is partial, unavailable, or not requested.

## Counterevidence requirement

A possible-regression case must actively record recognized alternatives, including:

- replacement or supersession;
- equivalent representation elsewhere;
- rename, split, merge, or generated-artifact effects;
- intentional scope removal expressed by repository-local authority;
- incomplete extractor or traversal coverage.

The absence of discovered counterevidence is not proof that none exists unless the applicable search dimensions are complete.

## Transport independence

Native Gitdrift data owns the evidence semantics. JSON, JSON Lines, human views, SARIF, and future DX carriers are representations or transports of that model. Transport framing must not alter evidence identity or judgment semantics.
