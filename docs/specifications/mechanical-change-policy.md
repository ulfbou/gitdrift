# Mechanical-change policy

## Purpose

This specification defines reversible semantic suppression of declared mechanical changes while preserving complete raw history.

## Invariant

A transition is never deleted from repository evidence. A projection may exclude it from a semantic chain only under an identified policy.

## Mechanical candidates

Candidates may include formatting-only changes, generated-output refreshes, line-ending normalization, mass renames, or declared migration revisions. Classification requires evidence and scope; change size alone is insufficient.

## Declared ignored revisions

A project may identify revisions whose selected changes should be treated as mechanical candidates. The declaration records authority, revision identity, scope, rationale, and limitations.

Ignored does not mean absent. Raw snapshots, patches, objects, and parent transitions remain retrievable and referenced by the projection.

## Reversible suppression

Every suppression record contains transition identity, excluded evidence, policy identity, classifier, rationale, semantic projection affected, and reversal information.

Re-running without the suppression policy restores the excluded transitions without reacquiring or reconstructing evidence.

## Generated content

Generated status does not prove semantic irrelevance or non-authority. Generated artifacts may remain required evidence, enforcement, release output, or a source of contradiction. Policy and repository-local authority determine treatment.

## Blame-style limitations

Line attribution may support movement and origin candidates but does not report all deleted or replaced content and does not replace full transition evidence. Ignored revisions, move and copy detection, path simplification, and unavailable parents are recorded as limitations.

## Completeness

A semantic projection reports every suppressed transition or a retrievable inventory, the affected scope, and any completeness consequence. Suppression cannot strengthen an absence claim.
