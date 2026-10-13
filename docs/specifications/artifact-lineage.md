# Artifact lineage

## Purpose

This specification defines artifact identity and the relations used to reconstruct artifact evolution across repository states.

## Identity and instances

A path is a location at a state, not an artifact identity. An `ArtifactInstance` binds:

```text
artifact or lineage identity
repository-state identity
workspace-relative path
artifact-snapshot identity
content identity
file mode or artifact kind
provenance
```

An `ArtifactLineage` is an evidence-backed graph of instances and typed relations. It is not required to be a single path or chain.

## Relation classes

### Creation

An instance appears without a supported predecessor within the declared traversal and artifact scope. Creation is bounded by completeness and does not prove that similar content never existed elsewhere.

### Modification

A predecessor and successor represent the same supported artifact identity with changed content, mode, or metadata under an explicit transition.

### Rename and move

A rename or move relates locations across states. Git rename evidence, content similarity, and structural analysis are recorded separately. A changed path alone does not break artifact identity.

### Copy

A copy candidate relates one predecessor to multiple successor instances while preserving the source. Copy detection method, similarity, and limitations remain explicit.

### Deletion

An instance is absent at a successor state relative to a specific transition. Deletion does not prove semantic loss, retirement, or repository-wide absence.

### Restoration

A later instance is supported as restoring an earlier artifact, fact set, or obligation representation after absence or replacement. Restoration references the earlier lineage and intervening evidence.

### Replacement

A successor artifact may replace the function or authority of another without retaining the same path or content. Replacement is an inferred or declared relation and requires semantic and authority evidence.

### Split

One source instance may correspond to multiple successor artifacts or fragments. Split accounting identifies transferred, transformed, duplicated, residual, and unaccounted material where supported.

### Merge

Multiple predecessor artifacts or fragments may correspond to one successor. The relation preserves each source and identifies overlap, conflict, transformation, and unresolved attribution.

### Supersession

Supersession identifies that a representation is no longer controlling because an authorized replacement became effective. It is not inferred from recency, deletion, or movement alone.

## Deterministic and inferred relations

Each relation records:

```text
relation identity
relation class
source instances
target instances
producer and version
method
input evidence
confidence class
alternatives
limitations
```

Commit identity, exact object identity, and explicit repository declarations may support deterministic relations. Similarity, rename scoring, split inference, replacement, and semantic equivalence remain attributed derivations unless stronger evidence establishes them.

## Branching and merging

A lineage graph preserves alternate branch-specific evolutions and parent-specific merge transitions. Endpoint equivalence does not erase distinct provenance. One state may contain several active or contradictory descendants of the same earlier artifact.

## Completeness

Lineage completeness records traversed refs and commits, parent policy, path and artifact scope, rename and copy configuration, unsupported artifact kinds, unresolved relation candidates, and omitted history.
