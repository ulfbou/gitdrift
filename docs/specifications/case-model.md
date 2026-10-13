# Case model

## Purpose

A `Case` is the canonical judgment-ready projection of repository evidence around one bounded question. It separates facts, interpretations, obligations, assessments, and judgment.

## Required structure

A case contains:

```text
case identity
question
subject
observations
interpretations
obligations
assessments
alternatives
supporting evidence
counterevidence
unknowns
judgment
completeness
reproduction
evidence inventory
```

## Question and subject

The question identifies the decision to be made, such as possible regression, unresolved divergence, candidate nugget, semantic fragmentation, or authority conflict. It names the relevant states or transition and does not presuppose the answer.

The subject references a stable artifact lineage, fragment, concept, fact, obligation, transition, or explicitly bounded collection.

## Observations

Observations are directly established repository evidence or deterministic normalizations of it. They retain evidence class, producer, immutable inputs, method, and limitations.

Examples include commit parentage, resolved object identities, exact snapshots, raw changes, and captured state manifests.

## Interpretations

Interpretations derive meaning from observations, including structural relations, extracted semantic facts, fact deltas, equivalence candidates, and contradiction candidates. They identify producer, method, input evidence IDs, confidence class, and limitations.

No inferred, heuristic, AI-assisted, or human-supplied assertion may be serialized as observed evidence.

## Obligations and assessments

The case includes each applicable obligation with authority, scope, activation, and provenance. Assessments relate the evidence or transition to those obligations and retain assessor class.

An assessment cannot mutate an obligation evaluation or erase conflicting assessments.

## Alternatives and counterevidence

Every possible-regression case actively records recognized alternatives, including:

- authorized retirement or supersession;
- equivalent or stronger representation elsewhere;
- rename, copy, split, merge, replacement, or generated-artifact effects;
- incomplete extraction, traversal, or ref selection;
- intentional scope removal established by repository-local authority; and
- contradictory evidence.

The absence of discovered counterevidence is not proof of absence unless the applicable search dimensions are complete.

## Unknowns

Unknowns are structured records identifying the unresolved proposition, why it remains unresolved, affected conclusions, missing evidence, and a bounded review question where applicable.

## Judgment

Allowed initial judgment values are:

```text
true-regression
authorized-change
divergence
valuable-alternative
false-positive
insufficient-evidence
unresolved
```

A judgment records the policy, policy version, inputs, rationale references, and assessor. `Unresolved` is a valid result. Detection of a finding is represented in case data and is distinct from failure to execute analysis.

## Completeness

The case includes a `CompletenessDeclaration` for relevant dimensions, including graph traversal, selected refs, state capture, artifact coverage, lineage resolution, semantic extraction, obligation coverage, counterevidence search, and external context.

Allowed values distinguish at least complete, partial, unavailable, not-requested, and not-applicable. Dimension-specific detail records scope, omissions, and consequences.

## Reproduction

The `ReproductionManifest` records the exact repository identities, resolved refs, captured provisional states, comparison and traversal configuration, extractors and versions, obligation set, configuration digest, and schema version needed to reproduce the case.

Mutable ref names may be included as locators but never substitute for captured immutable targets.

## Evidence inventory

The inventory lists every evidence item directly included or referenced by the case and identifies omitted evidence through retrievable identities when selection or compression is used.

## Closure

A case is closed for deterministic judgment only when the configured policy's authority, evidence, counterevidence, and completeness prerequisites are met. Otherwise it remains an inspectable unresolved case rather than being silently discarded.
