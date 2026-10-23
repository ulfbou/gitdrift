from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = (
    pathlib.Path(__file__).parents[1]
    / "scripts"
    / "gates"
    / "gate_runner.py"
)

SPEC = importlib.util.spec_from_file_location(
    "gitdrift_gate_runner",
    MODULE_PATH,
)
assert SPEC is not None
assert SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class GateRunnerHostTests(unittest.TestCase):
    def test_require_identity_rejects_commit_mismatch(self) -> None:
        with self.assertRaisesRegex(
            runner.RunnerError,
            "candidate commit mismatch",
        ):
            runner.require_identity(
                {
                    "branch": "test/branch",
                    "commit": "actual",
                    "tree": "tree",
                },
                expected_branch="test/branch",
                expected_commit="expected",
                expected_tree="tree",
            )

    def test_windows_build_requires_pinned_mingit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            context = pathlib.Path(temporary)
            with self.assertRaisesRegex(
                runner.RunnerError,
                "--mingit-url is required",
            ):
                runner.build_command(
                    platform_name="windows",
                    context=context,
                    image="runner:test",
                    revision="abc",
                    mingit_url=None,
                    mingit_sha256=None,
                )

    def test_windows_build_passes_hyperv_and_mingit_identity(self) -> None:
        command = runner.build_command(
            platform_name="windows",
            context=pathlib.Path("context"),
            image="runner:test",
            revision="abc",
            mingit_url="https://example.invalid/mingit.zip",
            mingit_sha256="a" * 64,
        )
        self.assertIn("--isolation=hyperv", command)
        self.assertIn(
            "MINGIT_URL=https://example.invalid/mingit.zip",
            command,
        )
        self.assertIn("MINGIT_SHA256=" + "a" * 64, command)

    def test_linux_run_enforces_network_and_read_only_controls(self) -> None:
        command = runner.gate_run_command(
            platform_name="linux",
            image="runner:test",
            request_dir=pathlib.Path("request"),
            evidence_dir=pathlib.Path("evidence"),
            gate="platform-observation",
            identity={
                "branch": "test/branch",
                "commit": "commit",
                "tree": "tree",
            },
            bundle_sha256="b" * 64,
        )
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("ALL", command)
        self.assertIn("no-new-privileges", command)
        self.assertIn("/workspace:rw,nosuid,size=1g", command)

    def test_validate_inspection_rejects_embedded_candidate(self) -> None:
        payload = json.dumps(
            {
                "schema": "gitdrift-gate-runner-inspection-v1",
                "runner_contract": runner.RUNNER_CONTRACT,
                "platform_system": "Linux",
                "candidate_embedded": True,
                "known_gates": ["platform-observation"],
                "outcome": "pass",
            }
        )
        with self.assertRaisesRegex(
            runner.RunnerError,
            "unexpectedly embeds",
        ):
            runner.validate_inspection(
                payload,
                platform_name="linux",
            )

    def test_validate_gate_outputs_requires_exact_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            evidence = pathlib.Path(temporary)
            (evidence / "gate-execution.json").write_text(
                json.dumps(
                    {
                        "schema": "gitdrift-gate-execution-v1",
                        "gate": "platform-observation",
                        "candidate": {
                            "commit": "wrong",
                            "tree": "tree",
                        },
                        "mutation_sentinel": {"outcome": "pass"},
                        "outcome": "pass",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                runner.RunnerError,
                "commit mismatch",
            ):
                runner.validate_gate_outputs(
                    evidence,
                    identity={
                        "branch": "test/branch",
                        "commit": "commit",
                        "tree": "tree",
                    },
                    gate="platform-observation",
                )

    def test_create_bundle_binds_exact_head(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            repository = root / "repository"
            repository.mkdir()
            runner.execute(("git", "init", "--quiet", str(repository)))
            runner.git(repository, "config", "user.name", "Gitdrift Test")
            runner.git(
                repository,
                "config",
                "user.email",
                "gitdrift@example.invalid",
            )
            (repository / "tracked.txt").write_text(
                "tracked\n",
                encoding="utf-8",
                newline="\n",
            )
            runner.git(repository, "add", "tracked.txt")
            runner.git(repository, "commit", "--quiet", "-m", "fixture")
            commit = runner.git(repository, "rev-parse", "HEAD")
            bundle = root / "candidate.bundle"
            digest = runner.create_bundle(repository, bundle, commit)
            self.assertEqual(digest, runner.sha256_file(bundle))
            heads = runner.execute(
                ("git", "bundle", "list-heads", str(bundle))
            ).stdout.splitlines()
            self.assertEqual(
                {line.split(maxsplit=1)[0] for line in heads},
                {commit},
            )

    @patch.object(runner, "docker_os", return_value="linux")
    def test_require_engine_rejects_other_platform(
        self,
        _docker_os: object,
    ) -> None:
        with self.assertRaisesRegex(
            runner.RunnerError,
            "Docker engine mismatch",
        ):
            runner.require_engine("windows")


if __name__ == "__main__":
    unittest.main()
