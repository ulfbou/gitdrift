# Repository architecture for 0.1

## Status and scope

This document defines the implementable repository architecture for the milestone `Gitdrift 0.1: repository-state alignment and provenance`.

It translates the existing domain, layering, profile, API, CLI, evidence, compatibility, resource, safety, and acceptance contracts into one repository structure and dependency system. It does not weaken those contracts or promote deferred capabilities into the 0.1 implementation.

The 0.1 vertical slice captures committed and provisional repository states, performs the state-awareness comparison matrix, preserves exact evidence, runs supported deterministic extractors, evaluates explicit obligations, builds bounded cases, and emits validated canonical native JSON without mutating the analyzed repository.

## Architectural authority

The repository architecture is constrained by:

- [product vision](../vision/product-vision.md), [product principles](../vision/product-principles.md), and [non-goals](../vision/non-goals.md);
- [layered analysis architecture](layered-analysis-model.md), [domain model](domain-model.md), and [library and adapter boundaries](library-and-adapter-boundaries.md);
- [quality attributes](quality-attributes.md) and [trust boundaries](trust-boundaries.md);
- [repository state](../specifications/repository-state-model.md), [transition](../specifications/transition-and-change-set.md), [evidence](../specifications/evidence-and-provenance.md), [obligation](../specifications/obligation-and-authority.md), [case](../specifications/case-model.md), and [native investigation](../specifications/native-investigation-model.md) contracts;
- [state-awareness profile](../profiles/state-awareness.md); and
- [acceptance strategy](../testing/acceptance-strategy.md).

When this document and a more specific accepted semantic contract conflict, the semantic contract controls. Repository paths organize implementation; they do not redefine domain meaning.

## Product and distribution shape

Gitdrift 0.1 is one Python distribution containing:

```text
gitdrift library
thin gitdrift CLI adapter
native JSON schema resources
no required network service
no required external product repository
```

The library is the product core. The CLI is a process adapter. `dx-artifacts` and `Dx.Domain` remain external acceptance corpora and never become runtime source dependencies or required submodules.

The analytical core requires no network access and performs no repository mutation. An explicit output sink is the only supported write boundary for analytical execution.

## Repository layout

The 0.1 repository uses the following responsibility-oriented shape:

```text
/
  pyproject.toml
  README.md
  LICENSE
  docs/
  src/
    gitdrift/
      __init__.py
      py.typed
      domain/
      application/
      ports/
      profiles/
        state_awareness/
      adapters/
        git/
        extractors/
        obligations/
        serialization/
        sinks/
      schemas/
      cli/
      composition.py
  tests/
    unit/
    contract/
    integration/
    acceptance/
    property/
    adversarial/
    fixtures/
      repositories/
      manifests/
      obligations/
      golden/
  scripts/
    validation/
  .github/
    workflows/
```

This is a responsibility contract, not permission to expose every module publicly. Directory renaming is compatible only when dependency direction, public imports, resource loading, tests, and documented entry points remain equivalent.

## Source package boundaries

### `gitdrift.domain`

Owns immutable domain records, value objects, enums, identity inputs, invariants, and domain-level validation.

Initial responsibilities include:

```text
repository and state identities
captured-state manifests
comparisons and transitions
artifact snapshots and raw changes
evidence references and provenance
semantic facts
obligations and evaluations
cases, completeness, and reproduction
diagnostics and resource records
```

The domain package imports only the Python standard library and explicitly accepted small foundational dependencies. It does not import adapters, CLI code, subprocess facilities, filesystem discovery, renderers, or composition roots.

Domain records do not perform ambient I/O. Constructors and pure functions reject invalid states rather than repairing them through hidden defaults.

### `gitdrift.application`

Owns explicit use cases and orchestration over domain-owned ports.

Initial use cases are:

```text
capture selected states
construct the state comparison matrix
read exact artifact evidence
extract supported facts
evaluate explicit obligations
build bounded cases
assemble a native investigation
validate and serialize the native result
```

Application services accept typed request objects and return typed results. Expected partial analysis is represented in results and diagnostics. Application services do not parse CLI arguments or select process exit codes.

### `gitdrift.ports`

Owns protocols required by the domain and application layers. Initial ports cover:

```text
repository discovery and identity
ref and object reading
committed-state acquisition
index and working-tree capture
state comparison and raw changes
fact extraction
obligation-set loading
native schema validation
explicit output sinks
clock or environment facts only where reproduction requires them
```

