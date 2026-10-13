from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any

SCRIPT = (
    Path(__file__).parents[1]
    / "scripts"
    / "governance"
    / "verify-master-ruleset.py"
)

SPEC = importlib.util.spec_from_file_location(
    "gitdrift_governance_verifier",
    SCRIPT,
)
assert SPEC
assert SPEC.loader

verifier = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verifier
SPEC.loader.exec_module(verifier)


def characterization() -> dict[str, Any]:
    return {
        "canonical_check_candidates": [
            {
                "name": "validate",
                "observations": [
                    {
                        "sha": (
                            "c6ff1e66a113c28341c015df338528a5d81ec88b"
                        ),
                        "check": {
                            "name": "validate",
                            "app": {
                                "id": 15368,
                                "slug": "github-actions",
                            },
                        },
                    }
                ],
            }
        ],
        "same_name_commit_status_conflicts": [],
    }


def valid_snapshot() -> dict[str, Any]:
    ruleset_id = 8001
    rules = [
        {"type": "deletion"},
        {"type": "non_fast_forward"},
        {
            "type": "pull_request",
            "parameters": {
                "required_approving_review_count": 0,
            },
        },
        {
            "type": "required_status_checks",
            "parameters": {
                "required_status_checks": [
                    {
                        "context": "validate",
                        "integration_id": 15368,
                    }
                ],
                "strict_required_status_checks_policy": True,
                "do_not_enforce_on_create": False,
            },
        },
    ]

    effective = [
        {
            **copy.deepcopy(rule),
            "ruleset_id": ruleset_id,
            "ruleset_source_type": "Repository",
            "ruleset_source": "ulfbou/gitdrift",
        }
        for rule in rules
    ]

    return {
        "repository": "ulfbou/gitdrift",
        "default_branch": "master",
        "repository_rulesets": [
            {
                "id": ruleset_id,
                "name": "gitdrift-master-integration",
                "target": "branch",
                "enforcement": "active",
                "bypass_actors": [],
                "conditions": {
                    "ref_name": {
                        "include": ["refs/heads/master"],
                        "exclude": [],
                    }
                },
                "rules": rules,
            }
        ],
        "effective_rules_for_master": effective,
    }


def outcomes(
    snapshot: dict[str, Any],
    evidence: dict[str, Any] | None = None,
) -> dict[str, str]:
    diagnostics = verifier.verify_snapshot(
        snapshot,
        evidence or characterization(),
    )
    return {
        diagnostic.requirement: diagnostic.outcome
        for diagnostic in diagnostics
    }


