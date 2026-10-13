# Cache and derived data

## Purpose

This specification defines cache and derived-data invariants before caching is implemented. Caching may reduce cost but must never alter evidence semantics, identity, completeness, or judgment.

## Derived and disposable

Cache entries are derived artifacts. They are disposable and are never the sole authority for repository evidence, obligations, policy, or judgment.

Deleting a cache may increase execution cost but must not change the semantic result for identical inputs and capabilities.

## Cache key

A cache identity includes every semantic input required by the cached computation, including where applicable:

```text
cache family and key schema version
repository identity
immutable state and object identities
captured provisional-state manifest
transition, traversal, and diff options
path and subject scope
extractor identity and version
obligation-set identity
policy identity and version
native schema version
canonicalization and identity scheme versions
configuration digest
capability composition
resource or truncation boundary when material
```

Ambient mutable state may not influence a cache hit unless captured in the key or validated explicitly.

## Cache entry

Every entry records:

```text
cache identity
producer and producer version
creation input identities
payload identity and schema
completeness
limitations
diagnostics
resource accounting
validation status
```

Timestamps may support storage management but never determine semantic freshness alone.

## Cache hit validation

Before reuse, the implementation verifies key equality, schema and producer compatibility, payload integrity, required capabilities, and applicable completeness.

A stale, incompatible, corrupt, or semantically incomplete entry is rejected with bounded diagnostics. It is not treated as a cache miss that silently satisfies the request.

## Semantic invariance

For identical semantic inputs, a validated cache hit and uncached computation produce semantically identical domain results. Cache-specific provenance may differ only in explicitly non-semantic accounting records.

Cache hits cannot:

- change an evidence class;
- replace immutable source identities;
- upgrade confidence or completeness;
- remove diagnostics or limitations;
- finalize a judgment not available without caching; or
- hide omitted work.

## Completeness

Cached results retain their original completeness and truncation. A broader current request may reuse a bounded cached component only when the remaining work and combined completeness are represented correctly.

A complete cache entry for a narrow path, ref set, history window, extractor set, or obligation set is not complete for a broader request.

## Producer evolution

Changing extractor, parser, policy, canonicalization, identity, schema, or domain producer versions invalidates or migrates entries according to declared compatibility. Compatibility is never inferred from package version proximity.

## Negative and failure caching

Unsupported capability, unavailable evidence, parser failure, timeout, and resource exhaustion may be cached only under an explicit policy. Such entries retain diagnostics, retry conditions, evidence scope, and completeness and cannot be reused as proof of semantic absence.

## Storage and security

Cache storage is an adapter concern outside the domain kernel. Paths are explicit and safe; payloads are integrity-checked; repository content is never executed; secrets and unnecessary personal data are excluded.

A cache must not modify analyzed refs, index entries, working-tree files, configuration, or hooks.

## Eviction and garbage collection

Eviction depends on storage policy and does not alter domain history or native artifacts already emitted. Reference counting, age, size, or reachability may guide eviction but do not redefine identity or authority.

## Remote or shared caches

A future shared cache is an external trust boundary. Provider identity, authentication, integrity, confidentiality, tenant isolation, compatibility, and provenance must be explicit before use.

## Observability

Resource accounting reports cache lookups, hits, misses, rejections, verification, bytes reused, and work avoided when mechanically known. Cache effectiveness is descriptive and is not a correctness signal.
