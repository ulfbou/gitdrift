# CLI contract

## Purpose

This specification defines the initial process-level contract for a thin Gitdrift CLI adapter without freezing the complete future command surface.

## Structured output

Machine-readable native JSON is the default product output for analytical commands. Human rendering is explicit and derived from the same native result.

The CLI does not mix progress, warnings, or explanatory prose into a requested machine-readable stream.

## Standard streams

```text
stdout: requested result artifact when no explicit output sink is selected
stderr: diagnostics, validation failures, and optional progress
```

When an explicit output sink is selected, stdout behavior is command-defined and must not duplicate or corrupt the artifact implicitly.

## Exit status semantics

Exit status reports process execution outcome, not whether the investigation contains a finding.

The initial categories distinguish:

```text
successful execution
invalid invocation or request
unavailable required capability
repository acquisition or capture failure
analysis execution failure
serialization or validation failure
output sink failure
```

Exact numeric assignments remain an implementation detail until accepted with the CLI skeleton. A successfully represented regression or unresolved case is still a successful execution unless an explicit policy-check command later defines a separate gate contract.

## Discovery

The CLI exposes machine-readable schema and capability discovery backed by the installed composition. Discovery results follow [capability discovery](capability-discovery.md) and do not advertise planned but unavailable adapters.

## Input manifests

Commands may accept an explicit request or input manifest. The manifest controls repository location, selected states, traversal, diff options, extractors, obligations, comparison matrix, and output requirements supported by the chosen profile.

CLI flags expand into the same request model. When both are permitted, precedence is explicit and reproduced in the analysis manifest.

## Output sinks

The CLI supports stdout and may support an explicit file sink. A sink is selected before execution. Artifact bytes are delivered completely to that sink or the command reports failure; partial output is not described as a successful artifact.

## Human rendering

Human text or Markdown is opt-in. Renderers consume accepted native results and may summarize, select, or reorder information only while declaring omissions and preserving stable references to native identities.

## Initial command boundary

The first CLI surface exposes only what is required to discover capabilities and run the state-awareness profile. It does not stabilize the full future command list discussed during product discovery.

Conceptually required interactions are:

```text
discover installed capabilities
discover supported native schemas
run state-awareness from explicit inputs
validate or emit the native result
optionally render a human projection
```

Exact command names and flags remain provisional until implementation acceptance.

## Read-only behavior

Analytical commands do not modify refs, commits, the index, working-tree files, repository configuration, hooks, or hosted metadata. Output writes only to the selected sink.

## Diagnostics

Diagnostics have stable machine codes in native results or structured diagnostic output where defined. Human messages are explanatory and are not machine contracts. Secrets, credentials, and unrelated environment data are not emitted.
