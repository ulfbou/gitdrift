# ADR-003: Native JSON is canonical

## Status

Accepted.

## Context

Gitdrift must serve libraries, automation, humans, editors, CI systems, and later evidence transports without allowing presentation formats to redefine evidence or judgment semantics.

Human text and Markdown optimize review. SARIF targets interoperability. DX may later transport closed evidence packages. None can represent the complete native investigation by assumption.

## Decision

Native Gitdrift JSON is the authoritative serialized representation of investigations, evidence, obligations, evaluations, cases, completeness, reproduction, and judgments.

Human text, Markdown, JSON Lines, SARIF, and DX are derived projections, streams, interoperability exports, or transports. They do not own semantic identity or originate decisions.

The native schema is versioned independently from the Python package and from any transport format. A serializer records the schema identifier and version it emits.

For a CLI adapter:

- stdout carries the requested machine-readable result;
- stderr carries diagnostics and progress;
- a detected finding is represented in the result model;
- exit status reports execution outcome, invalid input, unsupported capability, or serialization failure according to the CLI contract; and
- renderers do not perform obligation evaluation or judgment.

These CLI rules establish direction for future contracts without freezing the complete command surface.

## Consequences

### Positive

- one native model controls meaning across projections;
- schema validation can protect machine consumers;
- diagnostics cannot silently corrupt artifact streams;
- transport adapters remain downstream;
- schema compatibility can evolve independently from package releases.

### Costs

- projections must declare omitted native information;
- schema evolution requires explicit compatibility discipline;
- streaming and interoperability formats may need loss declarations or references to the complete native artifact.

## Rejected alternatives

### Human output as the primary contract

Rejected because prose is not a complete or reliably composable evidence interface.

### SARIF as the native model

Rejected because Gitdrift's repository states, histories, lineages, obligations, cases, and completeness exceed a findings-only interoperability projection.

### DX as the native model

Rejected because transport framing must not own Gitdrift evidence identity or judgment semantics.

### Renderer-specific decisions

Rejected because the same native investigation must produce semantically consistent projections.
