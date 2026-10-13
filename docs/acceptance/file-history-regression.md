# File-history regression acceptance

## Purpose

This document defines acceptance scenarios for file lineage, fact evolution, and regression provenance using reproducible repository fixtures.

## Fixture contract

Each scenario declares immutable commits and refs, complete parent relationships, artifact snapshots, expected raw changes, extractor and obligation inputs, expected lineage relations, localization results, completeness, and a mutation sentinel.

## Scenarios

### Simple linear regression

An active obligation is satisfied at one commit and violated by its direct child. Gitdrift identifies the last satisfied state and first violating parent-to-child transition with exact evidence.

### Regression introduced through merge

A merge result violates an obligation relative to one parent. Gitdrift records every parent-specific transition and distinguishes origin commit, integration commit, and first observed commit on the selected branch.

### Change later restored

A later transition restores the earlier supported representation or behavior. The result preserves the violating interval and records restoration evidence.

### Change recreated independently

Equivalent satisfying content appears later without supported restoration lineage. The result classifies independent reintroduction and preserves distinct provenance.

### Rename before regression

An artifact is renamed or moved before a later violating change. Path change does not break the supported artifact lineage, and localization references the correct instance and transition.

### Split before regression

One artifact is split across several successors before a required fact is lost. The result records split candidates, accounted and unaccounted representations, and unresolved lineage where deterministic proof is unavailable.

### Fact surviving on another branch

The selected controlling path loses a fact while a captured alternate ref retains it. Affected and preserving refs are recorded without treating branch activity or naming as authority.

### Large rewrite with no semantic loss

A file changes substantially while all relevant facts and obligations remain equivalent or stronger. Gitdrift reports structural change without a regression judgment.

### Tiny normative weakening

A small textual change weakens an active normative obligation. Gitdrift localizes the exact transition despite low churn and records authority, fact delta, and counterevidence.

## Read-only acceptance

Before and after sentinels for refs, index, working tree, configuration, and selected objects remain equal. Output is written only to the explicit sink.

## Acceptance rule

A scenario passes only when raw evidence and derived lineage remain distinct, parent-specific transitions are preserved, localization terms are used correctly, alternatives and counterevidence are represented, completeness is accurate, native output validates, and the read-only sentinel passes.