Ports use domain-oriented types and bounded byte or stream interfaces. They do not expose `subprocess.CompletedProcess`, parser-library nodes, provider SDK objects, `argparse.Namespace`, or terminal concepts.

### `gitdrift.profiles.state_awareness`

Owns the 0.1 profile request, result, capability requirements, comparison selection, degradation rules, and application-level profile service.

It composes application use cases. It does not import a concrete Git adapter directly, own serialization semantics, or create special cases for `dx-artifacts`.

### `gitdrift.adapters.git`

Implements repository ports using read-only Git operations.

The adapter owns:

```text
Git command or library invocation
Git-version and object-format detection
ref resolution
commit, tree, blob, mode, symlink, and gitlink reading
index-stage reading
working-tree byte capture
raw diff construction
rename and copy configuration
bounded subprocess diagnostics
capture race detection
```

Repository content is passed as data, never interpolated into shell programs. The adapter does not checkout, update refs, alter the index, modify working-tree files, change configuration, invoke hooks, fetch, merge, rebase, or commit.

Ambient Git configuration that could alter evidence is disabled, normalized, or recorded according to the controlling transition and reproduction contracts.

### `gitdrift.adapters.extractors`

Implements versioned extractor ports. The first extractors are limited to artifact kinds accepted by the milestone and acceptance fixtures, initially Markdown structure and Python symbols where implemented.

Each extractor declares stable identity, version, accepted inputs, produced fact kinds, determinism class, cost class, configuration schema, and limitations. Unsupported bytes remain exact evidence and reduce semantic completeness where applicable.

Extractors do not establish controlling authority or final regression judgments.

### `gitdrift.adapters.obligations`

Loads and validates explicit obligation sets and repository-local authority declarations accepted by the request.

Loading preserves obligation-set identity, source evidence, schema or configuration version, and diagnostics. The adapter cannot infer obligations from proximity, repeated wording, branch names, or file location alone.

### `gitdrift.adapters.serialization`

Maps accepted domain records to canonical native JSON and validates them against packaged native schemas.

Serialization owns no semantic decisions. Record identity is independent of array order. Canonical ordering is explicit for reproducibility and does not replace stable identifiers.

Human text and Markdown, when present in 0.1, are non-authoritative projections over accepted native results.

### `gitdrift.adapters.sinks`

Implements explicit byte sinks such as an in-memory sink, caller-supplied binary stream, stdout adapter, or explicitly selected file destination.

A sink receives complete serialized bytes. Partial writes, close failures, and destination failures are reported as sink failures and never as successful artifacts.

### `gitdrift.schemas`

Contains packaged, versioned native JSON schemas and configuration schemas required by implemented capabilities.

Schema resources are loaded through package-resource APIs rather than repository-relative paths. Installed wheels and source distributions therefore behave independently of the source checkout layout.

### `gitdrift.cli`

Owns argument parsing, input-manifest loading, composition selection, standard-stream behavior, human diagnostics, and exit-status mapping.

The CLI converts flags into the same explicit application request model used by library callers. It writes requested machine output to stdout or an explicit sink and diagnostics to stderr. A represented finding does not become process failure unless a future separately specified gate command defines that behavior.

### `gitdrift.composition`

Provides the supported composition root for the installed product. It binds concrete adapters to ports, advertises actual capabilities, and constructs profile services.

Composition failure is an explicit configuration or capability failure. The composition root does not use dynamic imports from analyzed repositories and does not advertise deferred adapters.

## Dependency direction and enforcement

Allowed compile-time dependencies are:

```text
domain <- ports <- application <- profiles
   ^         ^          ^           ^
   |         |          |           |
   +------ adapters -----+-----------+
                         ^
                         |
                    composition <- cli
```

The diagram expresses semantic direction:

- domain depends on no higher layer;
- ports depend on domain contracts;
- application depends on domain and ports;
- profiles depend on application and stable domain contracts;
- adapters implement ports and may depend on domain types;
- composition depends on concrete adapters and application/profile constructors;
- CLI depends on composition and public request/result contracts.

Prohibited edges include:

```text
domain -> adapters
 domain -> CLI
 application -> CLI
 application -> concrete Git implementation
 extractor -> renderer
 serializer -> repository acquisition
 profile -> subprocess invocation
 adapter -> higher-level judgment policy
 any runtime package -> tests or external acceptance corpora
```

Architecture tests mechanically enforce permitted import edges. Public import tests ensure that internal restructuring does not accidentally expand the supported API.

## Public API boundary

The supported 0.1 API is use-case-oriented and intentionally small. Public exports are declared explicitly from controlled package entry points; importing arbitrary internal modules is unsupported.

