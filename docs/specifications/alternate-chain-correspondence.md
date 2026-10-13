# Alternate-chain correspondence

## Purpose

This specification defines how Gitdrift compares alternate histories without assuming that commit identity, patch similarity, artifact similarity, and semantic equivalence are the same relation.

## Chain boundary

An alternate-chain comparison declares:

```text
left and right captured tips
common ancestry evidence
selected merge base or bases
left traversal
right traversal
subject scope
correspondence methods
limitations
```

## Commit correspondence

Commit correspondence is an attributed relation between commits or transitions. Candidate evidence may include identical commit identity, patch identity, patch similarity, parent context, affected artifacts, or declared provenance.

Commit messages, timestamps, or author identity may support review but do not prove correspondence.

## Patch equivalence

Patch-equivalent changes produce equivalent normalized changes under an explicit comparison method and scope. The result records normalization, paths, diff options, and known losses.

Patch equivalence does not by itself prove semantic equivalence, authority, or integration.

## Cherry-pick equivalence

A cherry-pick-equivalence candidate records that distinct commits appear to carry equivalent changes across different ancestry. It remains distinct from identical commits and from proof that all related behavior or obligations are equivalent.

## Unmatched transitions

Transitions without a supported counterpart remain unmatched. Unmatched does not mean unique value, regression, noise, or omission. Later semantic analysis may classify their facts.

## Artifact-chain correspondence

Artifact correspondence relates artifact instances or lineages across chains using deterministic Git evidence and attributed structural inference. Rename, copy, replacement, split, and merge candidates retain their relation class, method, confidence, and limitations.

## Semantic correspondence

Semantic correspondence compares facts, concept representations, and obligation evaluations. Initial relations are:

```text
equivalent
left-stronger
right-stronger
contradictory
superseded
unresolved
```

Semantic correspondence must reference supporting facts, authority evidence, counterevidence, and completeness. Text or patch similarity alone cannot finalize it.

## Pairing constraints

Pairing is not required to be one-to-one. One transition may correspond to several transitions, and unmatched evidence remains available. Pairing order and display order never define identity.

## Confidence and limitations

Every non-deterministic correspondence records producer, version, method, input evidence, confidence class, alternatives, and limitations. Partial correspondence cannot support complete absence or equivalence claims outside its scope.
