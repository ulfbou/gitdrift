# Gold-nugget classification

## Purpose

This specification defines candidate gold nuggets and the classifications used to prevent indiscriminate recovery of alternate-branch content.

## Candidate rule

A candidate nugget is a semantically relevant fact present in a candidate state, absent from the controlling state within declared complete-enough scope, and not already represented there equivalently or more strongly.

Candidate selection records the fact, subject, candidate state, controlling state, provenance, relevance basis, counterevidence search, and completeness.

## Classifications

### candidate-nugget

The current evidence supports the candidate rule, but integration or final value judgment remains outside classification unless policy explicitly provides it.

### equivalent

The controlling state already contains a semantically equivalent representation within the relevant scope.

### stronger

The candidate contains a stronger non-contradictory representation than the controlling state. It may remain a candidate nugget when the stronger protection is relevant and absent from controlling state.

### weaker

The candidate representation provides less protection or obligation strength than the controlling state.

### superseded

Repository-local authority establishes that the candidate fact or representation has been replaced and is no longer controlling in the relevant scope.

### historical-only

The fact is valid as historical evidence but is not an active candidate for the controlling state.

### contradictory

The candidate conflicts with a controlling fact or obligation and no accepted supersession resolves the conflict.

### generated-noise

The difference derives from generated or mechanical material under an explicit reversible policy and adds no independently supported semantic fact. Raw evidence remains retained.

### branch-local-scaffolding

The fact serves an alternate branch's temporary or local construction and is not established as a transferable product obligation or capability.

### unresolved

Evidence is insufficient to establish absence, equivalence, strength, supersession, authority, or relevance.

## Classification constraints

- Unique commit, path, or wording is insufficient for `candidate-nugget`.
- `generated-noise` never deletes raw evidence.
- `historical-only` requires evidence about role or applicability, not age alone.
- `superseded` requires explicit authority evidence.
- `stronger` and `weaker` identify the relevant obligation or relation.
- A classification records alternatives and counterevidence.

## Provenance

Each classification references origin evidence, candidate and controlling states, correspondence records, semantic facts, obligation evaluations, assessor class, confidence, and completeness.
