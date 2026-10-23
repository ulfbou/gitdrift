from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest

REPOSITORY_ROOT = pathlib.Path(__file__).parents[1]
ENTRYPOINT_PATH = (
    REPOSITORY_ROOT
    / "containers"
    / "gate-runner"
    / "entrypoint.py"
)
MANIFEST_PATH = (
    REPOSITORY_ROOT
    / "containers"
    / "gate-runner"
    / "gates.json"
)

SPEC = importlib.util.spec_from_file_location(
    "gitdrift_gate_runner_entrypoint",
    ENTRYPOINT_PATH,
)
assert SPEC is not None
assert SPEC.loader is not None
entrypoint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(entrypoint)


def git(
    root: pathlib.Path,
    *arguments: str,
) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def create_repository(root: pathlib.Path) -> dict[str, str]:
    subprocess.run(
        ("git", "init", "--quiet", str(root)),
        check=True,
    )
    git(root, "config", "user.name", "Gitdrift Test")
    git(root, "config", "user.email", "gitdrift@example.invalid")
    (root / "tracked.txt").write_text(
        "tracked\n",
        encoding="utf-8",
        newline="\n",
    )
    git(root, "add", "tracked.txt")
    git(root, "commit", "--quiet", "-m", "test fixture")
    return {
        "commit": git(root, "rev-parse", "HEAD"),
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
    }


def create_bundle(
    repository: pathlib.Path,
    destination: pathlib.Path,
    commit: str,
) -> str:
    subprocess.run(
        (
            "git",
            "-C",
            str(repository),
            "bundle",
            "create",
            str(destination),
            "HEAD",
        ),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return entrypoint.sha256_file(destination)


class GateRunnerEntrypointTests(unittest.TestCase):
    def test_manifest_declares_platform_observation(self) -> None:
        gates = entrypoint.load_manifest(MANIFEST_PATH)
        self.assertEqual(
            set(gates),
            {"platform-observation"},
        )
        self.assertIn(
            "scripts/acceptance/platform_observation.py",
            gates["platform-observation"],
        )

    def test_manifest_rejects_unknown_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "gates.json"
            path.write_text(
                json.dumps(
                    {
                        "schema": "unknown-v1",
                        "runner_contract": (
                            entrypoint.RUNNER_CONTRACT
                        ),
                        "gates": {
                            "gate": {
                                "command": ["python", "gate.py"]
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "unsupported gate manifest schema",
            ):
                entrypoint.load_manifest(path)

    def test_manifest_rejects_invalid_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "gates.json"
            path.write_text(
                json.dumps(
                    {
                        "schema": "gitdrift-gate-manifest-v1",
                        "runner_contract": (
                            entrypoint.RUNNER_CONTRACT
                        ),
                        "gates": {
                            "gate": {"command": []}
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "non-empty array",
            ):
                entrypoint.load_manifest(path)

    def test_prepare_candidate_checks_commit_tree_and_clean_state(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            source = root / "source"
            request = root / "request"
            workspace = root / "workspace"
            source.mkdir()
            request.mkdir()
            identity = create_repository(source)
            bundle = request / "candidate.bundle"
            bundle_hash = create_bundle(
                source,
                bundle,
                identity["commit"],
            )
            candidate = entrypoint.prepare_candidate(
                request_dir=request,
                workspace=workspace,
                expected_commit=identity["commit"],
                expected_tree=identity["tree"],
                expected_bundle_sha256=bundle_hash,
            )
            self.assertEqual(candidate, {
                "commit": identity["commit"],
                "tree": identity["tree"],
                "bundle_sha256": bundle_hash,
            })
            self.assertEqual(
                git(
                    workspace,
                    "status",
                    "--porcelain=v1",
                    "--untracked-files=all",
                ),
                "",
            )

    def test_prepare_candidate_rejects_bundle_hash_mismatch(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            source = root / "source"
            request = root / "request"
            workspace = root / "workspace"
            source.mkdir()
            request.mkdir()
            identity = create_repository(source)
            bundle = request / "candidate.bundle"
            create_bundle(source, bundle, identity["commit"])
            with self.assertRaisesRegex(
                RuntimeError,
                "bundle SHA-256 mismatch",
            ):
                entrypoint.prepare_candidate(
                    request_dir=request,
                    workspace=workspace,
                    expected_commit=identity["commit"],
                    expected_tree=identity["tree"],
                    expected_bundle_sha256="0" * 64,
                )

    def test_prepare_candidate_rejects_tree_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            source = root / "source"
            request = root / "request"
            workspace = root / "workspace"
            source.mkdir()
            request.mkdir()
            identity = create_repository(source)
            bundle = request / "candidate.bundle"
            bundle_hash = create_bundle(
                source,
                bundle,
                identity["commit"],
            )
            with self.assertRaisesRegex(
                RuntimeError,
                "candidate tree mismatch",
            ):
                entrypoint.prepare_candidate(
                    request_dir=request,
                    workspace=workspace,
                    expected_commit=identity["commit"],
                    expected_tree="0" * 40,
                    expected_bundle_sha256=bundle_hash,
                )

    def test_sha256_file_is_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "payload.bin"
            payload = b"gitdrift\x00gate\r\nrunner\n"
            path.write_bytes(payload)
            self.assertEqual(
                entrypoint.sha256_file(path),
                hashlib.sha256(payload).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