class GovernanceRulesetVerifierTests(unittest.TestCase):
    def test_valid_ruleset_passes_every_requirement(self) -> None:
        result = outcomes(valid_snapshot())
        self.assertTrue(result)
        self.assertEqual(set(result.values()), {"pass"})

    def test_absent_ruleset_fails(self) -> None:
        snapshot = valid_snapshot()
        snapshot["repository_rulesets"] = []
        snapshot["effective_rules_for_master"] = []

        result = outcomes(snapshot)

        self.assertEqual(
            result["named-ruleset-exactly-once"],
            "fail",
        )

    def test_duplicate_named_ruleset_fails(self) -> None:
        snapshot = valid_snapshot()
        duplicate = copy.deepcopy(
            snapshot["repository_rulesets"][0]
        )
        duplicate["id"] = 8002
        snapshot["repository_rulesets"].append(duplicate)

        result = outcomes(snapshot)

        self.assertEqual(
            result["named-ruleset-exactly-once"],
            "fail",
        )

    def test_inactive_ruleset_fails(self) -> None:
        snapshot = valid_snapshot()
        snapshot["repository_rulesets"][0]["enforcement"] = (
            "evaluate"
        )

        result = outcomes(snapshot)

        self.assertEqual(
            result["ruleset-enforcement-active"],
            "fail",
        )

    def test_broad_target_fails(self) -> None:
        snapshot = valid_snapshot()
        conditions = snapshot["repository_rulesets"][0][
            "conditions"
        ]
        conditions["ref_name"]["include"] = ["~DEFAULT_BRANCH"]

        result = outcomes(snapshot)

        self.assertEqual(
            result["ruleset-target-exact-master"],
            "fail",
        )

    def test_master_exclusion_fails(self) -> None:
        snapshot = valid_snapshot()
        conditions = snapshot["repository_rulesets"][0][
            "conditions"
        ]
        conditions["ref_name"]["exclude"] = [
            "refs/heads/master"
        ]

        result = outcomes(snapshot)

        self.assertEqual(
            result["ruleset-excludes-none"],
            "fail",
        )

    def test_bypass_actor_fails(self) -> None:
        snapshot = valid_snapshot()
        snapshot["repository_rulesets"][0]["bypass_actors"] = [
            {
                "actor_id": 1,
                "actor_type": "RepositoryRole",
                "bypass_mode": "always",
            }
        ]

        result = outcomes(snapshot)

        self.assertEqual(
            result["ruleset-bypass-actors-empty"],
            "fail",
        )

    def test_missing_pull_request_rule_fails(self) -> None:
        snapshot = valid_snapshot()
        rules = snapshot["repository_rulesets"][0]["rules"]
        snapshot["repository_rulesets"][0]["rules"] = [
            rule
            for rule in rules
            if rule["type"] != "pull_request"
        ]

        result = outcomes(snapshot)

        self.assertEqual(
            result["pull-request-required"],
            "fail",
        )

    def test_update_restriction_fails(self) -> None:
        snapshot = valid_snapshot()
        snapshot["repository_rulesets"][0]["rules"].append(
            {"type": "update"}
        )

        result = outcomes(snapshot)

        self.assertEqual(
            result["update-restriction-absent"],
            "fail",
        )

    def test_missing_deletion_rule_fails(self) -> None:
        snapshot = valid_snapshot()
        rules = snapshot["repository_rulesets"][0]["rules"]
        snapshot["repository_rulesets"][0]["rules"] = [
            rule
            for rule in rules
            if rule["type"] != "deletion"
        ]

        result = outcomes(snapshot)

        self.assertEqual(
            result["deletion-prohibited"],
            "fail",
        )

    def test_missing_non_fast_forward_rule_fails(self) -> None:
        snapshot = valid_snapshot()
        rules = snapshot["repository_rulesets"][0]["rules"]
        snapshot["repository_rulesets"][0]["rules"] = [
            rule
            for rule in rules
            if rule["type"] != "non_fast_forward"
        ]

        result = outcomes(snapshot)

        self.assertEqual(
            result["non-fast-forward-prohibited"],
            "fail",
        )

    def test_wrong_check_context_fails(self) -> None:
        snapshot = valid_snapshot()
        status_rule = snapshot["repository_rulesets"][0][
            "rules"
        ][3]
        status_rule["parameters"]["required_status_checks"][0][
            "context"
        ] = "validation/validate"

        result = outcomes(snapshot)

        self.assertEqual(
            result["canonical-check-required-exactly-once"],
            "fail",
        )

    def test_missing_integration_binding_fails(self) -> None:
        snapshot = valid_snapshot()
        status_rule = snapshot["repository_rulesets"][0][
            "rules"
        ][3]
        status_rule["parameters"]["required_status_checks"][0].pop(
            "integration_id"
        )

        result = outcomes(snapshot)

        self.assertEqual(
            result["canonical-check-required-exactly-once"],
            "fail",
        )

    def test_non_strict_check_policy_fails(self) -> None:
        snapshot = valid_snapshot()
        status_rule = snapshot["repository_rulesets"][0][
            "rules"
        ][3]
        status_rule["parameters"][
            "strict_required_status_checks_policy"
        ] = False

        result = outcomes(snapshot)

        self.assertEqual(
            result["strict-required-check-policy-enabled"],
            "fail",
        )

    def test_conflicting_commit_status_fails(self) -> None:
        evidence = characterization()
        evidence["same_name_commit_status_conflicts"] = [
            {
                "name": "validate",
                "sha": "abc",
            }
        ]

        result = outcomes(valid_snapshot(), evidence)

        self.assertEqual(
            result["conflicting-same-name-status-absent"],
            "fail",
        )

    def test_ambiguous_check_identity_is_unresolved(self) -> None:
        evidence = characterization()
        evidence["canonical_check_candidates"][0][
            "observations"
        ].append(
            {
                "sha": "def",
                "check": {
                    "name": "validate",
                    "app": {
                        "id": 99999,
                        "slug": "other-app",
                    },
                },
            }
        )

        result = outcomes(valid_snapshot(), evidence)

        self.assertEqual(
            result["canonical-check-identity-resolved"],
            "unresolved",
        )

    def test_overlapping_controlled_rule_fails(self) -> None:
        snapshot = valid_snapshot()
        snapshot["effective_rules_for_master"].append(
            {
                "type": "required_status_checks",
                "ruleset_id": 9001,
                "ruleset_source_type": "Organization",
                "ruleset_source": "example",
                "parameters": {
                    "required_status_checks": [
                        {
                            "context": "another-check",
                            "integration_id": 15368,
                        }
                    ],
                    "strict_required_status_checks_policy": False,
                },
            }
        )

        result = outcomes(snapshot)

        self.assertEqual(
            result[
                "no-overlapping-effective-rule-ambiguity"
            ],
            "fail",
        )


if __name__ == "__main__":
    unittest.main()
