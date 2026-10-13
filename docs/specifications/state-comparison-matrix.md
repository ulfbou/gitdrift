# State comparison matrix

## Purpose

This specification defines the comparisons used by the state-awareness profile and the question answered by each pair. A comparison does not imply ancestry unless separately established.

## Required comparisons

### HEAD to INDEX

Question: what is staged relative to the captured `HEAD` state?

This comparison isolates the staged candidate. It is not a commit transition and must not assign an introduction commit.

### INDEX to WORKTREE

Question: what tracked or explicitly included content differs from the captured index?

This comparison isolates unstaged work under the recorded untracked and ignored-file policies.

### HEAD to WORKTREE

Question: what is the cumulative local difference from `HEAD` after combining staged and unstaged content?

This view supports review but does not replace the two comparisons above because it cannot attribute changes to their provisional boundary.

### HEAD and upstream

Question: how do the locally checked-out commit and captured upstream tip relate?

The result includes equality, ancestry or divergence evidence where established, plus their state comparison. Direction is reported explicitly and is not inferred from labels such as behind or ahead alone.

## Optional comparisons

### Upstream and INDEX

Question: how does the complete staged candidate compare with the independently captured upstream state before integration?

This detects overlap, unique changes, and possible obligation differences without pulling, merging, or rebasing.

### Upstream and WORKTREE

Question: how does the complete local provisional candidate compare with upstream?

This is useful when unstaged work participates in the candidate under review. It remains optional because its scope and reproducibility depend on working-tree capture policy.

## Matrix representation

Every matrix entry records:

```text
left state
right state
comparison kind
required, optional, unavailable, or not-requested status
question
change-set identity
ancestry evidence, if independently established
limitations
```

Missing states yield unavailable entries rather than removed rows. Skipped optional pairs remain `not-requested`.

## Interpretation constraints

- Ref-to-ref and provisional comparisons are not parent-to-child transitions.
- Symmetric difference does not establish semantic equivalence or regression.
- A HEAD-to-WORKTREE difference cannot identify whether content is staged.
- Upstream comparison never authorizes automatic integration.
- Findings reference the exact matrix entry and captured endpoint identities used.
