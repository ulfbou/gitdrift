# Gitdrift gate runners

This directory owns the reproducible execution environments for Gitdrift acceptance gates.

The runner image and the candidate are separate identities. Images contain the runtime, Git, the shared entrypoint, and the named-gate manifest. They never contain a Gitdrift candidate. A caller supplies `candidate.bundle`, its SHA-256, and the expected commit and tree.

## Platform roles

- `Dockerfile.linux` provides reproducible Linux-container execution.
- `Dockerfile.windows` provides reproducible Windows Server-container execution.
- Native Windows observation remains a separate required platform perspective. A Windows container does not silently replace native Windows evidence.

## Isolation contract

Callers must run containers with no network, a read-only root filesystem where supported, dropped capabilities where supported, bounded resources, a read-only request mount, and one writable evidence mount. The entrypoint rejects an unknown gate, verifies bundle identity, checks commit and tree identity, requires a clean candidate before execution, and fails when the gate mutates the candidate.

## Linux build

Build from this directory and bind the image to the repository revision:

```text
docker build --file Dockerfile.linux --build-arg RUNNER_REVISION=<commit> --tag gitdrift-gate-runner:python311-v1 .
```

The Linux base is pinned by digest.

## Windows build

Windows Docker Desktop must use the Windows engine. Supply an independently pinned MinGit archive; host-installed Git is not copied into the image.

```text
docker build --isolation=hyperv --file Dockerfile.windows --build-arg RUNNER_REVISION=<commit> --build-arg MINGIT_URL=<url> --build-arg MINGIT_SHA256=<sha256> --tag gitdrift-gate-runner-windows:python311-ltsc2022-v1 .
```

Record the resolved Windows base-image digest, MinGit URL and SHA-256, image ID, and runner revision in build evidence. Registry publication, SBOM and provenance attestations are follow-up infrastructure boundaries.
