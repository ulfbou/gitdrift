# Next repository objective: reproducible index capture

## Objective

Implement a read-only, reproducible capture of the Git index that satisfies the implementable portion of GD01-003 and creates the evidence boundary required for `HEAD -> INDEX` comparison.

## Scope

The increment must:

1. extend the domain-owned repository port with explicit index acquisition;
2. capture the base `HEAD` identity when available;
3. capture every selected index entry with workspace-relative path, stage, mode, and object identity;
4. preserve unmerged stages rather than collapsing them;
5. derive a stable index-state manifest and content identity from semantic inputs;
6. detect relevant index mutation across capture or return an explicit unstable-capture result;
7. perform no write to refs, index, working tree, configuration, hooks, or repository objects;
8. provide adapter conformance tests for normal, empty, staged, deleted, mode-changed, and unmerged index states; and
9. keep the state-awareness profile unavailable after this increment unless all of its required capabilities are composed.

## Exclusions

This objective does not include:

- working-tree capture;
- untracked or ignored-file policies;
- state comparison or raw patch construction;
- semantic extraction;
- obligation evaluation;
- case construction;
- native JSON serialization;
- new CLI analytical commands; or
- hosted repository mutation.

## Acceptance

The increment is complete when:

- index identities are deterministic for identical base, entries, stages, modes, objects, and capture policy;
- a semantically relevant index change changes the captured identity;
- unmerged entries retain all observed stages;
- a capture race cannot be reported as reproducible;
- before-and-after sentinels prove zero repository mutation;
- unsupported or unavailable index evidence produces typed failure or partial evidence rather than semantic absence;
- tests map explicitly to GD01-003, GD01-005, GD01-006, GD01-028, and the applicable G2 checks; and
- canonical repository validation passes with no capability overclaim.
