# Non-goals

## Purpose

This document protects Gitdrift from scope drift by distinguishing permanent product prohibitions from capabilities intentionally deferred until their evidence and contracts are mature.

A permanent non-goal may not enter the product without an explicit product-boundary decision. A not-now goal may be added later without contradicting product identity when its prerequisites and acceptance boundary are specified.

## Permanent non-goals

### Workplace performance evaluation

Gitdrift does not evaluate developer, team, manager, or organizational productivity, competence, intent, behavior, or performance. Repository activity is evidence about repository evolution, not a proxy for people.

### Organizational surveillance

Gitdrift does not construct employee monitoring, authorship ranking, behavioral profiling, or organizational-control systems from repository evidence.

### General-purpose forensics

Gitdrift does not perform disk, memory, malware, intrusion, host, or incident forensics. Its forensic scope is repository evolution required to reconstruct lineage, alignment, divergence, and regression provenance.

### Automatic human-intent inference

Gitdrift does not infer why a person made a change unless an attributed evidence source explicitly expresses that rationale. Commit timing, branch naming, authorship, and textual style do not establish intent.

### Convenience signals as authority

Gitdrift does not treat branch names, default-branch status, recency, popularity, commit distance, author identity, or merge status as authority.

### Replacing Git

Gitdrift does not replace Git storage, object identity, history, refs, merging, or repository administration. It analyzes captured repository evidence through read-only adapters.

### Repository mutation from the analytical core

The analytical core does not checkout, commit, merge, rebase, reset, patch, repair, update refs, alter the index, modify working-tree files, or change repository configuration.

### Autonomous semantic truth

Gitdrift does not promise autonomous determination of meaning. It produces traceable evidence, interpretations, obligations, assessments, cases, and policy-governed judgments with uncertainty preserved.

### Opaque composite verdict scoring

Gitdrift does not use an unexplained single risk, health, drift, pressure, or purity number as proof of regression, authority, correctness, or quality.

## Not-now goals

The following are deferred capabilities, not permanent prohibitions:

- forge metadata such as issues, pull requests, reviews, labels, milestones, project boards, and hosted checks;
- SARIF export;
- verified DX evidence export;
- AI-assisted assessment in the implemented product;
- automatic concept clustering;
- automatic fixes or repair recommendations;
- hosted-service integration;
- checkpoint persistence;
- JSON Lines streaming;
- a public plugin or extractor SDK;
- generalized automatic split and merge inference;
- cross-language semantic lineage; and
- exposed composite projections over independently inspectable pressure dimensions.

## Admission rule for deferred capabilities

A deferred capability may enter scope only when:

1. its evidence domain and trust boundary are explicit;
2. its native data contract is defined;
3. its effect on provenance, completeness, reproduction, and compatibility is specified;
4. it cannot silently redefine established evidence, authority, or judgment semantics;
5. its failure and partial-analysis behavior is machine-readable; and
6. acceptance scenarios establish read-only and non-regression guarantees where applicable.

## Boundary principle

Git evidence establishes what repository states contain and how they changed. Semantic analysis establishes what represented facts and obligations changed. External context may later help explain a case, but it cannot silently rewrite repository evidence or controlling authority.