The public boundary includes only accepted request and result types, supported profile operations, capability discovery, native serialization or validation operations needed by callers, and documented exceptions for invalid requests or failed execution prerequisites.

Public operations do not:

- accept `argparse` objects;
- write to stdout or stderr;
- terminate the process;
- depend on a current working directory;
- search for configuration implicitly outside the request contract;
- return adapter-specific process objects; or
- hide selected states, comparison options, extractor versions, obligation identity, budgets, or completeness from reproduction metadata.

## 0.1 execution flow

A state-awareness analysis follows this sequence:

```text
validate request and configuration
  -> discover repository and active capabilities
  -> capture immutable HEAD and optional upstream targets
  -> capture requested index and working-tree provisional states
  -> verify capture stability
  -> construct required and requested comparisons
  -> preserve exact snapshots and raw changes
  -> run supported deterministic extractors
  -> load and evaluate explicit obligations
  -> search configured counterevidence scope
  -> build bounded cases and completeness declarations
  -> assemble the native investigation
  -> validate against the native schema
  -> serialize canonical JSON
  -> deliver complete bytes to the selected sink
```

Every stage contributes diagnostics and completeness effects. A later stage cannot upgrade incomplete evidence produced by an earlier stage.

## State capture and Git safety

Committed states retain immutable commit, tree, blob, mode, and parent identities. Mutable refs are captured as locators plus immutable targets.

Index capture records stages, modes, object identities, base state, and unmerged entries. Working-tree capture records exact selected bytes, modes, symlink treatment, deletion, and declared untracked and ignored-file policies.

Capture uses before-and-after observations sufficient to detect relevant mutation. A changing provisional state produces a bounded retry or explicit partial/failure outcome according to policy. It is never labeled reproducible without evidence.

Temporary files or in-memory objects used by adapters live outside the analyzed repository state. Tests verify that refs, `HEAD`, index, tracked and selected untracked bytes, configuration, and hooks are unchanged.

## Native data and schema architecture

Canonical native JSON is the only authoritative serialized investigation format in 0.1.

The root investigation contains the contractually defined manifest, states, comparisons, transitions, artifact changes, facts, obligations, evaluations, cases, completeness, resources, and diagnostics supported by the accepted schema version.

All cross-record relations use stable identifiers. Every reference either resolves in the document or names an explicit retrievable evidence reference. Unknown required semantics fail compatibility checks rather than being coerced.

Package version, native schema version, configuration version, extractor version, obligation-set identity, identity scheme, and policy version remain independent version domains.

## Configuration architecture

Configuration is explicit, versioned, schema-validated input. Precedence among profile request, input manifest, and CLI flags is deterministic and reproduced in the analysis manifest.

Repository-local configuration is untrusted evidence. It may select supported obligations or policies only through accepted schemas and cannot disable read-only safety, provenance, completeness, compatibility, or path restrictions.

No 0.1 behavior depends on undeclared global user configuration, aliases, hooks, current terminal state, or hosted-service metadata.

## Diagnostics and failure architecture

Analytical outcomes and execution conditions remain separate.

The repository implementation supports the controlling categories:

```text
completed
completed unresolved
completed partial
unsupported input or capability
state changed during capture
evidence unavailable
invalid configuration or request
internal execution failure
serialization or validation failure
output sink failure
```

Stable diagnostic codes are data contracts; human messages are not. Exceptions cross a public library boundary only for documented invalid invocation or execution failures. Findings, unresolved cases, and partial analytical results remain typed data.

## Resource architecture

Every analysis accepts and reproduces supported budgets. Accounting includes mechanically known objects, commits, edges, trees, blobs, bytes, transitions, comparisons, extractor executions, obligation evaluations, cases, cache use if any, and truncation.

Budget exhaustion preserves valid evidence, emits diagnostics, reduces affected completeness, and prevents unsupported absence or equivalence claims.

Persistent caching is not required for 0.1. Any incidental process-local memoization is derived, disposable, bounded to the request, and semantically invisible. A future persistent cache must implement the accepted cache-key, provenance, compatibility, completeness, and trust-boundary contract without changing public use cases.

## Test architecture

Tests mirror architectural boundaries:

```text
unit          pure domain invariants and deterministic functions
contract      every port and adapter conformance suite
integration   installed composition over controlled repositories
acceptance    complete state-awareness scenarios and native artifacts
property      identities, ordering, completeness, reference closure, and invariants
adversarial   hostile paths, blobs, content, configuration, races, and budgets
fixtures      reproducible repositories, manifests, obligations, and golden JSON
```

