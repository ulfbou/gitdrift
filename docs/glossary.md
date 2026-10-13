# Glossary

## Purpose

This glossary controls Gitdrift terminology across vision, architecture, specifications, schemas, diagnostics, profiles, and acceptance material. A domain term must not acquire a conflicting local meaning without an explicit specification change.

## Repository evidence

### State

An immutable or reproducibly captured view of relevant repository content. State kinds include commits, captured branch tips, the index, the working tree, explicit snapshots, and synthetic analytical states.

### Snapshot

The exact representation of an artifact at one state, including content identity, path, mode or kind, and exact bytes or a retrievable evidence reference.

### Transition

An ordered relation between two states under declared comparison semantics. Only a parent-to-child transition inherently asserts ancestry.

### History path

An ordered selection of states or parent edges under an explicit traversal and parent policy. A history path is not necessarily the only ancestry path between endpoints.

## Structural evolution

### Artifact

A repository representation treated as a meaningful structural subject. A path is an artifact location, not durable artifact identity.

### Artifact instance

An artifact representation bound to one state, snapshot, and location.

### Lineage

An evidence-backed graph relating artifact, fragment, or concept representations across states. A lineage may branch, merge, split, remain unresolved, or contain competing relation candidates.

### Fragment

A bounded region or structural element within an artifact snapshot, such as a Markdown section, code symbol, requirement, configuration entry, test, or explicit byte range.

### Restoration

A supported relation in which a later representation restores an earlier artifact, fact, or obligation satisfaction after an intervening absence, replacement, or violation.

### Reintroduction

A later equivalent representation whose provenance is not sufficiently connected to an earlier representation to establish restoration. Independent reintroduction preserves distinct provenance.

## Semantic representation

### Concept

A stable semantic subject independent of any one path, file, wording, branch, or implementation language.

### Concept representation

One or more fragments representing a concept at a state, each with an explicit role such as authority, specification, implementation, enforcement, explanation, navigation, historical evidence, or generated derivation.

### Fact

A meaning-bearing assertion observed, computed, extracted, inferred, AI-assisted, or human-supplied about repository evidence. Its evidence class, producer, inputs, method, and limitations remain explicit.

### Fact delta

An attributed interpretation describing how corresponding facts differ across a comparison or transition. Raw snapshots and changes remain the underlying evidence.

## Alignment and judgment

### Obligation

An explicit relation that must hold among identified subjects under declared authority, scope, activation, retirement, and supersession rules.

### Authority

Evidence establishing which source or decision controls an obligation or interpretation within a declared scope. Authority is never inferred solely from branch name, recency, popularity, authorship, or location.

### Assessment

An attributed conclusion about evidence, interpretations, obligations, or a bounded question. Assessments are deterministic, heuristic, AI-assisted, or human-supplied and never become observed evidence silently.

### Finding

A machine-readable analytical result warranting attention. A finding may describe difference, overlap, possible regression, unresolved authority, or another case condition. A finding is not automatically a final judgment.

### Case

A bounded, judgment-ready projection around one question and subject containing observations, interpretations, obligations, assessments, alternatives, supporting evidence, counterevidence, unknowns, completeness, and reproduction metadata.

### Judgment

A policy-governed classification applied to a case after required evidence, authority, counterevidence, and completeness prerequisites are evaluated.

### Regression

A policy-governed conclusion that an established active obligation became weaker, violated, or contradictory across an identified state comparison or transition without accepted retirement or supersession.

### Divergence

A difference between selected histories, states, facts, or obligation evaluations. Ordinary graph divergence and semantic divergence do not independently establish regression.

### Overlap

A condition in which compared states change or represent the same relevant path, artifact, fragment, concept, fact, or obligation subject. Overlap selects deeper analysis and is not a verdict.

### Convergence

A condition in which alternate histories arrive at equivalent relevant facts or obligation satisfaction while retaining distinct provenance.

### Gold nugget

A semantically relevant fact present in a candidate state, absent from the controlling state within sufficient scope, and not represented there equivalently or more strongly.

### Supersession

An attributed, authority-backed relation in which a replacement obligation, fact, or representation becomes effective for an identified scope. Newness, deletion, or similarity alone does not prove supersession.

## Evidence quality and prioritization

### Completeness

A dimension-specific declaration of analyzed coverage. Completeness values distinguish complete, partial, unavailable, not requested, and not applicable. Completeness is not confidence.

### Confidence

An attributed assessor's strength of support for a derived conclusion. Confidence cannot strengthen incomplete evidence or establish authority.

### Purity

A transparent description of how an evidence set or conclusion depends on observed evidence, deterministic computation, heuristics, AI assistance, human judgment, and external context. Purity is multidimensional and is not correctness.

### Pressure

A transparent analytical-attention signal derived from inspectable dimensions such as transition volume, branch divergence, artifact overlap, semantic overlap, authority dispersion, fragmentation, unresolved equivalence, evidence impurity, or coverage deficit. Pressure selects analysis and is not a regression verdict.
