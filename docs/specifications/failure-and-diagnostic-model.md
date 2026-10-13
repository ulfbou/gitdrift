# Failure and diagnostic model

## Purpose

This specification separates analytical outcomes from execution conditions and establishes stable machine-readable diagnostics.

## Outcome categories

### Completed

All requested required capabilities executed and the result represents its declared completeness. Findings, including verified regression, do not make execution fail.

### Completed unresolved

Analysis completed successfully but evidence or authority does not permit a final judgment. Unresolved is an analytical result.

### Completed partial

A valid native result was produced, but one or more requested dimensions are partial, unavailable, truncated, or unsupported. Diagnostics identify the effect on completeness.

### Unsupported input or capability

The request, repository feature, artifact kind, schema version, or required capability is not supported. Existing evidence is preserved when a truthful partial result can be emitted.

### State changed during capture

The index, working tree, ref, or other provisional input changed during acquisition such that reproducible capture could not be established under the retry policy.

### Evidence unavailable

A required object, snapshot, path, external record, or retrievable payload could not be acquired. Absence of acquisition is not semantic absence.

### Invalid configuration or request

Input violates its schema, compatibility rules, path safety, capability constraints, or required invariants.

### Internal execution failure

An unexpected implementation failure prevented safe completion. It is not represented as an empty investigation or analytical finding.

## Diagnostic record

Every diagnostic contains:

```text
stable diagnostic code
severity
category
message
affected request, state, artifact, or record IDs
producer and version
supporting exception class or adapter status when safe
retryability when explicitly known
completeness effects
related diagnostics
```

Human-readable messages are not stable identifiers.

## Severity

Initial severities are informational, warning, error, and fatal. Severity describes execution or interpretation impact. It does not map directly to finding severity or judgment.

## Findings versus diagnostics

A regression, divergence, nugget candidate, contradiction, or unresolved case belongs in native analytical records. Diagnostics describe acquisition, validation, capability, execution, serialization, or sink conditions.

## Partial-result rule

A partial native result may be emitted only when retained records remain truthful, references resolve, affected completeness is reduced, and diagnostics identify omitted or failed work. Required-root corruption, incompatible native schema, or unsafe identity ambiguity prevents successful artifact emission.

## Process mapping

Library operations return typed results and documented exceptions. A CLI adapter maps execution categories to exit status while keeping a successfully represented finding separate from process failure.

## Security

Diagnostics avoid secrets, arbitrary repository-content execution, uncontrolled path disclosure, and unnecessary personal data. Raw parser or subprocess output is bounded and attributed.
