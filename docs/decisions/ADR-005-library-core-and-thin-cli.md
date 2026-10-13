# ADR-005: Library core and thin CLI

## Status

Accepted.

## Context

Gitdrift needs a command-line interface for reproducible local and automated use, but its reusable product semantics must remain available to tests, embedding applications, and future adapters without process coupling.

Placing analysis behavior in command handlers would bind the product to argparse objects, standard streams, subprocess exit semantics, and one composition root.

## Decision

The Gitdrift Python library is the product core. The CLI is a thin adapter over typed application use cases and profile services.

The library owns:

- domain identities and records;
- repository-state and transition semantics;
- fact, obligation, evaluation, and case contracts;
- completeness and reproduction semantics;
- profile orchestration; and
- canonical native serialization behavior.

The CLI owns:

- process argument parsing;
- input-manifest loading;
- composition-root selection;
- standard-stream and explicit-sink behavior;
- process diagnostics; and
- exit-status mapping.

No public library operation accepts argparse objects, writes diagnostics to standard streams, or terminates the process.

## Consequences

### Positive

- library callers and the CLI use the same semantic operations;
- domain behavior can be tested without subprocesses;
- additional adapters can reuse the kernel;
- CLI evolution does not redefine evidence or judgment.

### Costs

- process concerns require explicit translation at the adapter boundary;
- typed request and result models must be maintained;
- convenience behavior cannot remain implicit in CLI handlers.

## Rejected alternatives

### CLI-first implementation with later extraction

Rejected because domain boundaries would be shaped by process concerns and implicit command defaults.

### Library without a CLI adapter

Rejected because reproducible local and automation workflows still require a supported process interface.

### Shared untyped utility functions

Rejected because reuse must preserve domain meaning, provenance, completeness, and side-effect boundaries.
