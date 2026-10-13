# ADR-006: External products are evidence boundaries

## Status

Accepted.

## Context

`dx-artifacts` and `Dx.Domain` are formative Gitdrift acceptance corpora. They expose state-awareness, divergence, lineage, and obligation problems that Gitdrift must analyze.

They are independent products with different responsibilities and, in the case of `Dx.Domain`, a different runtime platform. Treating either repository as a Gitdrift runtime submodule would confuse evidence under analysis with implementation dependency.

## Decision

`dx-artifacts` and `Dx.Domain` remain independent products and repository evidence boundaries.

Gitdrift does not depend on their source trees, import their internal implementations, or require Git submodules containing them at runtime.

They may be used as:

- immutable or reproducibly constructed acceptance corpora;
- integration fixtures selected outside the distributable runtime;
- sources of domain obligations and repository evidence; and
- interoperability partners through explicitly versioned, language-neutral contracts.

Future integration may use native JSON, JSON Schema, SARIF, subprocess protocols, or optional DX evidence transport after those boundaries are specified. Such adapters remain optional and downstream from the Gitdrift semantic kernel.

## Consequences

### Positive

- Gitdrift remains independently installable and testable;
- analyzed repositories do not become trusted implementation extensions;
- Python and .NET runtime concerns remain separated;
- acceptance evidence can be pinned without coupling production code to fixture layout;
- DX transport cannot redefine native Gitdrift semantics.

### Costs

- acceptance fixtures require explicit acquisition and identity management;
- cross-product integration requires versioned data contracts;
- no implementation reuse is assumed merely because products model related concepts.

## Rejected alternatives

### Runtime Git submodules

Rejected because source pinning does not create a stable language or product boundary and would couple installation to repository layout.

### Direct dependency on dx-artifacts for the core

Rejected because DX export is deferred and optional. The repository-analysis kernel must operate without carrier-format dependencies.

### In-process dependency on Dx.Domain

Rejected because Gitdrift is a Python product and `Dx.Domain` is an independent .NET product. Their useful relationship is evidence and interoperability, not shared runtime implementation.
