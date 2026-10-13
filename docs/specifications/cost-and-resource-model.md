# Cost and resource model

## Purpose

This specification defines machine-readable accounting, budgets, truncation, and exhaustion behavior for repository analysis. Resource limits may bound work, but partial execution must never masquerade as complete analysis.

## Resource record

Every investigation records applicable resource observations:

```text
repository objects considered
commits and parent edges visited
trees visited
blobs addressed
blobs read
bytes addressed
bytes read
bytes parsed
transitions constructed
comparisons executed
artifacts and fragments analyzed
extractors selected
extractors executed
obligations evaluated
cases constructed
cache lookups, hits, misses, and rejected entries
wall-clock and process measurements when explicitly supported
```

Counts are emitted only when mechanically established. Unknown or unavailable measurements remain explicit rather than estimated silently.

## Budget dimensions

A request may declare independent limits for:

```text
objects
commits
parent edges
history depth
refs
blobs
bytes read
bytes parsed
transitions
comparisons
extractor executions
obligation evaluations
cases
time when supported
memory when supported
output size
```

A missing budget means governed by the active composition's declared policy, not unlimited by assumption. Capability discovery reports which dimensions can be enforced and measured.

## Analysis depth

Depth is an explicit request and result property. Initial depth classes may distinguish:

```text
repository evidence
structural evolution
semantic extraction
obligation evaluation
case construction
judgment
```

Stopping at a shallower layer is not failure when requested. Budget-forced omission of a requested layer reduces completeness and produces diagnostics.

## Exhaustion behavior

When a budget is exhausted, the implementation must:

1. stop the affected work safely at a defined boundary;
2. preserve valid evidence already acquired;
3. report the exhausted dimension and configured limit;
4. inventory omitted or unattempted work when mechanically knowable;
5. reduce every affected completeness dimension;
6. avoid repository-wide absence or equivalence claims; and
7. emit a schema-valid partial result when truthful representation remains possible.

If safe identity, reference integrity, or required-root serialization cannot be preserved, execution fails explicitly rather than producing a misleading artifact.

## Truncation

Truncation records:

```text
truncation identity
resource or selection boundary
last completed unit
omitted range or inventory
reason
affected records and questions
completeness effects
resume or expansion identity when supported
```

Truncated collections are never indistinguishable from complete empty collections.

## Cost classes

Capabilities may declare descriptive cost classes for planning and selection. Cost class is not a performance guarantee and cannot replace observed accounting.

Cost classes may consider expected graph breadth, history depth, bytes, parser complexity, semantic extraction, inference, or external assessment. Their criteria and versions are discoverable.

## Cache accounting

Resource records distinguish work performed from work reused. A cache hit records the cache key identity, producer version, validated semantic inputs, source artifact identity, and any verification performed.

Cache reuse cannot improve completeness beyond the completeness of the cached result and current request scope.

## Reproduction

The reproduction manifest includes requested budgets, active resource policy, enforced and unsupported limits, observed usage, truncation, cache behavior, and diagnostics.

## Pressure integration

Pressure dimensions may guide budget allocation or select deeper analysis. Pressure does not silently override caller budgets, completeness rules, or judgment prerequisites.

## Safety constraints

Resource enforcement must not mutate analyzed repository state, execute repository content, follow unsafe paths, or omit diagnostics to conserve output. Oversized or adversarial repositories produce bounded evidence and explicit limitations.
