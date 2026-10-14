# Next repository objective: reproducible working-tree capture

## Objective

Implement read-only, reproducible working-tree capture under explicit tracked, untracked, ignored, symlink, deletion, and submodule policies, satisfying the implementable portion of GD01-004 and extending the capture-race boundary established by index acquisition.

## Scope

The increment must:

1. extend the domain-owned repository port with explicit working-tree acquisition;
2. bind the capture to the captured index and available `HEAD` base identities;
3. capture exact selected bytes, modes, symlink treatment, deletions, and gitlink status;
4. implement explicit `exclude`, `include-selected`, and `include-all-visible` untracked policies;
5. exclude ignored files by default and distinguish any explicit ignored-file inclusion;
6. derive a deterministic manifest identity from semantic inputs and capture policies;
7. detect relevant working-tree or index mutation across capture;
8. perform no write to refs, index, working tree, configuration, hooks, or repository objects; and
9. keep the state-awareness profile unavailable until comparison, evidence, extraction, obligation, case, and native-output requirements are composed.

## Exclusions

This objective does not include state comparison, raw patches, semantic extraction, obligation evaluation, case construction, native JSON serialization, new analytical CLI commands, or hosted mutation.

## Acceptance

The increment is complete when deterministic fixtures prove clean, modified, deleted, untracked, ignored, symlink, mode, submodule, unreadable, unsupported, and capture-race outcomes; before-and-after sentinels prove zero repository mutation; limitations and policy exclusions are explicit; canonical validation passes; and capability discovery does not overclaim profile readiness.
