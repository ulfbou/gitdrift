# Acceptance strategy

## Purpose

This strategy defines how Gitdrift proves semantic contracts, adapter behavior, reproducibility, safety, and compatibility across synthetic fixtures and independent repository corpora.

Acceptance establishes implemented behavior. Documentation claims without corresponding executable evidence are not sufficient release proof.

## Test layers

### Domain-unit tests

Small deterministic tests cover identity, state and transition semantics, lineage relations, fact deltas, obligations, cases, completeness, diagnostics, compatibility, pressure, purity, and resource accounting without requiring Git subprocesses.

### Adapter-conformance tests

Every Git, parser, extractor, serializer, sink, cache, or later interoperability adapter is tested against its domain-owned port. Conformance tests prove exact evidence mapping, diagnostics, read-only behavior, and unsupported-input handling.

### Profile acceptance tests

State-awareness, divergence, file-lineage, forensics, and judgment scenarios exercise complete vertical slices through native validated results.

## Synthetic graph fixtures

Synthetic repositories provide controlled histories for:

- linear parent-to-child evolution;
- merges with parent-specific results;
- multiple merge bases;
- first-parent and full-ancestry differences;
- ref movement after capture;
- renames, copies, deletions, restoration, and independent reintroduction;
- split and merge candidates;
- patch-equivalent and cherry-pick-equivalent histories;
- staged, unstaged, untracked, ignored, and unmerged states;
- submodules, symlinks, modes, binary blobs, and unsupported artifacts; and
- shallow, missing, corrupt, or inaccessible evidence.

Fixture construction is reproducible and records immutable object identities.

## Real-repository acceptance corpora

`dx-artifacts` and `Dx.Domain` are independent acceptance corpora, not runtime dependencies.

Pinned immutable repository states validate that synthetic contracts compose against realistic documentation, code, tests, configuration, branches, and historical structures. Mutable hosted state is never embedded as an unqualified expected fact.

## Golden native JSON

Golden artifacts validate canonical native serialization, stable identity, references, diagnostics, completeness, and reproduction metadata.

Golden comparisons distinguish semantic equality from incidental formatting or ordering. Intentional schema evolution uses explicit migration or updated compatibility evidence rather than silent replacement.

## Property-based tests

Property-based tests cover invariants such as:

- identity independence from presentation order;
- comparison endpoint ordering;
- no strengthening of partial completeness;
- preservation of raw evidence under semantic suppression;
- reference closure;
- deterministic canonicalization;
- lineage graphs retaining every declared source and target; and
- cache reuse preserving semantics.

Generated examples remain bounded and reproducible through recorded seeds or minimized counterexamples.

## Mutation-safety tests

Before-and-after sentinels cover refs, `HEAD`, index entries, working-tree files, repository configuration, hooks, selected Git objects, and hosted metadata where applicable.

Analysis passes only when these remain unchanged except for an explicit output sink outside analyzed state.

## Determinism tests

Repeated executions with identical immutable inputs, configuration, versions, capabilities, budgets, and cache policy produce semantically identical native results. Nondeterministic metadata is isolated or normalized according to its contract.

## Schema compatibility tests

Tests cover supported reader and writer combinations, unknown optional fields, unknown required fields, enum evolution, migration provenance, case-policy compatibility, configuration versions, extractor versions, and transport independence.

## Cross-platform Git behavior

Conformance runs cover supported operating systems, filesystem semantics, Git object formats, path normalization, modes, symlinks, line endings, executable bits, and subprocess encoding where available.

Platform-specific limitations are capabilities and diagnostics, not silently divergent semantics.

## Adversarial repositories

Acceptance includes hostile or malformed paths, oversized blobs, deep histories, broad ref sets, prompt-injection content, malformed configuration, parser bombs, rapidly mutating provisional state, broken objects, unsafe symlinks, and resource exhaustion.

Repository content remains untrusted evidence and cannot control execution instructions.

## Partial-analysis tests

Every budget, unavailable capability, unsupported artifact, parser failure, missing object, truncation, and capture race proves that valid evidence is preserved, diagnostics are stable, completeness decreases accurately, and no false absence or deterministic judgment is emitted.

## Evidence requirements

Each acceptance scenario records:

```text
fixture identity
request and configuration
producer versions
expected native schema
expected observations and derived records
expected diagnostics
expected completeness
resource budget and accounting
mutation sentinel
reproduction command or harness identity
```

## Synthetic state-awareness acceptance

The first complete synthetic state-awareness boundary composes the accepted
repository-state acquisition, required comparison matrix, raw-change evidence,
native serialization, capability-discovery, determinism, and read-only
sentinel suites.

Run the boundary against one clean committed candidate with:

```bash
python scripts/acceptance/state_awareness_synthetic.py \
  --output "$OUTPUT_DIR/gitdrift-state-awareness-synthetic.json"
```

The generated evidence identifies the exact candidate commit, executed test
modules, required scenarios, mapped obligations, release gates, mutation
sentinel, bounded test-output identity, and aggregate outcome.

This boundary does not satisfy the pinned `dx-artifacts` corpus check,
cross-platform closure, complete obligation closure, or final release review.
It does not activate semantic extraction, obligation evaluation, case
construction, divergence, lineage, forensics, SARIF, DX export, AI assessment,
or repository mutation through the executable state-awareness profile.

## Installed-distribution acceptance

The installed-distribution boundary builds one wheel and one source
distribution from the same clean candidate. Each artifact is installed into
a separate isolated environment and exercised outside the source checkout.

The executable boundary verifies:

- supported public imports;
- packaged native-schema loading;
- CLI and library capability-discovery equivalence;
- truthful available and unavailable capability declarations;
- independent package and native-schema version domains; and
- exact candidate and artifact SHA-256 identities.

Run the boundary with:

```bash
python scripts/acceptance/installed_distribution.py \
  --output "$OUTPUT_DIR/gitdrift-installed-distribution.json"
```

The generated evidence is release evidence for the exact candidate. It is not
a substitute for state-awareness corpus, platform, obligation-closure, or
final release-gate evidence.

## Release-candidate evidence aggregation
The exact-candidate aggregation boundary executes canonical validation, synthetic state-awareness acceptance, and installed-distribution acceptance against one clean commit. It records content digests for bounded command output, rejects mixed candidate identities, and reports every GD01 obligation and G0 through G8 gate as `pass` or `blocked`. Missing release-wide evidence remains blocked and cannot be promoted to release readiness.

Run the boundary with:
```bash
python scripts/acceptance/release_candidate.py \
  --output "$OUTPUT_DIR/gitdrift-release-candidate.json"
```

An exit status of `2` means the evidence document was produced successfully but mandatory release closure remains blocked. Exit status `1` means the evidence operation itself failed.

## Release boundary

A release passes only when applicable domain, conformance, profile, determinism, mutation-safety, compatibility, adversarial, and corpus scenarios pass and their evidence artifacts validate.
