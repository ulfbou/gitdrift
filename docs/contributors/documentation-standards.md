# Gitdrift documentation standards

## Status

Accepted repository standard.

## Authority

- Accepted ADRs control the decisions they record.
- Specifications control normative product and technical contracts according to their stated status and activation boundary.
- The release-obligation matrix identifies release obligations and their evidence expectations.
- Acceptance-ready and Definition of Done documents control their declared integration or release boundaries.
- Release-gate documents define mandatory evidence for the boundary they govern.
- Roadmaps and implementation plans sequence work but do not override accepted decisions or specifications.
- Historical records and provenance explain earlier states but do not silently control current behavior.
- When authorities conflict, the stricter, later, or more specific accepted authority controls and the conflicting document must be corrected.

## Required distinctions

Documentation must distinguish:

- accepted baseline fact;
- currently implemented behavior;
- proposed contract;
- activated capability;
- future plan;
- historical behavior;
- external evidence;
- unresolved question.

Do not describe a planned capability as implemented, a passing unit test as release completion, or a compatibility re-export as canonical ownership.

## Requirements

- Write from inside the Gitdrift repository and use repository-relative paths.
- Identify authoritative inputs, outputs, identities, provenance, evidence classes, completeness, limitations, budgets, and mutation boundaries where relevant.
- Preserve qualifications and explicit uncertainty when rewriting accepted material.
- Avoid duplicating normative requirements. Link to the controlling document and add only local context.
- Keep package version, native-schema version, capability-schema version, identity scheme, extractor version, obligation-set identity, and policy version separate.
- State whether Git observations are fetched, locally observed, computed, inferred, or externally supplied.
- State whether a comparison establishes ancestry or is only a pairwise comparison.
- State all meaningful exclusions and activation boundaries.
- Commands must be directly copyable and must not use placeholder repository paths.
- Do not claim that validation, verification, mutation safety, determinism, compatibility, or completeness passed unless the corresponding operation ran successfully.

## Product and tool documentation

- Document the Python library as the product boundary.
- Document CLI or module execution as an adapter over supported library behavior, not as the owner of domain semantics.
- Document only implemented and conformance-gated commands, fields, profiles, and exports as current behavior.
- State filesystem, Git, network, resource, diagnostic, serialization, and error boundaries.
- Describe capability discovery truthfully: unavailable or partial functionality must not appear available.

## Links and structure

- Repository-relative Markdown links must resolve to existing files or anchors.
- Links to directories must identify an actual index or entry-point document.
- Headings must be stable enough for inbound links; changing a linked heading requires updating its inbound links in the same PR.
- New contributor standards must be reachable from the documentation entry point or an existing contributor index.

## Required validation

Documentation changes run through the canonical repository validator. Broken repository-relative Markdown links, missing declared authority targets, or unsupported implementation claims block integration.
