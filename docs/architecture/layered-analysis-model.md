# Layered analysis architecture

## Architectural style

Gitdrift begins as a modular monolith: one Python library distribution, one thin CLI adapter, and multiple analysis profiles over shared domain contracts.

Dependencies point inward. Infrastructure adapters implement domain-owned ports. Lower layers never import higher layers.

```text
presentation and transport
          |
cases and judgment support
          |
alignment and obligations
          |
semantic representation
          |
structural evolution
          |
repository evidence
```

## Layer 0: repository evidence

Responsibilities:

- resolve immutable state identities;
- enumerate refs, commits, parents, trees, and blobs;
- materialize index and working-tree states without mutation;
- enumerate parent-to-child transitions;
- preserve raw changes, object identities, and traversal configuration.

Representative types:

```text
RepositoryState
StateId
Transition
ArtifactSnapshot
RawChange
EvidenceRecord
```

This layer reports only what repository evidence proves.

## Layer 1: structural evolution

Responsibilities:

- path, region, and symbol lineages;
- rename, copy, move, split, merge, and replacement candidates;
- adjacent, rolling, epoch, and obligation-relative windows;
- alternate-chain correspondence;
- accretion and fragmentation observations.

Representative types:

```text
ArtifactIdentity
ArtifactInstance
ArtifactLineage
Fragment
FragmentRelation
EvolutionChain
StructuralDelta
```

This layer may report a probable rename or possible split. It may not declare semantic regression.

## Layer 2: semantic representation

Responsibilities:

- extract machine-readable facts from content;
- identify concepts and representations;
- classify representation roles such as authority, specification, implementation, enforcement, explanation, navigation, historical evidence, and generated derivation;
- propose equivalence, contradiction, supersession, and residue relationships.

Representative types:

```text
SemanticFact
Concept
ConceptRepresentation
RepresentationRole
SemanticDelta
AuthorityClaim
EquivalenceCandidate
ContradictionCandidate
```

Every derived assertion records producer, version, inputs, method, confidence, and limitations.

## Layer 3: alignment and obligations

Responsibilities:

- activate explicitly declared obligations;
- determine scope and authority;
- evaluate obligations at repository states;
- compare obligation strength across transitions and branches;
- identify weakening, violation, contradiction, and unresolved supersession.

Representative types:

```text
Obligation
ObligationScope
ObligationEvaluation
AlignmentAssessment
RegressionCandidate
DivergenceCandidate
```

Possible evaluation states are:

```text
satisfied
strengthened
weakened
violated
contradictory
superseded
absent
not-applicable
unresolved
```

## Layer 4: cases and judgment support

Responsibilities:

- assemble observations, interpretations, obligations, assessments, and alternatives;
- include supporting evidence and counterevidence;
- expose unknowns and completeness limits;
- formulate bounded review questions;
- apply deterministic judgment policies;
- accept separately attributed human or AI assessments.

Representative types:

```text
Case
CaseQuestion
Assessment
Judgment
CompletenessDeclaration
ReproductionManifest
```

Judgment classifications may include:

```text
true-regression
authorized-change
divergence
valuable-alternative
false-positive
insufficient-evidence
unresolved
```

AI may propose semantic equivalence, summarize evidence, and rank candidates. It may not invent repository facts, establish authority from recency or branch naming, or finalize a regression without the configured policy gate.

## Layer 5: presentation and transport

Responsibilities:

- canonical native JSON;
- JSON Lines streams for large investigations;
- human text and Markdown views;
- later SARIF interoperability;
- later DX evidence-carrier export.

No semantic decision originates in this layer.

## Cross-layer invariants

1. Every derived object references its input evidence.
2. Deterministic, heuristic, AI-assisted, and human-supplied claims remain distinguishable.
3. Partial analysis declares its completeness limits.
4. A transition is never erased from evidence; a projection may explicitly suppress it.
5. Branch names are locators, not immutable identities or proof of authority.
6. Large changes and high churn are selectors for deeper analysis, not verdicts.
7. Content similarity alone does not prove semantic equivalence.
8. Repository mutation is outside the core.

## Library design constraints

The library favors small immutable domain records and explicit use cases over generic dictionaries and a universal `analyze(repository)` entry point.

Preferred application operations include:

```text
capture_states
compare_states
construct_transitions
reconstruct_lineage
extract_facts
evaluate_obligations
build_cases
apply_judgment_policy
```

Profiles compose these operations without bypassing layer contracts.
