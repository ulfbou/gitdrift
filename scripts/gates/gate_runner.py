from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from typing import Any

RUNNER_CONTRACT = "gitdrift-gate-runner-v1"
DEFAULT_IMAGES = {
    "linux": "gitdrift-gate-runner:python311-v1",
    "windows": "gitdrift-gate-runner-windows:python311-ltsc2022-v1",
}
CONTAINER_PATHS = {
    "linux": {
        "request": "/request",
        "workspace": "/workspace",
        "evidence": "/evidence",
    },
    "windows": {
        "request": r"C:\request",
        "workspace": r"C:\workspace",
        "evidence": r"C:\evidence",
    },
}


class RunnerError(RuntimeError):
    pass


def execute(
    command: Sequence[str],
    *,
    cwd: pathlib.Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        tuple(command),
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if check and completed.returncode != 0:
        rendered = " ".join(command)
        raise RunnerError(
            f"command failed ({completed.returncode}): {rendered}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed


def git(repo: pathlib.Path | str, *arguments: str) -> str:
    return execute(
        ("git", "-C", str(repo), *arguments),
    ).stdout.strip()


def repository_root(value: str) -> pathlib.Path:
    discovered = git(value, "rev-parse", "--show-toplevel")
    return pathlib.Path(discovered)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_identity(repo: pathlib.Path) -> dict[str, str]:
    status = git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        raise RunnerError("repository must be clean")
    return {
        "branch": git(repo, "branch", "--show-current"),
        "commit": git(repo, "rev-parse", "HEAD"),
        "tree": git(repo, "rev-parse", "HEAD^{tree}"),
    }


def require_identity(
    identity: dict[str, str],
    *,
    expected_branch: str | None,
    expected_commit: str | None,
    expected_tree: str | None,
) -> None:
    expected = {
        "branch": expected_branch,
        "commit": expected_commit,
        "tree": expected_tree,
    }
    for key, wanted in expected.items():
        if wanted is not None and identity[key] != wanted:
            raise RunnerError(
                f"candidate {key} mismatch: "
                f"expected={wanted} actual={identity[key]}"
            )


def docker_os() -> str:
    return execute(
        ("docker", "info", "--format", "{{.OSType}}"),
    ).stdout.strip().lower()


def require_engine(platform_name: str) -> None:
    actual = docker_os()
    if actual != platform_name:
        raise RunnerError(
            "Docker engine mismatch: "
            f"expected={platform_name} actual={actual}"
        )


def image_labels(image: str) -> dict[str, str]:
    payload = execute(
        ("docker", "image", "inspect", image),
    ).stdout
    documents = json.loads(payload)
    if not isinstance(documents, list) or len(documents) != 1:
        raise RunnerError("Docker returned an invalid image inspection")
    labels = documents[0].get("Config", {}).get("Labels") or {}
    if not isinstance(labels, dict):
        raise RunnerError("image labels are invalid")
    return {str(key): str(value) for key, value in labels.items()}


def verify_labels(
    labels: dict[str, str],
    *,
    platform_name: str,
    revision: str,
) -> None:
    expected = {
        "dev.gitdrift.runner.contract": RUNNER_CONTRACT,
        "dev.gitdrift.runner.platform": platform_name.capitalize(),
        "dev.gitdrift.runner.candidate-embedded": "false",
        "org.opencontainers.image.revision": revision,
    }
    for key, value in expected.items():
        if labels.get(key) != value:
            raise RunnerError(
                f"image label mismatch: {key}; "
                f"expected={value!r} actual={labels.get(key)!r}"
            )


def build_command(
    *,
    platform_name: str,
    context: pathlib.Path,
    image: str,
    revision: str,
    mingit_url: str | None,
    mingit_sha256: str | None,
) -> tuple[str, ...]:
    dockerfile = context / f"Dockerfile.{platform_name}"
    command = [
        "docker",
        "build",
        "--file",
        str(dockerfile),
        "--build-arg",
        f"RUNNER_REVISION={revision}",
        "--tag",
        image,
    ]
    if platform_name == "windows":
        if not mingit_url:
            raise RunnerError("--mingit-url is required for Windows")
        if not mingit_sha256 or not re.fullmatch(
            r"[0-9a-fA-F]{64}", mingit_sha256
        ):
            raise RunnerError(
                "--mingit-sha256 must be a 64-character SHA-256"
            )
        command.extend(
            (
                "--isolation=hyperv",
                "--build-arg",
                f"MINGIT_URL={mingit_url}",
                "--build-arg",
                f"MINGIT_SHA256={mingit_sha256.lower()}",
            )
        )
    command.append(str(context))
    return tuple(command)


def inspect_command(*, platform_name: str, image: str) -> tuple[str, ...]:
    command = ["docker", "run", "--rm", "--network", "none"]
    if platform_name == "linux":
        command.extend(
            (
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=64m",
                "--tmpfs",
                "/workspace:rw,nosuid,size=256m",
            )
        )
    else:
        command.extend(("--isolation=hyperv",))
    command.extend((image, "inspect"))
    return tuple(command)


def validate_inspection(
    payload: str,
    *,
    platform_name: str,
) -> dict[str, Any]:
    document = json.loads(payload)
    expected_system = "Linux" if platform_name == "linux" else "Windows"
    if document.get("schema") != "gitdrift-gate-runner-inspection-v1":
        raise RunnerError("runner inspection schema mismatch")
    if document.get("runner_contract") != RUNNER_CONTRACT:
        raise RunnerError("runner inspection contract mismatch")
    if document.get("platform_system") != expected_system:
        raise RunnerError("runner inspection platform mismatch")
    if document.get("candidate_embedded") is not False:
        raise RunnerError("runner unexpectedly embeds a candidate")
    if document.get("outcome") != "pass":
        raise RunnerError("runner inspection did not pass")
    if "platform-observation" not in document.get("known_gates", []):
        raise RunnerError("runner lacks platform-observation gate")
    return document


def image_metadata(image: str) -> dict[str, Any]:
    documents = json.loads(
        execute(("docker", "image", "inspect", image)).stdout
    )
    document = documents[0]
    return {
        "image_reference": image,
        "image_id": document.get("Id"),
        "repo_digests": document.get("RepoDigests") or [],
        "created": document.get("Created"),
        "os": document.get("Os"),
        "architecture": document.get("Architecture"),
        "labels": document.get("Config", {}).get("Labels") or {},
    }


def atomic_json(path: pathlib.Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".working")
    temporary.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def build_runner(arguments: argparse.Namespace) -> int:
    repo = repository_root(arguments.repo)
    identity = candidate_identity(repo)
    require_identity(
        identity,
        expected_branch=arguments.expected_branch,
        expected_commit=arguments.expected_commit,
        expected_tree=arguments.expected_tree,
    )
    require_engine(arguments.platform)
    image = arguments.image or DEFAULT_IMAGES[arguments.platform]
    context = repo / "containers" / "gate-runner"
    execute(
        build_command(
            platform_name=arguments.platform,
            context=context,
            image=image,
            revision=identity["commit"],
            mingit_url=arguments.mingit_url,
            mingit_sha256=arguments.mingit_sha256,
        )
    )
    labels = image_labels(image)
    verify_labels(
        labels,
        platform_name=arguments.platform,
        revision=identity["commit"],
    )
    inspection = execute(
        inspect_command(
            platform_name=arguments.platform,
            image=image,
        )
    )
    validate_inspection(
        inspection.stdout,
        platform_name=arguments.platform,
    )
    metadata = {
        "schema": "gitdrift-gate-runner-image-v1",
        "runner_contract": RUNNER_CONTRACT,
        "platform": arguments.platform,
        "candidate_embedded": False,
        "runner_revision": identity["commit"],
        "image": image_metadata(image),
        "inspection": json.loads(inspection.stdout),
        "outcome": "pass",
    }
    atomic_json(pathlib.Path(arguments.metadata), metadata)
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


def create_bundle(
    repo: pathlib.Path,
    destination: pathlib.Path,
    commit: str,
) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    execute(
        (
            "git",
            "-C",
            str(repo),
            "bundle",
            "create",
            str(destination),
            "HEAD",
        )
    )
    listed = execute(
        (
            "git",
            "bundle",
            "list-heads",
            str(destination),
        )
    ).stdout.splitlines()
    heads = {
        line.split(maxsplit=1)[0]
        for line in listed
        if line.strip()
    }
    if heads != {commit}:
        raise RunnerError(
            "candidate bundle head mismatch: "
            f"expected={commit} actual={sorted(heads)}"
        )
    return sha256_file(destination)


def bind_mount(source: pathlib.Path, destination: str, *, readonly: bool) -> str:
    value = f"type=bind,src={source},dst={destination}"
    if readonly:
        value += ",readonly"
    return value


def gate_run_command(
    *,
    platform_name: str,
    image: str,
    request_dir: pathlib.Path,
    evidence_dir: pathlib.Path,
    gate: str,
    identity: dict[str, str],
    bundle_sha256: str,
) -> tuple[str, ...]:
    paths = CONTAINER_PATHS[platform_name]
    command = ["docker", "run", "--rm", "--network", "none"]
    if platform_name == "linux":
        command.extend(
            (
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--pids-limit",
                "256",
                "--memory",
                "1g",
                "--cpus",
                "2",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=128m",
                "--tmpfs",
                "/workspace:rw,nosuid,size=1g",
            )
        )
    else:
        command.extend(("--isolation=hyperv", "--memory", "2g"))
    command.extend(
        (
            "--mount",
            bind_mount(request_dir, paths["request"], readonly=True),
            "--mount",
            bind_mount(evidence_dir, paths["evidence"], readonly=False),
            image,
            "run",
            "--gate",
            gate,
            "--candidate-commit",
            identity["commit"],
            "--candidate-tree",
            identity["tree"],
            "--bundle-sha256",
            bundle_sha256,
            "--request",
            paths["request"],
            "--workspace",
            paths["workspace"],
            "--evidence",
            paths["evidence"],
        )
    )
    return tuple(command)


def validate_gate_outputs(
    evidence_dir: pathlib.Path,
    *,
    identity: dict[str, str],
    gate: str,
) -> dict[str, Any]:
    envelope_path = evidence_dir / "gate-execution.json"
    if not envelope_path.is_file():
        raise RunnerError("gate execution envelope is missing")
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    if envelope.get("schema") != "gitdrift-gate-execution-v1":
        raise RunnerError("gate execution schema mismatch")
    if envelope.get("gate") != gate:
        raise RunnerError("gate execution name mismatch")
    candidate = envelope.get("candidate") or {}
    if candidate.get("commit") != identity["commit"]:
        raise RunnerError("gate execution commit mismatch")
    if candidate.get("tree") != identity["tree"]:
        raise RunnerError("gate execution tree mismatch")
    if envelope.get("mutation_sentinel", {}).get("outcome") != "pass":
        raise RunnerError("gate mutation sentinel did not pass")
    if envelope.get("outcome") != "pass":
        raise RunnerError("gate execution did not pass")
    return envelope


def run_gate(arguments: argparse.Namespace) -> int:
    repo = repository_root(arguments.repo)
    identity = candidate_identity(repo)
    require_identity(
        identity,
        expected_branch=arguments.expected_branch,
        expected_commit=arguments.expected_commit,
        expected_tree=arguments.expected_tree,
    )
    require_engine(arguments.platform)
    image = arguments.image or DEFAULT_IMAGES[arguments.platform]
    labels = image_labels(image)
    verify_labels(
        labels,
        platform_name=arguments.platform,
        revision=identity["commit"],
    )
    evidence_dir = pathlib.Path(arguments.evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    if any(evidence_dir.iterdir()) and not arguments.replace_evidence:
        raise RunnerError(
            "evidence directory is not empty; use --replace-evidence"
        )
    if arguments.replace_evidence:
        for path in evidence_dir.iterdir():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    with tempfile.TemporaryDirectory(
        prefix="gitdrift-gate-request-"
    ) as temporary:
        request_dir = pathlib.Path(temporary)
        bundle = request_dir / "candidate.bundle"
        bundle_hash = create_bundle(
            repo,
            bundle,
            identity["commit"],
        )
        completed = execute(
            gate_run_command(
                platform_name=arguments.platform,
                image=image,
                request_dir=request_dir,
                evidence_dir=evidence_dir,
                gate=arguments.gate,
                identity=identity,
                bundle_sha256=bundle_hash,
            ),
            check=False,
        )
        sys.stdout.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        if completed.returncode != 0:
            raise RunnerError(
                f"container gate failed: {completed.returncode}"
            )
    envelope = validate_gate_outputs(
        evidence_dir,
        identity=identity,
        gate=arguments.gate,
    )
    final_identity = candidate_identity(repo)
    if final_identity != identity:
        raise RunnerError("source repository changed during gate execution")
    print(json.dumps(envelope, indent=2, sort_keys=True))
    return 0


def add_identity_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=".")
    parser.add_argument("--expected-branch")
    parser.add_argument("--expected-commit")
    parser.add_argument("--expected-tree")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="operation",
        required=True,
    )
    build = subparsers.add_parser("build")
    add_identity_arguments(build)
    build.add_argument(
        "--platform",
        choices=("linux", "windows"),
        required=True,
    )
    build.add_argument("--image")
    build.add_argument("--metadata", required=True)
    build.add_argument("--mingit-url")
    build.add_argument("--mingit-sha256")
    run_parser = subparsers.add_parser("run")
    add_identity_arguments(run_parser)
    run_parser.add_argument(
        "--platform",
        choices=("linux", "windows"),
        required=True,
    )
    run_parser.add_argument("--image")
    run_parser.add_argument(
        "--gate",
        default="platform-observation",
    )
    run_parser.add_argument("--evidence-dir", required=True)
    run_parser.add_argument(
        "--replace-evidence",
        action="store_true",
    )
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    try:
        if arguments.operation == "build":
            return build_runner(arguments)
        return run_gate(arguments)
    except (RunnerError, OSError, json.JSONDecodeError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
