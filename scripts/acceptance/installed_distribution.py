#!/usr/bin/env python3
"""Prove wheel and sdist installation outside the source checkout."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any, Sequence


class AcceptanceFailure(RuntimeError):
    """The installed-distribution acceptance boundary failed."""


def _run(
    arguments: Sequence[str],
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(arguments),
        cwd=cwd,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if completed.returncode:
        raise AcceptanceFailure(
            f"command failed ({completed.returncode}): "
            f"{' '.join(arguments)}\n{completed.stderr.strip()}"
        )
    return completed


def _git_archive(
    root: Path,
    destination: Path,
) -> None:
    completed = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD"],
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if completed.returncode:
        detail = completed.stderr.decode(
            "utf-8",
            errors="replace",
        ).strip()
        raise AcceptanceFailure(
            "git archive failed "
            f"({completed.returncode}): {detail}"
        )

    destination.mkdir()

    with tarfile.open(
        fileobj=io.BytesIO(completed.stdout),
        mode="r:",
    ) as archive:
        archive.extractall(
            destination,
            filter="data",
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _venv_python(root: Path) -> Path:
    if os.name == "nt":
        return root / "Scripts" / "python.exe"
    return root / "bin" / "python"


def _clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def _artifact_kind(path: Path) -> str:
    name = path.name
    if name.endswith(".whl"):
        return "wheel"
    if name.endswith(".tar.gz"):
        return "sdist"
    raise AcceptanceFailure(
        f"unexpected distribution artifact: {name}"
    )


def _installed_probe(
    python: Path,
    *,
    working_directory: Path,
    environment: dict[str, str],
) -> dict[str, Any]:
    program = r'''
import json
import pathlib
import gitdrift
from gitdrift.adapters.serialization import load_native_schema

discovery = gitdrift.discover_capabilities().to_dict()
schema = load_native_schema()
module_path = pathlib.Path(gitdrift.__file__).resolve()

print(json.dumps({
    "module_path": str(module_path),
    "package_version": gitdrift.__version__,
    "native_schema_version": gitdrift.NATIVE_SCHEMA_VERSION,
    "schema_id": schema["$id"],
    "schema_version": schema["x-gitdrift-schema-version"],
    "public_exports": sorted(gitdrift.__all__),
    "discovery": discovery,
}, sort_keys=True))
'''
    completed = _run(
        [str(python), "-I", "-c", program],
        cwd=working_directory,
        environment=environment,
    )
    try:
        document = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise AcceptanceFailure(
            "installed probe did not emit valid JSON"
        ) from error

    if not isinstance(document, dict):
        raise AcceptanceFailure(
            "installed probe root is not an object"
        )

    return document


def _verify_probe(
    probe: dict[str, Any],
    *,
    checkout: Path,
) -> None:
    module_path = Path(probe["module_path"]).resolve()

    try:
        module_path.relative_to(checkout)
    except ValueError:
        pass
    else:
        raise AcceptanceFailure(
            "installed probe imported gitdrift from the source checkout"
        )

    if probe["schema_id"] != (
        "https://gitdrift.dev/schemas/investigation/v1"
    ):
        raise AcceptanceFailure(
            "installed schema identity is incorrect"
        )

    if probe["schema_version"] != "1.0.0":
        raise AcceptanceFailure(
            "installed schema version is incorrect"
        )

    discovery = probe["discovery"]
    profiles = discovery["profiles"]
    operations = discovery["operations"]

    if profiles["available"] != ["state-awareness"]:
        raise AcceptanceFailure(
            "installed available profile declaration is incorrect"
        )

    expected_unavailable_profiles = {
        "divergence",
        "file-lineage",
        "forensics",
    }

    if not expected_unavailable_profiles <= set(
        profiles["unavailable"]
    ):
        raise AcceptanceFailure(
            "installed deferred profiles are not all unavailable"
        )

    expected_available_operations = {
        "capability-discovery",
        "repository-acquisition",
        "state-comparison",
        "native-investigation-serialization",
    }
    required_unavailable_operations = {
        "ai-assessment",
        "dx-export",
        "repository-mutation",
        "sarif-export",
    }

    available_operations = set(operations["available"])
    unavailable_operations = set(operations["unavailable"])

    overclaimed_operations = (
        available_operations
        & required_unavailable_operations
    )
    if overclaimed_operations:
        raise AcceptanceFailure(
            "installed deferred operations are overclaimed: "
            + ", ".join(sorted(overclaimed_operations))
        )

    if available_operations != expected_available_operations:
        raise AcceptanceFailure(
            "installed available operation declaration is incorrect"
        )

    if not required_unavailable_operations <= unavailable_operations:
        raise AcceptanceFailure(
            "installed deferred operations are overclaimed"
        )

    if probe["package_version"] == probe["native_schema_version"]:
        raise AcceptanceFailure(
            "package and native-schema versions are not independent"
        )


def _build(
    root: Path,
    destination: Path,
) -> tuple[Path, Path]:
    build_environment = _clean_environment()
    build_environment.pop("PYTHONNOUSERSITE", None)

    _run(
        [
            sys.executable,
            "-m",
            "build",
            "--outdir",
            str(destination),
            str(root),
        ],
        cwd=root,
        environment=build_environment,
    )

    artifacts = sorted(destination.iterdir())
    wheels = [
        item
        for item in artifacts
        if item.name.endswith(".whl")
    ]
    sdists = [
        item
        for item in artifacts
        if item.name.endswith(".tar.gz")
    ]

    if len(wheels) != 1 or len(sdists) != 1:
        raise AcceptanceFailure(
            "build must produce exactly one wheel and one sdist"
        )

    return wheels[0], sdists[0]


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()

    candidate = _run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
    ).stdout.strip()

    status = _run(
        ["git", "status", "--porcelain=v1"],
        cwd=root,
    ).stdout

    if status:
        raise AcceptanceFailure(
            "installed-distribution acceptance requires a clean candidate"
        )

    source_root = root.resolve()
    environment = _clean_environment()

    with tempfile.TemporaryDirectory(
        prefix="gitdrift-installed-distribution-"
    ) as directory:
        temporary = Path(directory)

        distributions = temporary / "dist"
        distributions.mkdir()

        probe_directory = temporary / "probe"
        probe_directory.mkdir()

        build_source = temporary / "source"
        _git_archive(root, build_source)

        wheel, sdist = _build(
            build_source,
            distributions,
        )
        results: list[dict[str, Any]] = []

        for artifact in (wheel, sdist):
            kind = _artifact_kind(artifact)
            environment_root = temporary / f"venv-{kind}"

            _run(
                [
                    sys.executable,
                    "-m",
                    "venv",
                    str(environment_root),
                ],
                cwd=temporary,
                environment=environment,
            )

            python = _venv_python(environment_root)

            _run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--no-deps",
                    str(artifact),
                ],
                cwd=probe_directory,
                environment=environment,
            )

            probe = _installed_probe(
                python,
                working_directory=probe_directory,
                environment=environment,
            )

            _verify_probe(
                probe,
                checkout=source_root,
            )

            cli = _run(
                [
                    str(python),
                    "-I",
                    "-m",
                    "gitdrift",
                    "discover",
                ],
                cwd=probe_directory,
                environment=environment,
            )

            try:
                cli_document = json.loads(cli.stdout)
            except json.JSONDecodeError as error:
                raise AcceptanceFailure(
                    "CLI discovery did not emit valid JSON"
                ) from error

            if cli_document != probe["discovery"]:
                raise AcceptanceFailure(
                    "CLI and library discovery documents differ"
                )

            if cli.stderr:
                raise AcceptanceFailure(
                    "CLI discovery emitted diagnostics on stderr"
                )

            results.append(
                {
                    "artifact_kind": kind,
                    "artifact_name": artifact.name,
                    "artifact_bytes": artifact.stat().st_size,
                    "artifact_sha256": _sha256(artifact),
                    "probe": probe,
                    "cli_library_equivalent": True,
                }
            )

        left = dict(results[0]["probe"])
        right = dict(results[1]["probe"])
        left.pop("module_path", None)
        right.pop("module_path", None)

        if left != right:
            raise AcceptanceFailure(
                "wheel and sdist installed behavior differs"
            )

        return {
            "schema": (
                "gitdrift-installed-distribution-acceptance-v1"
            ),
            "candidate_commit": candidate,
            "source_checkout": str(source_root),
            "artifacts": results,
            "outcome": "pass",
        }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    arguments = _parser().parse_args(argv)

    try:
        result = run(arguments.root)

        payload = (
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n"
        )

        arguments.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        arguments.output.write_text(
            payload,
            encoding="utf-8",
            newline="\n",
        )

        return 0
    except AcceptanceFailure as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
