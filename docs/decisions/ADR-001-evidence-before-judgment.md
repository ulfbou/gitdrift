# ADR-001: Evidence before judgment

## Status

Accepted for the documentation inception baseline.

## Context

Git repositories expose commits, trees, blobs, refs, the index, the working tree, and parent transitions. These sources can establish what changed, but they do not by themselves establish whether a change is a semantic regression.

A deleted file may have been replaced. A large rewrite may preserve every obligation. A one-word change may weaken a normative contract. A branch may contain unique commits but no unique value, while an abandoned branch may preserve a fact lost from the controlling line.

Humans and AI require enough information to distinguish observation, interpretation, active obligation, assessment, and final judgment.

## Decision

Gitdrift will construct evidence-complete cases before applying judgment.

Each case separates:

1. observations directly established by repository evidence;
2. interpretations derived by named extractors or assessors;
3. obligations, authorities, scopes, and activation conditions;
4. assessments of how a state or transition relates to an obligation;
5. judgment, including unresolved or insufficient-evidence outcomes.

Cases include supporting evidence, counterevidence, alternatives, unknowns, completeness limits, and reproduction metadata.

No heuristic or AI assessment may silently become a repository fact. No branch name, recency signal, change size, or file deletion independently proves regression.

## Consequences

### Positive

- findings are inspectable and reproducible;
- humans and AI can challenge individual links in a conclusion;
- uncertainty remains explicit;
- the same evidence supports text, JSON, SARIF, and later DX export;
- deterministic and inferential components can evolve independently.

### Costs

- the native model is richer than a conventional diff report;
- extractors and policies must retain provenance;
- unresolved cases are expected and are valid outputs;
- schema and compatibility discipline are required early.

## Rejected alternatives

### Single risk score

Rejected because it hides evidence dimensions and creates false precision.

### AI-only semantic classification

Rejected because repository facts, authority, and completeness must remain independently verifiable.

### Raw diff as the primary product

Rejected because raw patches do not express obligation strength, counterevidence, supersession, or semantic lineage.
