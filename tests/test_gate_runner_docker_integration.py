from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

REPOSITORY_ROOT = pathlib.Path(__file__).parents[1]
HOST_RUNNER_PATH = (
    REPOSITORY_ROOT
    / "scripts"
    / "gates"
    / "gate_runner.py"
)
RUNNER_CONTEXT = (
    REPOSITORY_ROOT
    / "containers"
    / "gate-runner"
)
INTEGRATION_FLAG = "GITDRIFT_DOCKER_INTEGRATION"
WINDOWS_MINGIT_URL = "GITDRIFT_WINDOWS_MINGIT_URL"
WINDOWS_MINGIT_SHA256 = "GITDRIFT_WINDOWS_MINGIT_SHA256"

SPEC = importlib.util.spec_from_file_location(
    "gitdrift_gate_runner_integration",
    HOST_RUNNER_PATH,
)
assert SPEC is not None
assert SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def integration_enabled() -> bool:
    return os.environ.get(INTEGRATION_FLAG) == "1"


class GateEntrypointTemplateTests(unittest.TestCase):
    def test_manifest_uses_embedded_evidence_placeholder(self) -> None:
        manifest_path = RUNNER_CONTEXT / "gates.json"
        document = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
        command = document["gates"]["platform-observation"]["command"]
        self.assertIn(
            "{evidence}/gitdrift-platform-observation.json",
            command,
        )



