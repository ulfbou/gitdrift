# Obligation and authority

## Purpose

This specification defines alignment obligations as the bridge between repository evidence and semantic regression judgment.

## Obligation identity

An obligation has a stable project-defined or content-derived identity independent of current wording, file path, or display order. Its record contains:

```text
obligation identity
subjects
required relation
authority references
scope
activation condition
retirement condition
supersession rules
evaluation method
severity or policy metadata, when declared
provenance
```

## Subjects and relations

Subjects may reference concepts, semantic facts, fragments, artifact instances, tests, configuration keys, public symbols, gates, or other stable domain identities.

Relations are explicit, for example:

```text
consistent-with
implements
enforces
references
preserves
exists
does-not-exist
stronger-than-or-equivalent-to
```

A shared name or nearby location does not implicitly create an obligation.

## Authority sources

Authority is established only by configured or repository-local evidence whose role is identified. An authority reference records its subject, representation, scope, activation, and provenance.

Authority must not be inferred solely from:

- branch name;
- recency;
- commit distance;
- file size;
- document location;
- change frequency;
- author identity; or
- majority wording.

When applicable authority cannot be resolved, evaluation remains `unresolved` or judgment remains `insufficient-evidence`.

## Activation, retirement, and applicability

An obligation is evaluated only where its activation conditions are satisfied and its retirement has not taken effect. Applicability is determined per repository state using immutable or captured evidence.

Retirement requires explicit evidence. Apparent disappearance does not prove retirement. An authority may be historical evidence after retirement without remaining controlling authority.

## Supersession

Supersession is an attributed relation identifying:

```text
superseded obligation or authority
replacement obligation or authority
effective state or activation condition
scope
supporting evidence
assessment class
limitations
```

A newer representation, rename, deletion, or textual similarity does not establish supersession by itself.

## Equivalence and stronger representation

Equivalence means two representations satisfy the same relevant semantic obligation within declared scope. A stronger representation satisfies the obligation and adds protection without contradicting it.

Equivalence and strength claims retain method, evidence, confidence class, and limitations. Heuristic or AI-assisted proposals remain proposals until a configured policy permits their use.

## Evaluation values

An `ObligationEvaluation` uses these values:

```text
satisfied
strengthened
weakened
violated
contradictory
superseded
absent
not-applicable
unresolved
```

Each evaluation references the obligation, state, applicable authority, supporting evidence, counterevidence, evaluator, method, completeness, and limitations.

`Absent` records that the required subject or representation was not found within the declared search scope. It is not repository-wide proof when coverage is partial.

## Comparing evaluations

A transition assessment compares evaluations without replacing them. A possible regression exists when a previously applicable obligation moves from satisfied or strengthened to weakened, violated, contradictory, or unresolved absence, subject to authority, supersession, and completeness checks.

Ordinary difference, overlap, or divergence is not automatically regression.

## Unresolved authority

When multiple active authority candidates conflict, the result records:

- each candidate and its provenance;
- the conflicting claims;
- applicable scope;
- supporting evidence and counterevidence;
- missing resolution evidence; and
- a bounded review question.

Gitdrift does not select authority from convenience signals.

## Deterministic judgment prerequisites

A deterministic `true-regression` judgment requires all of the following:

1. the obligation identity and scope are resolved;
2. the obligation was active at the prior state;
3. the prior state satisfied or strengthened it;
4. the candidate state weakened, violated, or contradicted it;
5. no applicable authorized retirement or supersession is established;
6. required evidence and counterevidence searches meet the configured completeness policy;
7. every conclusion is traceable to evidence IDs; and
8. the configured judgment policy authorizes finalization.

If any prerequisite is missing, the case remains unresolved or insufficient-evidence rather than being promoted by confidence alone.
