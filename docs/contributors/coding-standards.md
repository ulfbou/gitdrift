# Gitdrift coding standards

## Status

Accepted repository standard.

## Core principles

1. Readability is part of correctness.
2. Evidence, identity, provenance, and limitations are explicit data, not narrative implications.
3. Deterministic operations are reproducible from declared inputs, configuration, versions, and budgets.
4. Gitdrift is read-only by default and must not mutate the repository being investigated.
5. Public behavior and compatibility boundaries are tested before integration.
6. Existing contracts are preserved, explicitly deprecated, or intentionally versioned.
7. Failed, partial, unresolved, unsupported, and complete outcomes remain distinguishable.

## Python

- Support the Python runtime range declared by project metadata and CI.
- Type-annotate supported APIs and stable internal boundaries.
- Prefer immutable value objects for states, evidence, facts, obligations, cases, diagnostics, manifests, and results.
- Keep domain records, acquisition ports, infrastructure adapters, application orchestration, serialization, CLI adaptation, and process termination separated.
- Domain modules must not depend on CLI modules, subprocesses, infrastructure adapters, or process termination.
- Infrastructure adapters implement domain-owned ports; domain code does not import adapters.
- Only process entry points convert returned status into process termination.
- Use argument-vector subprocess calls with `shell=False`, disabled stdin, bounded output, explicit timeouts, and captured diagnostics.
- Never use user-global Git configuration as an unstated test or product dependency.
- Treat repository paths as locations, not durable semantic identities.
- Preserve comparison endpoint direction and state-kind semantics in identity inputs.
- Preserve observed, computed, heuristic, AI-assisted, and human-supplied evidence as distinct classes.
- Do not aggregate completeness more strongly than the least-complete contributing evidence permits.

## Module ownership

- Each domain concept has one canonical owning module.
- Compatibility modules may re-export established names but must not duplicate their implementations.
- Responsibility splits must preserve class identity, supported exports, stable identity inputs, and observable behavior unless an accepted change explicitly authorizes otherwise.
- Avoid catch-all implementation modules. A module that accumulates unrelated concepts must be split before further responsibilities are added.
- Import cycles must be prevented through dependency direction, not hidden through runtime import tricks.

## Supported API

- Names explicitly exported through `gitdrift.__all__` are the supported top-level Python API.
- `gitdrift.domain` is the canonical domain import surface for exported domain records.
- `gitdrift.domain.records` is a compatibility surface while it remains documented and tested; owning modules are canonical.
- Private modules, parser objects, subprocess wiring, test helpers, and rendering helpers are not supported interfaces.
- Supported-interface removal requires the compatibility and deprecation policy.

## Tests and fixtures

- Compile the complete source and test trees before test discovery.
- Run tests through isolated temporary repositories where Git behavior is involved.
- Tests must set repository-local identity and configuration explicitly.
- Tests for read-only behavior must compare relevant refs, index bytes, worktree status, and repository metadata before and after execution.
- Tests must cover negative and incomplete outcomes, not only successful paths.
- Controlling fixtures must not be silently regenerated.
- Generated source and scripts must pass the same canonical validation as handwritten content.

## Required local gate

Before commit, push, or PR creation, run:

```bash
python scripts/validation/validate.py
```

A failing mandatory gate blocks integration. Do not bypass a failure by weakening, deleting, or excluding the affected check without an accepted decision that changes the controlling requirement.
