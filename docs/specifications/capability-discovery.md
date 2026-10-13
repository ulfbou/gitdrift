# Capability discovery

## Purpose

Capability discovery lets library callers, automation, and the CLI determine what an installed Gitdrift composition can execute without probing through failed analyses.

## Capability document

Discovery returns a machine-readable capability document containing:

```text
capability schema version
product and package version
native schema versions
state kinds
transition and traversal modes
profiles
extractors
supported artifact kinds
output formats
validation capabilities
determinism classes
confidence classes
cost classes
limitations
```

The document describes the active composition, not every capability that might exist in another installation.

## State and traversal capabilities

State capabilities identify supported committed and provisional state kinds and any capture restrictions. Traversal capabilities identify full ancestry, first-parent, simplified, lineage-selected, merge-base, or other supported modes without implying that every profile exposes every mode.

## Extractor capabilities

Each extractor declaration contains:

```text
stable extractor identity
extractor version
accepted artifact kinds or languages
produced fact kinds
determinism class
confidence classes that may be emitted
cost class
configuration schema identity
known limitations
```

Filename extensions alone do not prove support. Selection follows the extractor's declared matching contract.

## Profile capabilities

Each profile declares:

- stable profile identity and version;
- accepted request schema;
- produced result schema;
- required capabilities;
- optional capabilities;
- supported degradation behavior; and
- explicit exclusions.

A profile is available only when its required capabilities can be composed.

## Output capabilities

Output declarations distinguish canonical native JSON from projections and transports. Each format records schema or format versions, streaming support, loss characteristics, validation support, and available sinks.

DX and SARIF are absent until their adapters are implemented. Planned capability is not reported as available capability.

## Determinism, confidence, and cost

Initial determinism classes are:

```text
deterministic
heuristic
AI-assisted
human-supplied
```

Confidence classes describe attributed derived claims and do not replace evidence completeness. Cost classes are descriptive categories for planning execution; they are not performance guarantees.

## Stability and versioning

Capability identities and discovery schema versions are machine contracts. Human descriptions may evolve without changing meaning. Removing or weakening a declared capability requires compatibility treatment appropriate to the affected contract.

## Failure behavior

Discovery does not mutate repositories and does not require an analysis target unless a target-specific query is explicitly requested. Unavailable optional dependencies produce explicit unavailable capability records or omissions defined by the discovery schema, never fabricated support.
