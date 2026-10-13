# Versioning and compatibility

## Purpose

This specification separates the versions and identities that evolve across Gitdrift's package, native contracts, configuration, extractors, obligations, policies, and projections.

## Version domains

### Package version

Identifies a released Gitdrift implementation distribution. Package version does not determine the native schema version by itself.

### Native schema version

Identifies the serialized investigation, evidence, case, capability, or other native contract. Schema identity and version travel with every artifact.

### Configuration version

Identifies request, project-configuration, obligation-configuration, and policy syntax where applicable. Configuration compatibility is validated before execution.

### Extractor version

Identifies the producer behavior for extracted fragments and facts. Extractor identity and version are retained on every derived record and in reproduction metadata.

### Obligation-set identity

Identifies the exact normalized obligation definitions, authority declarations, activation rules, and applicable configuration used by an investigation. Mutable source paths do not replace its digest or immutable identity.

### Policy version

Identifies judgment, mechanical-change, selection, correspondence, or other applied policy behavior.

## Compatibility claims

Compatibility is declared per contract and direction:

```text
reader identity and version
writer identity and version
schema or configuration family
backward, forward, or exact compatibility
preserved semantics
ignored or rejected features
known loss
```

A package version never implies universal compatibility with every schema or configuration version.

## Backward compatibility

A newer reader is backward compatible only when it can consume an older artifact while preserving its defined meaning or explicitly migrating it with provenance and validation.

## Forward compatibility

An older reader is forward compatible only where the relevant schema defines safe unknown-field behavior and no unknown required semantic feature is present.

## Unknown fields and enum values

Unknown optional fields may be retained or ignored only as defined by the schema. Unknown required fields, record kinds, enum values, identity algorithms, or semantic features produce explicit incompatibility or partial capability. They are never silently coerced.

## Case-schema compatibility

A case is judgment-compatible only when the policy accepts its case schema, evidence classes, completeness model, obligation representation, and referenced native schema versions.

## Migration

Migration creates a new artifact with migration provenance, source digest, target schema, producer version, diagnostics, and any declared loss. Historical source artifacts remain unchanged.

## Projections and transports

Markdown, SARIF, JSON Lines, and DX versions are independent from native Gitdrift schemas. Transport compatibility does not imply semantic completeness, and native schema compatibility does not imply transport compatibility.

## Capability discovery

The active composition reports supported reader and writer versions, migrations, extractors, configurations, policies, and projections. Planned support is not advertised as available.
