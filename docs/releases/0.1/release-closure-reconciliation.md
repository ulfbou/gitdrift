# Gitdrift 0.1 release-closure reconciliation

## Status

Executable reconciliation boundary for issue #51 under umbrella issue #23.

This document classifies the residual release evidence represented by the
repository at controlling commit `fe2ca1425dbbc1f4b53e7140bf65ab3d9f2d605a`, tree
`1f995bd45c79894896f414b05343be6e6ca7c137`. It does not itself satisfy an obligation or release
gate.

## Completed bounded work

The following completed boundaries are reused without repetition:

- #47 established resource-bound and state-aware acceptance evidence;
- #48 established reusable Linux and Windows gate runners;
- #49 established exact-candidate Linux and Windows platform evidence.

## Mechanically aggregated obligations

The current release-candidate aggregation covers:

`GD01-001,GD01-002,GD01-003,GD01-004,GD01-005,GD01-006,GD01-007,GD01-008,GD01-018,GD01-019,GD01-020,GD01-021,GD01-022,GD01-023,GD01-024,GD01-025,GD01-026,GD01-027,GD01-028,GD01-029,GD01-030,GD01-031,GD01-032,GD01-033,GD01-035,GD01-036,GD01-037`

These obligations remain subject to exact-candidate identity checks by the
release-candidate aggregator. Their presence in this list does not permit
reuse after a semantically material candidate change without renewed
applicability evidence.

## Residual obligations

### Focused evidence aggregation required

The following obligations are implemented or represented by repository
contracts and focused tests, but are not currently aggregated as passing
release evidence:

- GD01-009: path location versus durable artifact identity;
- GD01-010: versioned Markdown section extraction;
- GD01-011: versioned Python symbol extraction;
- GD01-012: exact evidence preservation for unsupported artifacts;
- GD01-013: derived-fact producer and provenance completeness;
- GD01-014: explicit obligation and authority evaluation;
- GD01-015: negative protection against selector-to-verdict promotion;
- GD01-016: unresolved authority, equivalence, and supersession;
- GD01-017: complete bounded case construction.

The next implementation sub-issue may close these only through executable,
candidate-bound evidence. Documentation or test-module presence alone is not
a passing evidence record.

### Completed evidence not yet aggregated

GD01-034 has completed exact-candidate Linux and Windows evidence from #49.
The release-candidate aggregation does not yet consume that platform matrix.
The next applicable integration boundary must reuse the existing evidence
when candidate, configuration, and validator identities remain applicable.

## Release-gate reconciliation

The current release-candidate aggregation covers:

`G0,G1,G2,G3,G4,G5,G6`

Residual gates are:

- G7: compose completed platform evidence with passing resource-bound evidence;
- G8: perform final documentation, obligation, checklist, and release review
  only after every prior mandatory obligation and G0 through G7 are closed.

## Dependency order

1. Add focused exact-candidate evidence for GD01-009 through GD01-017.
2. Integrate applicable completed platform evidence and close G7 without
   rerunning unchanged platform boundaries.
3. Create the final exact-candidate G8 release-review boundary.
4. Use only the final closure PR to close #23.

Sub-issues must remain outcome-bounded. Optional, post-0.1, divergence,
lineage, forensics, forge, AI, SARIF, DX-export, transport, and repository
mutation work remains outside this release closure.
