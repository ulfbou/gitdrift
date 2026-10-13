# Analysis pressure and purity

## Purpose

This specification defines transparent dimensions for selecting analytical attention and describing evidence composition. Pressure and purity are projections over existing evidence, provenance, completeness, and resource records. They are not regression, correctness, authority, or quality judgments.

## Core rule

```text
pressure selects analytical attention
obligations and evidence determine regression
```

No pressure or purity value may independently finalize a finding or judgment.

## Pressure dimensions

### Transition pressure

Describes the volume and concentration of relevant transitions within a declared subject and window. It records counts, window, filters, and suppressed mechanical transitions separately.

### Branch pressure

Describes the number and relationships of selected divergent, unmatched, or independently evolving histories relevant to the subject. Branch count alone is not risk.

### Artifact overlap

Describes how many selected states change or contain corresponding artifacts, fragments, or symbols. Overlap is structural evidence, not semantic conflict.

### Semantic overlap

Describes corresponding concepts, facts, obligations, or representation roles affected across states. Extraction and correspondence completeness remain explicit.

### Authority dispersion

Describes the distribution of active or candidate authority representations across artifacts and states, including unresolved conflict and duplicated authority. Dispersion is not automatically harmful.

### Representation fragmentation

Describes one-to-many, many-to-one, residual, duplicated, divergent, and unaccounted representations according to the fragmentation contract.

### Unresolved-equivalence pressure

Describes material correspondence candidates whose equivalence, strength, contradiction, replacement, or supersession remains unresolved.

### Evidence impurity

Describes dependence on non-observed evidence classes and external context. Impurity does not mean invalidity; it indicates which transformations and assessments require inspection.

### Coverage deficit

Describes completeness dimensions that are partial, unavailable, or not requested and could affect the analytical question.

## Dimension record

Every pressure dimension records:

```text
dimension identity and kind
subject and scope
window or compared states
input evidence and record IDs
method and configuration
raw measures
normalization, if any
result value
producer and version
limitations
completeness
```

Raw measures remain available when a categorical or normalized projection is emitted.

## Purity vector

Purity is represented as independently inspectable contribution dimensions:

```text
observed evidence
deterministic computation
heuristic inference
AI-assisted assessment
human-supplied judgment
external context
```

Each contribution references the records and transformations it summarizes. A purity vector does not rank one evidence class as morally or universally superior. It describes dependency composition.

## Composite projections

A composite pressure view may be introduced only when it is:

- explicitly named and versioned;
- defined by a published formula;
- traceable to all source dimensions and raw measures;
- reversible into independently inspectable dimensions;
- accompanied by limitations and calibration scope; and
- prohibited from acting as a regression verdict.

The label `DPI` is reserved for such a future named projection. It must not silently change meaning between Drift Pressure Index and Dependency or Decision Pressure Index.

## Use cases

Pressure may prioritize subjects, choose windows, allocate resource budgets, order review candidates, or trigger deeper extraction. Purity may inform review routing, explain conclusion dependencies, or expose where deterministic reproduction ends.

## Constraints

- High pressure does not imply regression.
- Low pressure does not prove safety.
- High observed-evidence proportion does not prove correctness.
- AI or human contribution does not invalidate a case when attributed properly.
- Missing coverage cannot be hidden by normalization.
- Pressure and purity never replace completeness, confidence, authority, or judgment policy.
