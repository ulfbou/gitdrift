# State-awareness profile

## Purpose

The state-awareness profile is the first narrow slice of the Gitdrift library. It analyzes meaningful committed and provisional states without integrating, committing, or otherwise mutating the repository.

The profile is repository-independent. `dx-artifacts` is its first acceptance corpus, not a runtime dependency or embedded special case.

## Inputs

A request identifies:

```text
repository identity
HEAD selection
optional configured upstream
index inclusion
working-tree inclusion
untracked-file policy
ignored-file policy
path or subject scope
extractors
obligation set
comparison overrides
```

Every mutable locator is resolved and captured before analysis. The request records unsupported or unavailable inputs instead of silently omitting them.

## Selected states

The profile may select:

- `HEAD`, captured as an immutable commit state;
- configured upstream, captured as a branch-tip locator and immutable commit;
- `INDEX`, captured reproducibly against its base commit;
- `WORKTREE`, captured reproducibly against the index and base commit.

An absent upstream is valid when the request does not require one. Its absence is explicit in diagnostics and completeness.

## Default comparison matrix

Required when both endpoints exist:

```text
HEAD -> INDEX
INDEX -> WORKTREE
HEAD -> WORKTREE
HEAD <-> upstream
```

Optional comparisons:

```text
upstream <-> INDEX
upstream <-> WORKTREE
```

The profile uses the contract in `state-comparison-matrix.md`. Only actual parent-to-child relationships are ancestry transitions.

## Capture and analysis

Committed states retain commit and tree identities. Provisional states follow `provisional-state-capture.md` and retain manifests, policies, and mutation checks.

For each selected comparison, the profile produces raw path changes and exact evidence. Supported extractors may add Markdown sections, Python symbols, tests, or declared facts. Unsupported content remains available as exact evidence and reduces semantic-extraction completeness where applicable.

## Obligation evaluation

Only explicitly supplied or repository-locally discovered obligations accepted by the request are evaluated. The profile records applicability, authority, evidence, counterevidence, completeness, and unresolved questions for each evaluation.

A changed path or symbol selects possible affected obligations. It does not prove weakening or regression.

## Case selection

A case may be created for:

- possible obligation weakening or violation;
- contradictory candidate states;
- unresolved supersession or equivalence;
- overlap between independent upstream and provisional candidates;
- missing evidence needed for judgment.

Clean, aligned states still produce a valid investigation and may produce no cases.

## Completeness

The result independently declares completeness for state capture, selected comparisons, artifact coverage, semantic extraction, obligation coverage, and counterevidence search. A skipped optional comparison is `not-requested`, not complete.

## Output contract

The profile returns one native investigation containing:

```text
analysis manifest
captured states
comparisons and transitions
artifact changes
extracted facts
obligations and evaluations
cases
completeness
diagnostics
```

Native JSON is canonical. Presentation and transport are downstream.

## Explicit exclusions

The initial profile does not perform all-branch archaeology, complete file-history reconstruction, split or merge inference, AI assessment, forge integration, repository mutation, automatic fixes, SARIF export, or DX evidence export.
