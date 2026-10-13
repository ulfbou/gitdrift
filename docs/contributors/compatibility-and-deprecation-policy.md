# Gitdrift compatibility and deprecation policy

## Status

Accepted repository standard for pre-1.0 development.

## Independent version domains

The following identities are independent and must not be advanced implicitly together:

- Python distribution version;
- supported Python API version;
- native investigation schema version;
- capability schema version;
- stable identity scheme;
- extractor and evaluator versions;
- obligation-set identity;
- policy and profile versions;
- export-format versions.

A software release does not implicitly change any schema, identity, extractor, obligation, policy, profile, or export identity.

## Supported interfaces

- Names explicitly exported by `gitdrift.__all__` are supported top-level Python interfaces.
- Names explicitly exported by `gitdrift.domain.__all__` are supported domain interfaces.
- `gitdrift.domain.records` is a compatibility import surface while documented and covered by compatibility tests.
- Native schema fields become supported only when the schema and serializer are activated by their controlling acceptance boundary.
- Capability discovery output is supported according to its explicit schema identity.

Private modules, CLI parser objects, subprocess implementation details, adapter internals, test helpers, and undocumented imports are not supported interfaces.

## Compatibility

- Patch releases preserve supported observable behavior and identities for identical effective inputs.
- Minor releases may add backward-compatible exports, records, fields, diagnostics, capabilities, or profiles.
- Incompatible API, schema, identity, capability, policy, profile, or export changes require an explicitly versioned boundary.
- Stable IDs must remain identical for identical semantic inputs under the same identity scheme.
- Changing canonicalization or semantic identity inputs requires a new identity-scheme value.
- Moving a type between modules must preserve the established canonical and compatibility imports unless the old path is deprecated first.
- Completeness may become more precise from additional evidence, but aggregation must not overstate the completeness of contributing evidence.

## Deprecation

A supported interface is deprecated before removal. Deprecation documentation records:

- affected interface or identity;
- replacement;
- first software release carrying the deprecation;
- earliest permitted removal release;
- migration guidance;
- compatibility and evidence impact.

Deprecation diagnostics must not contaminate machine-readable stdout. Safety, security, repository-mutation, or evidence-integrity defects may require accelerated removal, but the change must be explicit, evidence-backed, and recorded.

## Pre-1.0 change discipline

Pre-1.0 status permits deliberate contract evolution; it does not permit silent breakage. Every incompatible change still requires an explicit decision, updated version boundary where applicable, migration treatment, and regression evidence.

## Consumer verification

Consumers pin released distributions by version and provenance, validate supported schema and capability identities, and run consumer-owned integration evidence. Generated reports and serialized investigations are not hand-edited as substitutes for source evidence.
