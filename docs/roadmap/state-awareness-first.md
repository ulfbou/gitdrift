# State-awareness-first roadmap

## Milestone

```text
Gitdrift 0.1: repository-state alignment and provenance
```

The milestone builds the first narrow slice of the reusable Gitdrift library through the `dx-artifacts` state-awareness profile.

## Required outcome

Given a repository with `HEAD`, an optional configured upstream, staged changes, and working-tree changes, Gitdrift produces a schema-valid native investigation that:

1. identifies every selected state immutably or by reproducible capture;
2. records the exact comparisons performed;
3. reports changed paths and available structural facts;
4. separates staged and unstaged changes;
5. identifies overlap and unique changes across candidate states;
6. evaluates explicitly declared obligations supported by implemented extractors;
7. creates judgment-ready cases with supporting evidence, counterevidence, unknowns, and completeness;
8. performs no repository mutation.

## Initial reusable components

```text
gitdrift.model
  repository states
  transitions
  artifact snapshots
  raw and structural changes
  evidence references

gitdrift.git
  repository reader port
  Git adapter
  ref resolver
  state materializer
  transition reader

gitdrift.diff
  change sets
  path changes
  content deltas
  explicit diff options

gitdrift.extract
  extractor protocol
  Markdown section extractor
  Python symbol extractor
  extracted facts

gitdrift.obligations
  obligation model
  evaluation model
  deterministic evaluator protocol

gitdrift.cases
  case model
  case builder
  completeness and reproduction metadata

gitdrift.formats
  native JSON writer
  JSON Schema validation

gitdrift.profiles.state_awareness
  request
  result
  application service
```

Names are architectural placeholders until the package design is accepted. The domain boundaries, not these exact Python module names, are controlling.

## Acceptance scenarios

### Linear history with staged architecture migration

The profile distinguishes `HEAD`, upstream, index, and worktree; compares the staged candidate independently from the remote-only candidate; and does not require integration before analysis.

### No staged or unstaged changes

The profile emits a valid result describing the available committed states and explicitly records non-applicable provisional comparisons.

### Partial extractor support

Unsupported content remains available as exact evidence. Semantic extraction is marked partial rather than silently treated as complete.

### Ambiguous semantic change

The profile produces an unresolved case with a bounded review question instead of asserting regression.

## Explicitly deferred

The milestone does not include:

```text
all-branch archaeology
complete file-history reconstruction
split and merge inference
concept clustering
adaptive historical epochs
SARIF export
DX evidence export
AI assessment
forge integration
repository mutation
automatic fixes
composite risk scoring
```

The model must permit these additions without changing the evidence-before-judgment principle.

## Following milestones

### Gitdrift 0.2: branch divergence and nugget provenance

Prove multi-branch traversal and semantic comparison against `Dx.Domain`, including alternate chains, patch correspondence, convergence, and candidate gold nuggets.

### Gitdrift 0.3: file lineage and regression provenance

Add complete selected file histories, parent-specific merge transitions, first-violation localization, region and symbol lineage, and restoration tracking.

### Gitdrift 0.4: accretion and fragmentation forensics

Add cumulative windows, semantic accretion cases, one-to-many and many-to-one lineage candidates, dispersal accounting, residue, duplication, and loss analysis.

### Later interoperability

Add SARIF and optional DX evidence carriers only after the native evidence and case contracts are stable enough to export without loss.
