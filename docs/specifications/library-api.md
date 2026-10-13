# Library API

## Purpose

This specification defines the intended narrow public library use cases. Exact Python names remain provisional until implementation proves them, but the input, output, and side-effect boundaries are controlling.

## API principles

The public API is:

- use-case-oriented rather than utility-oriented;
- explicit about repository, state, traversal, and diff inputs;
- typed around domain requests and results;
- read-only with respect to analyzed repositories;
- independent of argparse, stdout, stderr, and process exit status;
- free of ambient mutable defaults that cannot be represented in reproduction metadata; and
- capable of dependency injection through domain-owned ports.

A universal `analyze(repository)` operation is not part of the initial public contract.

## Initial use cases

### Capture states

Conceptual operation:

```text
capture_states(request, repository_reader) -> CapturedStates
```

Resolves committed states and captures requested provisional states. The result includes identities, manifests, completeness, and diagnostics as data.

### Compare states

Conceptual operation:

```text
compare_states(request, transition_reader) -> StateComparison
```

Compares explicit captured endpoints using recorded diff options. It does not infer ancestry from endpoint names.

### Construct transitions

Conceptual operation:

```text
construct_transitions(request, repository_reader) -> TransitionSet
```

Constructs parent-specific or explicitly requested historical transitions under recorded traversal policy.

### Extract facts

Conceptual operation:

```text
extract_facts(request, extractors) -> FactExtractionResult
```

Extracts attributed facts from exact artifact evidence. Unsupported input and partial extraction remain explicit.

### Evaluate obligations

Conceptual operation:

```text
evaluate_obligations(request, evaluators) -> ObligationEvaluationSet
```

Evaluates explicit obligations against captured facts and authority evidence. It returns unresolved evaluations when prerequisites are unavailable.

### Build cases

Conceptual operation:

```text
build_cases(request) -> CaseSet
```

Builds bounded cases from referenced observations, interpretations, obligations, evaluations, counterevidence, completeness, and reproduction records.

## Profile service

The state-awareness profile composes the initial use cases through a typed request and result. Profile services may offer convenience at the application boundary while preserving every explicit input in the resulting manifest.

## Errors and diagnostics

Programming errors and invalid requests may raise documented library exceptions. Expected analytical conditions, unsupported optional capabilities, partial extraction, findings, and unresolved judgments are represented in typed results and diagnostics.

Library exceptions never encode a detected regression merely to force a nonzero process exit.

## Output sinks

The library returns domain or serialization results. Writing to a file, byte stream, memory buffer, or other explicit sink is performed by a caller-selected adapter. The library does not assume that output is a filesystem path.

## Evolution rule

Names become stable only after the first implementation and acceptance fixtures demonstrate coherent boundaries. Convenience functions may be added only when they preserve the explicit request, reproduction, completeness, and diagnostic contracts.
