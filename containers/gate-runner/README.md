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

Windows Docker Desktop must use the Windows engine. Build and run this image with Hyper-V isolation. Host-installed Git is not copied into the image.

MinGit is a repository-owned dependency: the Dockerfile fixes the x64 MinGit 2.56.0.2 archive URL and SHA-256, verifies the archive before extraction, and asserts the installed Git version. Callers must not supply MinGit coordinates as build arguments.

The Windows base is pinned to both the LTSC 2022 tag and its immutable digest:

```text
mcr.microsoft.com/windows-cssc/python:3.11-servercore-ltsc2022@sha256:b583b4cab3fafc07299e758737b3576aa08e6c62e8c88b5f15434d3bb37954b4
```

Build from this directory and bind the image to the repository revision:

```text
docker build --isolation=hyperv --file Dockerfile.windows --build-arg RUNNER_REVISION=<commit> --tag gitdrift-gate-runner-windows:python311-ltsc2022-v1 .
```

The build metadata records the requested base tag, pinned base digest, MinGit URL and SHA-256, image ID and digest information, and runner revision. Registry publication, SBOM and provenance attestations remain follow-up infrastructure boundaries.
