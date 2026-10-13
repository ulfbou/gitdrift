# Comparison windows

## Purpose

This specification defines bounded historical windows used to compare transitions, cumulative change, and obligation evolution.

## Common window contract

Every window records its identity, selection method, ordered states or transitions, history mode, parent policy, subject scope, inclusions, exclusions, and completeness.

## Adjacent window

An adjacent window compares one explicit transition from a state to its direct successor under the selected parent relation. Merge commits produce independent adjacent windows for each parent.

## Rolling window

A rolling window compares overlapping bounded sequences across a selected history. Window width, step, endpoints, and omitted transitions are explicit.

## Epoch window

An epoch window compares selected historical anchors representing declared or mechanically selected eras. Epoch selection is attributed and does not erase intermediate transitions.

## Obligation-relative window

An obligation-relative window begins at an obligation's activation, last satisfied state, or another declared obligation boundary and ends at a selected state. Authority and activation evidence form part of the window definition.

## User-selected window

A user-selected window uses explicit immutable endpoints and traversal rules. Mutable locators are captured before analysis.

## Constraints

- A cumulative window never replaces its constituent raw transitions.
- Window endpoints do not imply ancestry unless established separately.
- Selection by churn or size does not establish risk.
- Simplified history and omitted transitions are recorded.
- Results cannot claim absence or continuity beyond window completeness.

## Reproduction

Reproduction records selected identities, traversal, ordering, diff options, mechanical-change policy, extractors, obligation set, and configuration digest.
