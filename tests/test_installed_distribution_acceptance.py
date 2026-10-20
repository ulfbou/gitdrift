from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = (
    Path(__file__).parents[1]
    / "scripts"
    / "acceptance"
    / "installed_distribution.py"
)

SPEC = importlib.util.spec_from_file_location(
    "gitdrift_installed_distribution_acceptance",
    SCRIPT,
)

assert SPEC
assert SPEC.loader

acceptance = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = acceptance
SPEC.loader.exec_module(acceptance)


class InstalledDistributionAcceptanceTests(unittest.TestCase):
    def probe(self) -> dict[str, object]:
        return {
            "module_path": (
                "/isolated/site-packages/gitdrift/__init__.py"
            ),
            "package_version": "0.0.0",
            "native_schema_version": "0.1.0-dev",
            "schema_id": (
                "https://gitdrift.dev/schemas/investigation/v1"
            ),
            "schema_version": "1.0.0",
            "public_exports": [],
            "discovery": {
                "profiles": {
                    "available": ["state-awareness"],
                    "unavailable": [
                        "divergence",
                        "file-lineage",
                        "forensics",
                    ],
                },
                "operations": {
                    "available": [
                        "capability-discovery",
                        "repository-acquisition",
                        "state-comparison",
                        "native-investigation-serialization",
                    ],
                    "unavailable": [
                        "semantic-extraction",
                        "obligation-evaluation",
                        "case-construction",
                        "ai-assessment",
                        "sarif-export",
                        "dx-export",
                        "repository-mutation",
                    ],
                },
            },
        }

    def test_valid_installed_probe_passes(self) -> None:
        acceptance._verify_probe(
            self.probe(),
            checkout=Path("/checkout"),
        )

    def test_source_checkout_import_is_rejected(self) -> None:
        probe = self.probe()
        probe["module_path"] = (
            "/checkout/src/gitdrift/__init__.py"
        )

        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "source checkout",
        ):
            acceptance._verify_probe(
                probe,
                checkout=Path("/checkout"),
            )

    def test_verify_probe_resolves_checkout_before_comparison(self):
        probe = self.probe()
        checkout = Path("/checkout")
        probe["module_path"] = str(
            checkout.resolve()
            / "src"
            / "gitdrift"
            / "__init__.py"
        )
        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "source checkout",
        ):
            acceptance._verify_probe(
                probe,
                checkout=checkout,
            )

    def test_deferred_operation_overclaim_is_rejected(
        self,
    ) -> None:
        probe = self.probe()
        operations = probe["discovery"]["operations"]
        operations["unavailable"].remove(
            "repository-mutation"
        )
        operations["available"].append(
            "repository-mutation"
        )

        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "overclaimed",
        ):
            acceptance._verify_probe(
                probe,
                checkout=Path("/checkout"),
            )

    def test_package_and_schema_versions_remain_independent(
        self,
    ) -> None:
        probe = self.probe()
        probe["native_schema_version"] = (
            probe["package_version"]
        )

        with self.assertRaisesRegex(
            acceptance.AcceptanceFailure,
            "not independent",
        ):
            acceptance._verify_probe(
                probe,
                checkout=Path("/checkout"),
            )

    def test_build_requires_one_wheel_and_one_sdist(
        self,
    ) -> None:
        with mock.patch.object(
            acceptance,
            "_run",
        ), mock.patch.object(
            Path,
            "iterdir",
            return_value=iter(
                [
                    Path(
                        "dist/"
                        "gitdrift-0.0.0-py3-none-any.whl"
                    ),
                ]
            ),
        ):
            with self.assertRaisesRegex(
                acceptance.AcceptanceFailure,
                "exactly one wheel and one sdist",
            ):
                acceptance._build(
                    Path("/repository"),
                    Path("/repository/dist"),
                )


if __name__ == "__main__":
    unittest.main()
