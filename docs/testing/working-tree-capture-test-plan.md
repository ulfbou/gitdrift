# Working-tree capture test plan

## Purpose

This plan defines executable evidence for the next bounded acquisition increment. It maps working-tree capture tests to GD01-004, GD01-005, GD01-006, GD01-028, and release gates G2, G4, G6, and G7. It does not activate the state-awareness profile.

## Shared fixture contract

Every fixture records the initial `HEAD`, index bytes, tracked and selected untracked bytes, local configuration, hooks inventory, request policies, expected entries, expected limitations, and expected diagnostics. Every test compares the same mutation sentinel after capture.

A captured entry must identify its workspace-relative path, entry kind, exact content identity when readable, effective mode, symlink target treatment, index relation, and limitations. A manifest must identify its captured index, policies, ordered entries, exclusions, and stable identity inputs.

## Deterministic capture scenarios

### Clean tracked file

Capture a tracked file whose working-tree bytes and mode match stage 0. Assert exact identity, clean relation to the index, deterministic rerun identity, and no mutation.

### Modified tracked file

Change bytes without staging. Assert that the captured content differs from the index object, the index remains unchanged, and repeated capture over unchanged bytes is deterministic.

### Deleted tracked file

Remove a tracked path from the working tree. Assert an explicit deletion entry relative to the captured index rather than omission.

### Executable-mode change

Change the effective executable mode on a platform that supports it. Assert mode evidence and a changed manifest. On unsupported platforms, require an explicit capability limitation rather than a false unchanged result.

### Symlink

Capture a tracked symlink as link metadata and target text without following the target. Assert that an external target cannot add host-file bytes to evidence.

### Gitlink and nested repository

Capture the gitlink identity and supported worktree status. Assert that the nested repository is not traversed implicitly.

### Binary and undecodable content

Capture exact bytes without requiring text decoding. Assert that semantic absence is not inferred.

### Empty file and empty worktree

Capture zero-length content and a repository with no selected worktree entries. Assert distinct valid manifests rather than unavailable capture.

## Untracked and ignored policies

### Untracked exclude

Create visible untracked files and assert they are omitted with policy recorded as `exclude`. Artifact coverage must not describe them as searched or absent.

### Untracked include-selected

Request explicit safe paths. Assert that only those untracked paths are captured and that missing, absolute, escaping, duplicate, and unsupported selections receive typed outcomes.

### Untracked include-all-visible

Assert inclusion of every visible non-ignored untracked path within scope, deterministic ordering, and bounded resource accounting.

### Ignored default exclusion

Create ignored content and assert exclusion without classifying it as generated or irrelevant.

### Explicit ignored inclusion

When supported by the request contract, assert separate policy identity and provenance for included ignored paths.

## Race and failure scenarios

### Index changes during capture

Change the index between the initial and final marker. Assert typed unstable-capture failure and no reproducible manifest.

### Selected bytes change during capture

Change a selected file after its initial observation. Assert bounded retry or typed unstable-capture failure according to the accepted policy.

### File is replaced during capture

Replace a regular file with a directory or symlink. Assert that mixed observations cannot form a reproducible entry.

### HEAD changes during capture

Move `HEAD` while acquiring the worktree base. Assert unstable capture when the base identity is material.

### Unreadable path

Make selected content unreadable where the platform permits. Assert evidence-unavailable diagnostics and truthful partial coverage.

### Unsafe and hostile paths

Exercise traversal-like names, control bytes supported by Git, platform-reserved names, case collisions, and normalization collisions. Assert safe rejection or exact bounded representation without host escape.

### Resource exhaustion

Exceed configured file-count, byte, and output budgets. Assert explicit truncation, omitted-work inventory, and reduced completeness.

## Cross-platform matrix

Run applicable conformance scenarios on every declared Python and operating-system target. Record behavior for executable bits, symlink privileges, case sensitivity, path encoding, line endings, file replacement, long paths, and subprocess streams. Platform limitations must appear in capability or diagnostic evidence.

## Completion rule

Working-tree capture is complete only when all applicable scenarios pass through the concrete Git adapter, deterministic reruns agree, every unstable observation is rejected or represented by the accepted partial-result policy, the mutation sentinel passes, canonical validation succeeds, and capability discovery still reports the analytical profile unavailable.