def execute(
    *command: str,
    cwd: pathlib.Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if check and completed.returncode != 0:
        rendered = " ".join(command)
        raise AssertionError(
            f"command failed ({completed.returncode}): {rendered}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed


def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    return execute(
        "docker",
        "version",
        check=False,
    ).returncode == 0


def docker_os() -> str | None:
    if not docker_available():
        return None
    completed = execute(
        "docker",
        "info",
        "--format",
        "{{.OSType}}",
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip().lower()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_identity() -> dict[str, str]:
    return {
        "commit": execute(
            "git",
            "rev-parse",
            "HEAD",
            cwd=REPOSITORY_ROOT,
        ).stdout.strip(),
        "tree": execute(
            "git",
            "rev-parse",
            "HEAD^{tree}",
            cwd=REPOSITORY_ROOT,
        ).stdout.strip(),
        "status": execute(
            "git",
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            cwd=REPOSITORY_ROOT,
        ).stdout,
    }


def remove_image(image: str) -> None:
    execute(
        "docker",
        "image",
        "rm",
        "--force",
        image,
        check=False,
    )


@unittest.skipUnless(
    integration_enabled(),
    f"set {INTEGRATION_FLAG}=1 to run Docker integration tests",
)
class LinuxDockerIntegrationTests(unittest.TestCase):
    image = "gitdrift-gate-runner:integration-linux"

    @classmethod
    def setUpClass(cls) -> None:
        if docker_os() != "linux":
            raise unittest.SkipTest(
                "Docker Linux engine is unavailable"
            )
        identity = repository_identity()
        if identity["status"]:
            raise unittest.SkipTest(
                "repository must be clean for exact-candidate integration"
            )
        cls.identity = identity
        execute(
            "docker",
            "build",
            "--file",
            str(RUNNER_CONTEXT / "Dockerfile.linux"),
            "--build-arg",
            f"RUNNER_REVISION={identity['commit']}",
            "--tag",
            cls.image,
            str(RUNNER_CONTEXT),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        if os.environ.get("GITDRIFT_KEEP_INTEGRATION_IMAGES") != "1":
            remove_image(cls.image)

    def test_image_inspection_contract(self) -> None:
        completed = execute(
            *runner.inspect_command(
                platform_name="linux",
                image=self.image,
            )
        )
        document = runner.validate_inspection(
            completed.stdout,
            platform_name="linux",
        )
        self.assertEqual(
            document["runner_contract"],
            runner.RUNNER_CONTRACT,
        )
        labels = runner.image_labels(self.image)
        runner.verify_labels(
            labels,
            platform_name="linux",
            revision=self.identity["commit"],
        )

    def test_exact_candidate_platform_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            request = root / "request"
            evidence = root / "evidence"
            request.mkdir()
            evidence.mkdir()
            bundle = request / "candidate.bundle"
            execute(
                "git",
                "bundle",
                "create",
                str(bundle),
                "HEAD",
                cwd=REPOSITORY_ROOT,
            )
            heads = execute(
                "git",
                "bundle",
                "list-heads",
                str(bundle),
            ).stdout.splitlines()
            self.assertEqual(
                {line.split(maxsplit=1)[0] for line in heads},
                {self.identity["commit"]},
            )
            bundle_hash = sha256_file(bundle)
            completed = execute(
                *runner.gate_run_command(
                    platform_name="linux",
                    image=self.image,
                    request_dir=request,
                    evidence_dir=evidence,
                    gate="platform-observation",
                    identity={
                        "branch": "",
                        "commit": self.identity["commit"],
                        "tree": self.identity["tree"],
                    },
                    bundle_sha256=bundle_hash,
                )
            )
            self.assertEqual(completed.returncode, 0)
            envelope = runner.validate_gate_outputs(
                evidence,
                identity={
                    "branch": "",
                    "commit": self.identity["commit"],
                    "tree": self.identity["tree"],
                },
                gate="platform-observation",
            )
            self.assertEqual(envelope["outcome"], "pass")
            observation = evidence / "gitdrift-platform-observation.json"
            self.assertTrue(observation.is_file())
            document = json.loads(
                observation.read_text(encoding="utf-8")
            )
            self.assertEqual(
                document["candidate_commit"],
                self.identity["commit"],
            )
            self.assertEqual(
                document["source_tree_identity"],
                self.identity["tree"],
            )
            self.assertEqual(
                document["platform"]["system"],
                "Linux",
            )
            self.assertEqual(document["outcome"], "pass")
        self.assertEqual(repository_identity(), self.identity)


@unittest.skipUnless(
    integration_enabled(),
    f"set {INTEGRATION_FLAG}=1 to run Docker integration tests",
)
class WindowsDockerIntegrationTests(unittest.TestCase):
    image = "gitdrift-gate-runner-windows:integration"

    @classmethod
    def setUpClass(cls) -> None:
        if docker_os() != "windows":
            raise unittest.SkipTest(
                "Docker Windows engine is unavailable"
            )
        identity = repository_identity()
        if identity["status"]:
            raise unittest.SkipTest(
                "repository must be clean for exact-candidate integration"
            )
        cls.identity = identity
        execute(
            *runner.build_command(
                platform_name="windows",
                context=RUNNER_CONTEXT,
                image=cls.image,
                revision=identity["commit"],
            )
        )

    @classmethod
    def tearDownClass(cls) -> None:
        if os.environ.get("GITDRIFT_KEEP_INTEGRATION_IMAGES") != "1":
            remove_image(cls.image)

    def test_image_inspection_contract(self) -> None:
        completed = execute(
            *runner.inspect_command(
                platform_name="windows",
                image=self.image,
            )
        )
        document = runner.validate_inspection(
            completed.stdout,
            platform_name="windows",
        )
        self.assertEqual(
            document["runner_contract"],
            runner.RUNNER_CONTRACT,
        )
        labels = runner.image_labels(self.image)
        runner.verify_labels(
            labels,
            platform_name="windows",
            revision=self.identity["commit"],
        )

    def test_exact_candidate_platform_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            request = root / "request"
            evidence = root / "evidence"
            request.mkdir()
            evidence.mkdir()
            bundle = request / "candidate.bundle"
            execute(
                "git",
                "bundle",
                "create",
                str(bundle),
                "HEAD",
                cwd=REPOSITORY_ROOT,
            )
            heads = execute(
                "git",
                "bundle",
                "list-heads",
                str(bundle),
            ).stdout.splitlines()
            self.assertEqual(
                {line.split(maxsplit=1)[0] for line in heads},
                {self.identity["commit"]},
            )
            bundle_hash = sha256_file(bundle)
            completed = execute(
                *runner.gate_run_command(
                    platform_name="windows",
                    image=self.image,
                    request_dir=request,
                    evidence_dir=evidence,
                    gate="platform-observation",
                    identity={
                        "branch": "",
                        "commit": self.identity["commit"],
                        "tree": self.identity["tree"],
                    },
                    bundle_sha256=bundle_hash,
                )
            )
            self.assertEqual(completed.returncode, 0)
            envelope = runner.validate_gate_outputs(
                evidence,
                identity={
                    "branch": "",
                    "commit": self.identity["commit"],
                    "tree": self.identity["tree"],
                },
                gate="platform-observation",
            )
            self.assertEqual(envelope["outcome"], "pass")
            observation = evidence / "gitdrift-platform-observation.json"
            self.assertTrue(observation.is_file())
            document = json.loads(
                observation.read_text(encoding="utf-8")
            )
            self.assertEqual(
                document["candidate_commit"],
                self.identity["commit"],
            )
            self.assertEqual(
                document["source_tree_identity"],
                self.identity["tree"],
            )
            self.assertEqual(
                document["platform"]["system"],
                "Windows",
            )
            self.assertEqual(document["outcome"], "pass")
        self.assertEqual(repository_identity(), self.identity)


if __name__ == "__main__":
    unittest.main()