A concrete adapter is accepted only through its shared contract suite. Alternate implementations must pass the same evidence, diagnostics, safety, and completeness expectations.

Golden native JSON is validated structurally and semantically. Tests avoid treating incidental formatting or list position as identity.

## Acceptance corpora

Synthetic fixtures are the primary deterministic proof mechanism. Pinned immutable states from `dx-artifacts` provide the independent real-repository acceptance corpus for the 0.1 state-awareness profile.

Acceptance-corpus acquisition is outside the installed runtime. Tests skip with an explicit unavailable-fixture result only where the test tier permits it; release evidence cannot claim corpus acceptance when the corpus was not executed.

`Dx.Domain` supports later divergence acceptance and remains outside the 0.1 runtime and required state-awareness gate.

## Packaging and installation

The source distribution and wheel include:

```text
supported Python package modules
py.typed marker when public typing is shipped
native and configuration schemas
license and required package metadata
```

They exclude test corpora, mutable caches, local repository paths, build outputs not required at runtime, and source-checkout assumptions.

Acceptance includes installation into an isolated environment followed by import, capability discovery, schema loading, native validation, and the supported CLI smoke path without the repository root on `PYTHONPATH`.

## Validation and release gates

The repository provides one canonical validation entry point under `scripts/validation/`. The script is an adapter over ordinary project tooling and does not contain product semantics.

The 0.1 gate covers:

```text
format and static checks selected by the project
unit and property tests
port and adapter conformance
integration and profile acceptance
read-only mutation sentinels
determinism and repeated-run checks
native schema validation
compatibility fixtures
adversarial and resource-exhaustion scenarios
wheel and source-distribution build
isolated installation and smoke tests
documentation link and architecture-boundary checks
```

A gate records tool versions and fails when a required tier is skipped, unavailable, or partial unless the release policy explicitly classifies that tier as non-required.

## Cross-platform boundary

The domain and application layers are platform-neutral. Git and filesystem adapters normalize and expose supported platform behavior explicitly.

Tests cover supported path forms, encoding, executable modes, symlinks, line endings, subprocess streams, and Git object formats. Platform limitations become capabilities and diagnostics. They do not silently alter native meaning.

## Security architecture

Repositories, paths, blobs, configuration, parser inputs, and embedded instructions are untrusted.

The implementation:

- never executes repository content;
- uses argument-vector subprocess invocation rather than shell interpolation;
- bounds bytes, parser work, subprocess output, and traversal;
- rejects or explicitly represents unsafe and unsupported paths;
- does not follow symlinks into arbitrary host content;
- treats submodules as separate repository boundaries;
- excludes secrets and unrelated environment data from diagnostics;
- loads no code or plugins from analyzed repositories; and
- keeps AI, forge, and network adapters absent from the 0.1 composition.

## Deferred extension seams

The architecture permits later capabilities through existing boundaries without placing them in 0.1:

```text
additional profiles compose application use cases
new repository backends implement repository ports
new extractors implement versioned extractor ports
persistent caches implement derived-data adapters
SARIF and DX implement downstream projections or transports
AI and human review produce attributed assessments
forge providers produce separately captured external evidence
streaming serializers preserve native identities and omission accounting
```

An extension is future-compatible only when it preserves domain identity, evidence class, provenance, completeness, trust boundaries, compatibility, and read-only behavior. Extension seams are not promises that a capability is installed or supported.

## Explicit 0.1 exclusions

The repository architecture does not implement or advertise as available:

```text
all-branch archaeology
complete file or concept lineage
split and merge inference
AI-assisted assessment
forge metadata acquisition
SARIF export
DX evidence export
persistent checkpoints or shared caches
repository mutation or automatic fixes
plugin loading from analyzed repositories
opaque composite risk or regression scoring
hosted Gitdrift services
```

Those exclusions do not prohibit future adapters or profiles after their contracts and acceptance boundaries are established.

## Completion criteria

The 0.1 repository architecture is complete only when:

1. dependency direction is mechanically enforced;
2. public imports and use cases are explicit;
3. state capture and comparison execute through ports and read-only adapters;
4. native JSON validates and all references close;
5. partial analysis and failures are distinguishable;
6. resource exhaustion cannot produce false completeness;
7. mutation sentinels pass;
8. deterministic reruns are semantically identical;
9. wheel and source distribution work outside the checkout;
10. the state-awareness acceptance corpus passes from the installed composition; and
11. documentation, schemas, tests, and implemented capabilities describe the same 0.1 product boundary.
