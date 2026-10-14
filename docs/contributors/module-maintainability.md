# Python module maintainability

## Status

Accepted repository validation policy.

## Purpose

The canonical validator enforces bounded Python module size for implementation, repository tooling, and tests. The policy limits maintainability accretion without treating file size as semantic regression, architectural failure, or evidence that content is a harmful blob.

## Policy identity

The active policy is stored in:

```text
scripts/validation/module-maintainability.json
```

Its versioned identity is:

```text
gitdrift-python-module-maintainability-v1
```

Changing classification, measurement, limit, or exception semantics requires a new policy identity or an accepted compatibility-preserving policy update.

## Classified roles

The validator classifies Python modules by explicit repository role:

```text
src/**/*.py       implementation
scripts/**/*.py   repository-tooling
tests/**/*.py     test
```

Python files below `tests/fixtures/` are fixtures rather than test implementation and are not silently classified as test modules.

Documentation, schemas, generated data, binary artifacts, and non-Python files are outside this policy. Their exclusion from this maintainability gate does not remove them from changed-file discovery, repository evidence, or consumer-specific validation.

## Measurements

Each classified module is measured from exact bytes:

- byte count is the exact file length;
- physical-line count is derived from byte-level newline boundaries;
- decoding is not required for measurement;
- CRLF, LF, mixed endings, BOM, and unexpected encoding do not independently fail this gate.

A Python consumer may still reject source it cannot compile. That is the separate `python-compilation` gate.

## Limits

The policy currently applies these limits:

```text
implementation       65536 bytes   800 physical lines
repository-tooling   65536 bytes   800 physical lines
test                 98304 bytes  1200 physical lines
```

A violation reports the path, role, exact measurements, applicable limits, and exception state. The gate does not rewrite, normalize, remove, split, stage, or commit content.

## Exceptions

An exception must be:

- attached to one exact repository-relative Python module;
- bounded by explicit byte and physical-line limits;
- associated with an expiry boundary;
- accompanied by a concrete reason;
- mechanically validated against an existing classified module.

Exceptions cannot apply to modules under `scripts/validation/`. The validator cannot exempt its own implementation.

An exception permits only the recorded temporary bound. Growth beyond that bound fails validation.

## Interpretation

A module-limit violation is a maintainability-policy finding. It is not, by itself:

- semantic regression;
- architectural regression;
- evidence of lost behavior;
- proof that a file is a harmful blob;
- permission to delete or rewrite content automatically.

Any decomposition must preserve applicable behavior, public and compatibility surfaces, diagnostics, exact evidence, and controlling obligations.

## Canonical validation

The policy runs as the `module-maintainability` gate in the canonical sequence:

```bash
python scripts/validation/validate.py
```

Scoped validation applies the gate only to classified Python paths included by the selected base-ref, staged, unstaged, or untracked scope.
