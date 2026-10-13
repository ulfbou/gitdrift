# Ref selection and controlling state

## Purpose

This specification defines explicit baseline selection, local and remote ref capture, controlling-state identity, and selected-ref completeness for divergence analysis.

## Controlling state

A controlling state is the state against which candidate facts, obligations, and histories are evaluated. The request identifies it explicitly by resolvable locator or immutable identity.

The captured controlling-state record contains:

```text
state identity
immutable commit, tree, or snapshot identity
input locator, when supplied
capture time evidence
selection method
selection provenance
scope
limitations
```

Selection does not establish universal repository authority. It establishes the comparison boundary for the investigation.

## Prohibited authority inference

Gitdrift does not infer controlling authority solely from:

- branch or tag name;
- default-branch status;
- local versus remote location;
- recency or age;
- commit count or graph distance;
- author or committer identity;
- merge status;
- apparent activity; or
- forge metadata.

Repository-local authority and obligations are evaluated separately.

## Ref selection

A request declares which namespaces and patterns are included, for example selected local branches, selected remote-tracking refs, or an explicit list. Symbolic refs are resolved and their targets captured.

Remote-tracking refs are local repository evidence at capture time. Their names do not prove current hosted-service state, and Gitdrift does not fetch unless a separate acquisition action outside read-only analysis has been explicitly performed.

## Mutable locators and immutable tips

Every selected ref record retains:

```text
full ref name
ref kind
peeled target when applicable
immutable captured tip
symbolic target when applicable
resolution evidence
```

All analysis references the captured immutable target. Later movement of the locator does not rewrite the investigation.

## Selected-ref completeness

Completeness records:

- requested namespaces and patterns;
- enumerated refs;
- excluded refs and reasons;
- unresolved or inaccessible refs;
- duplicate tips under multiple locators;
- whether enumeration was complete for the declared scope; and
- whether external refs were not requested.

A result cannot claim that a fact is absent from all branches unless selected-ref coverage and relevant semantic coverage support that claim.

## Candidate relation to controlling state

Each candidate records equality, ancestor, descendant, divergent, or unresolved reachability relative to the controlling state. This graph relation is descriptive. It does not classify semantic strength or correctness.
