# Library and adapter boundaries

## Purpose

This document defines the boundary between Gitdrift's domain kernel, application services, ports, infrastructure adapters, serializers, profiles, and CLI. The purpose is to preserve one semantic core while permitting replaceable acquisition and presentation mechanisms.

## Architectural units

### Domain kernel

The domain kernel owns stable meanings for repository states, transitions, artifact snapshots and lineages, fragments, concepts, facts, obligations, evaluations, cases, completeness, reproduction, and judgments.

The domain kernel:

- contains no subprocess management;
- contains no CLI parsing;
- performs no terminal output;
- depends on no hosted forge;
- depends on no DX or SARIF framing; and
- does not read ambient repository configuration directly.

### Application services

Application services implement explicit use cases by coordinating domain records and domain-owned ports. They establish transaction-like analysis boundaries, propagate completeness, and return typed results.

Application services may select capabilities and compose layers. They may not redefine domain identity, silently substitute unavailable evidence, or convert heuristic claims into observations.

### Domain-owned ports

Ports express capabilities required by the domain and application layers, including:

```text
repository state resolution
object and snapshot reading
provisional-state capture
transition and change-set construction
fact extraction
obligation-set loading
schema validation
explicit output writing
```

Ports use domain-oriented inputs and outputs. They do not expose subprocess exit codes, argparse namespaces, provider SDK objects, or transport-specific framing to the domain.

### Git adapter

The Git adapter implements repository-reading ports. It resolves refs, reads commits, trees and blobs, captures index and working-tree evidence, and constructs raw changes using explicit configuration.

Git command details, library-specific objects, environment handling, and process diagnostics remain inside the adapter. The adapter never decides semantic equivalence, authority, regression, or judgment.

### Parser and extractor adapters

Parser adapters convert exact artifact evidence into structured representations. Extractors produce attributed semantic facts and declarations of support, determinism, confidence, and limitations.

An unsupported artifact remains exact repository evidence. Parser failure cannot be represented as semantic absence.

### Serializers and validators

Native JSON serializers map accepted domain records to the canonical schema without changing meaning. Validators report schema conformance. Human text, Markdown, JSON Lines, SARIF, and future DX exporters are downstream projections or transports.

A serializer does not evaluate obligations, select authority, or finalize judgments.

### Profiles

Profiles select traversal scope, analytical depth, capability requirements, case-selection rules, and output projection. They orchestrate application services rather than reaching directly into infrastructure adapters.

A profile may require capabilities, accept degraded execution, or reject unsupported requests according to its contract. Any degradation is reflected in completeness and diagnostics.

### CLI adapter

The CLI translates process inputs into application requests and translates application results into an explicit output sink. It owns argument parsing, standard-stream behavior, process diagnostics, and exit-status mapping.

The CLI does not own domain defaults that library callers cannot express. CLI convenience options expand into explicit application requests before analysis begins.

## Dependency rules

The allowed direction is:

```text
CLI and presentation adapters
            |
profiles and application services
            |
domain kernel and domain-owned ports
            ^
infrastructure adapters implement ports
```

The domain and application layers never import the CLI. Infrastructure adapters may depend on domain contracts to implement ports, but domain contracts never import adapter implementations.

## Prohibited dependencies

The following are prohibited:

- domain records importing Git subprocess wrappers;
- obligation evaluation importing renderers;
- case construction importing DX or SARIF libraries;
- application services accepting argparse objects;
- library operations writing to stdout or stderr;
- serializers performing repository acquisition;
- profiles bypassing ports to invoke external tools directly;
- adapters mutating repository state as a side effect of analysis; and
- external acceptance corpora becoming required runtime submodules.

## Composition root

A composition root selects adapters, capabilities, configuration, and profiles. The CLI may provide one composition root, while tests and embedding applications provide others.

Construction failures are explicit capability or configuration errors. They are not converted into empty investigations.

## Testing boundary

Domain behavior is testable with in-memory port implementations and immutable fixtures. Adapter conformance tests prove that concrete implementations preserve domain identities, exact evidence, diagnostics, and read-only guarantees.
