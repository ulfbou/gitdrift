# Domain model

## Purpose

This document defines the canonical domain entities, their ownership, identity rules, aggregate boundaries, and allowed dependencies. It refines the layered architecture without fixing Python package names or serialization shapes.

## Identity and location

A domain identity denotes a stable subject. A location denotes where a representation can be found at a particular state.

- A repository path is an artifact location, not an artifact identity.
- A branch name is a mutable locator, not a state identity or proof of authority.
- A fragment location is meaningful only with its artifact snapshot and state.
- Display order and generated sequence numbers never control identity.
- Stable identifiers derive from immutable inputs where possible; captured provisional states use reproducible manifests and digests.

## Canonical entities by layer

### Layer 0: repository evidence

`RepositoryState` is a content-addressable or reproducibly captured repository view. It owns a state identity, state kind, immutable targets or capture manifest, and locators recorded at capture time.

`Transition` identifies an ordered comparison between two states and records comparison semantics, parent specificity, traversal configuration, and diff options. Only a parent-to-child transition asserts ancestry.

`ArtifactSnapshot` is the exact representation of one workspace-relative path at one state. It records content identity, file mode or artifact kind, and exact bytes or a retrievable evidence reference.

`EvidenceReference` identifies evidence without changing its class. It records evidence ID, evidence class, producer, immutable subject identity, retrieval information, and limitations.

### Layer 1: structural evolution

`ArtifactInstance` binds an artifact identity to an `ArtifactSnapshot` at a state.

`ArtifactLineage` relates artifact instances across states through typed deterministic or inferred relationships. It does not itself establish semantic equivalence, authority, or regression.

`Fragment` identifies a bounded region, section, symbol, requirement, or other addressable part of an artifact snapshot.

### Layer 2: semantic representation

`Concept` identifies a semantic subject independently of any one file, path, or wording.

`ConceptRepresentation` binds a concept to one or more fragments at a state and classifies each representation role, including authority, normative specification, implementation, enforcement, explanation, navigation, historical evidence, or generated derivation.

`SemanticFact` is a meaning-bearing assertion extracted from or supplied about repository evidence. It retains producer, method, inputs, confidence class, and limitations.

### Layer 3: alignment and obligations

`Obligation` declares a relation that must hold among subjects under an identified authority, scope, and activation interval.

`ObligationEvaluation` records the result of evaluating one obligation at one state. It references facts and evidence used, applicable authority, evaluation value, completeness, and unresolved questions.

### Layer 4: cases and judgment support

`Assessment` relates evidence, interpretations, or obligation evaluations to a bounded question. Its assessor class is deterministic, heuristic, AI-assisted, or human-supplied.

`Case` is a bounded, judgment-ready projection around one question and subject. It aggregates observations, interpretations, obligations, assessments, alternatives, supporting evidence, counterevidence, unknowns, completeness, reproduction, and optional judgment.

`Judgment` is a policy-governed classification. It never rewrites observations, interpretations, or assessments.

`CompletenessDeclaration` records coverage independently by dimension and prevents partial analysis from being represented as repository-wide proof.

`ReproductionManifest` records repository identity, resolved immutable states, traversal and diff configuration, capture manifests, extractors, obligation-set identity, and schema version.

## Aggregate boundaries

The initial aggregate boundaries are:

1. Evidence aggregate: repository states, transitions, snapshots, raw changes, and evidence references.
2. Lineage aggregate: artifact instances, artifact lineages, fragments, and structural relations.
3. Semantic aggregate: concepts, representations, semantic facts, and semantic relation candidates.
4. Obligation aggregate: obligations, authority references, scopes, activation, and evaluations.
5. Case aggregate: bounded question, assessments, evidence inventory, completeness, reproduction, and judgment.

Aggregates reference entities in lower layers by stable identity. They do not copy a lower-layer record into a different evidence class or silently strengthen its certainty.

## Deterministic and inferred relationships

Every relationship declares its derivation class.

- Deterministic relationships follow directly from selected repository evidence and declared comparison semantics.
- Heuristic relationships depend on thresholds, similarity, or inference.
- AI-assisted and human-supplied relationships are attributed assessments.

Rename scores, content similarity, shared names, and textual resemblance may support candidates but do not establish semantic equivalence or supersession by themselves.

## Lineage relationships

Artifact lineage answers how concrete artifact instances correspond. Fragment lineage answers how bounded regions correspond. Concept lineage is represented through successive `ConceptRepresentation` records and their evidence-backed relations.

An obligation may govern concepts, facts, fragments, artifact instances, or relations among them. Obligation lineage is expressed through activation, retirement, and explicit supersession, not inferred merely from changed wording or a newer state.

## Dependency direction

Dependencies point from higher layers to stable identities and contracts in lower layers:

```text
cases -> obligations -> semantics -> structural evolution -> repository evidence
```

Allowed orchestration occurs through application services. Prohibited dependencies include:

- repository evidence importing lineage, semantics, obligations, cases, or presentation;
- structural evolution declaring semantic equivalence or regression;
- semantic representation importing cases or renderers;
- obligations depending on CLI or transport framing;
- cases depending on DX, SARIF, Markdown, or terminal rendering;
- renderers originating semantic decisions.

## Immutability and correction

Domain records are immutable observations or attributed derivations. Correction creates a replacement record with provenance; it does not mutate historical evidence. Mutable caches and adapter state are implementation concerns and are not part of the domain contract.
