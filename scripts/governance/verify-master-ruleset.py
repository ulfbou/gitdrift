#!/usr/bin/env python3
"""Independently verify Gitdrift's hosted master integration boundary."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

RULESET_NAME = "gitdrift-master-integration"
TARGET_REF = "refs/heads/master"
DEFAULT_BRANCH = "master"
CANONICAL_CHECK_SOURCE = "github-actions"
CONTROLLED_RULE_TYPES = frozenset(
    {
        "deletion",
        "non_fast_forward",
        "pull_request",
        "required_status_checks",
        "update",
    }
)


@dataclass(frozen=True, slots=True)
class Diagnostic:
    requirement: str
    outcome: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {
            "requirement": self.requirement,
            "outcome": self.outcome,
            "detail": self.detail,
        }


class VerificationFailure(RuntimeError):
    """Hosted governance verification could not be completed safely."""


def _gh_json(
    endpoint: str,
    *,
    method: str = "GET",
) -> Any:
    completed = subprocess.run(
        [
            "gh",
            "api",
            "--method",
            method,
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            "X-GitHub-Api-Version: 2022-11-28",
            endpoint,
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if completed.returncode:
        raise VerificationFailure(
            f"gh api failed for {endpoint}: {completed.stderr.strip()}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise VerificationFailure(
            f"gh api returned invalid JSON for {endpoint}"
        ) from error


def _repository() -> str:
    completed = subprocess.run(
        [
            "gh",
            "repo",
            "view",
            "--json",
            "nameWithOwner",
            "--jq",
            ".nameWithOwner",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if completed.returncode:
        raise VerificationFailure(
            f"cannot resolve repository: {completed.stderr.strip()}"
        )
    repository = completed.stdout.strip()
    if repository.count("/") != 1:
        raise VerificationFailure("resolved repository identity is invalid")
    return repository


def _rule_by_type(
    rules: Sequence[Mapping[str, Any]],
    rule_type: str,
) -> list[Mapping[str, Any]]:
    return [
        rule
        for rule in rules
        if rule.get("type") == rule_type
    ]


def _condition_values(
    ruleset: Mapping[str, Any],
    name: str,
) -> tuple[str, ...]:
    conditions = ruleset.get("conditions")
    if not isinstance(conditions, Mapping):
        return ()
    ref_name = conditions.get("ref_name")
    if not isinstance(ref_name, Mapping):
        return ()
    values = ref_name.get(name)
    if not isinstance(values, list):
        return ()
    return tuple(
        value for value in values if isinstance(value, str)
    )


def _required_checks(
    rule: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    parameters = rule.get("parameters")
    if not isinstance(parameters, Mapping):
        return []
    checks = parameters.get("required_status_checks")
    if not isinstance(checks, list):
        return []
    return [
        check
        for check in checks
        if isinstance(check, Mapping)
    ]


def _strict_required_checks(
    rule: Mapping[str, Any],
) -> bool:
    parameters = rule.get("parameters")
    return (
        isinstance(parameters, Mapping)
        and parameters.get("strict_required_status_checks_policy")
        is True
    )


def _observed_identity(
    characterization: Mapping[str, Any],
) -> tuple[str | None, int | None, str | None, str | None]:
    candidates = characterization.get("canonical_check_candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        return None, None, None, None

    candidate = candidates[0]
    if not isinstance(candidate, Mapping):
        return None, None, None, None

    name = candidate.get("name")
    observations = candidate.get("observations")
    if not isinstance(name, str) or not isinstance(observations, list):
        return None, None, None, None

    identities: set[tuple[int, str]] = set()
    commits: set[str] = set()

    for observation in observations:
        if not isinstance(observation, Mapping):
            continue
        sha = observation.get("sha")
        if isinstance(sha, str):
            commits.add(sha)

        check = observation.get("check")
        if not isinstance(check, Mapping):
            continue
        if check.get("name") != name:
            continue

        app = check.get("app")
        if not isinstance(app, Mapping):
            continue
        app_id = app.get("id")
        app_slug = app.get("slug")
        if isinstance(app_id, int) and isinstance(app_slug, str):
            identities.add((app_id, app_slug))

    if len(identities) != 1 or not commits:
        return None, None, None, None

    app_id, app_slug = next(iter(identities))
    inspected_commit = sorted(commits)[-1]
    return name, app_id, app_slug, inspected_commit


def verify_snapshot(
    snapshot: Mapping[str, Any],
    characterization: Mapping[str, Any],
) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []

    def record(
        requirement: str,
        passed: bool,
        detail: str,
        *,
        unresolved: bool = False,
    ) -> None:
        diagnostics.append(
            Diagnostic(
                requirement,
                "unresolved" if unresolved else (
                    "pass" if passed else "fail"
                ),
                detail,
            )
        )

    repository = snapshot.get("repository")
    default_branch = snapshot.get("default_branch")
    rulesets = snapshot.get("repository_rulesets")
    effective_rules = snapshot.get("effective_rules_for_master")
    conflicts = characterization.get(
        "same_name_commit_status_conflicts"
    )

    record(
        "repository-resolved",
        isinstance(repository, str) and repository.count("/") == 1,
        str(repository),
    )
    record(
        "default-branch-master",
        default_branch == DEFAULT_BRANCH,
        str(default_branch),
    )

    context, integration_id, source, inspected_commit = (
        _observed_identity(characterization)
    )

    identity_resolved = (
        context is not None
        and integration_id is not None
        and source == CANONICAL_CHECK_SOURCE
        and inspected_commit is not None
    )
    record(
        "canonical-check-identity-resolved",
        identity_resolved,
        (
            f"context={context!r}, integration_id={integration_id!r}, "
            f"source={source!r}, inspected_commit={inspected_commit!r}"
        ),
        unresolved=not identity_resolved,
    )

    no_conflicts = isinstance(conflicts, list) and not conflicts
    record(
        "conflicting-same-name-status-absent",
        no_conflicts,
        f"conflicts={len(conflicts) if isinstance(conflicts, list) else 'unknown'}",
        unresolved=not isinstance(conflicts, list),
    )

    if not isinstance(rulesets, list):
        record(
            "repository-rulesets-retrieved",
            False,
            "repository rulesets are unavailable",
            unresolved=True,
        )
        return tuple(diagnostics)

    record(
        "repository-rulesets-retrieved",
        True,
        f"count={len(rulesets)}",
    )

    named = [
        ruleset
        for ruleset in rulesets
        if isinstance(ruleset, Mapping)
        and ruleset.get("name") == RULESET_NAME
    ]

    record(
        "named-ruleset-exactly-once",
        len(named) == 1,
        f"count={len(named)}",
    )

    if len(named) != 1:
        return tuple(diagnostics)

    ruleset = named[0]
    ruleset_id = ruleset.get("id")
    rules = ruleset.get("rules")
    bypass_actors = ruleset.get("bypass_actors")
    includes = _condition_values(ruleset, "include")
    excludes = _condition_values(ruleset, "exclude")

    record(
        "ruleset-target-branches",
        ruleset.get("target") == "branch",
        f"target={ruleset.get('target')!r}",
    )
    record(
        "ruleset-enforcement-active",
        ruleset.get("enforcement") == "active",
        f"enforcement={ruleset.get('enforcement')!r}",
    )
    record(
        "ruleset-target-exact-master",
        includes == (TARGET_REF,),
        f"include={list(includes)!r}",
    )
    record(
        "ruleset-excludes-none",
        excludes == (),
        f"exclude={list(excludes)!r}",
    )
    record(
        "ruleset-bypass-actors-empty",
        bypass_actors == [],
        f"bypass_actors={bypass_actors!r}",
    )

    if not isinstance(rules, list):
        record(
            "ruleset-rules-retrieved",
            False,
            "rules are unavailable",
            unresolved=True,
        )
        return tuple(diagnostics)

    typed_rules = [
        rule for rule in rules if isinstance(rule, Mapping)
    ]
    record(
        "ruleset-rules-retrieved",
        True,
        f"count={len(typed_rules)}",
    )

    deletion = _rule_by_type(typed_rules, "deletion")
    non_fast_forward = _rule_by_type(
        typed_rules,
        "non_fast_forward",
    )
    pull_request = _rule_by_type(typed_rules, "pull_request")
    status_checks = _rule_by_type(
        typed_rules,
        "required_status_checks",
    )
    update = _rule_by_type(typed_rules, "update")

    record(
        "deletion-prohibited",
        len(deletion) == 1,
        f"rules={len(deletion)}",
    )
    record(
        "non-fast-forward-prohibited",
        len(non_fast_forward) == 1,
        f"rules={len(non_fast_forward)}",
    )
    record(
        "pull-request-required",
        len(pull_request) == 1,
        f"rules={len(pull_request)}",
    )
    record(
        "update-restriction-absent",
        len(update) == 0,
        f"rules={len(update)}",
    )
    record(
        "required-status-check-rule-exactly-once",
        len(status_checks) == 1,
        f"rules={len(status_checks)}",
    )

    if len(status_checks) == 1 and identity_resolved:
        required = _required_checks(status_checks[0])
        exact = [
            check
            for check in required
            if check.get("context") == context
            and check.get("integration_id") == integration_id
        ]
        record(
            "canonical-check-required-exactly-once",
            len(exact) == 1 and len(required) == 1,
            (
                f"required={required!r}, expected_context={context!r}, "
                f"expected_integration_id={integration_id!r}"
            ),
        )
        record(
            "strict-required-check-policy-enabled",
            _strict_required_checks(status_checks[0]),
            (
                "strict_required_status_checks_policy="
                f"{_strict_required_checks(status_checks[0])!r}"
            ),
        )

    if not isinstance(effective_rules, list):
        record(
            "effective-rules-retrieved",
            False,
            "effective rules are unavailable",
            unresolved=True,
        )
        return tuple(diagnostics)

    typed_effective = [
        rule
        for rule in effective_rules
        if isinstance(rule, Mapping)
    ]
    record(
        "effective-rules-retrieved",
        True,
        f"count={len(typed_effective)}",
    )

    expected_effective_types = {
        "deletion",
        "non_fast_forward",
        "pull_request",
        "required_status_checks",
    }
    named_effective = [
        rule
        for rule in typed_effective
        if rule.get("ruleset_id") == ruleset_id
    ]
    named_effective_types = {
        rule.get("type")
        for rule in named_effective
        if isinstance(rule.get("type"), str)
    }

    record(
        "named-ruleset-effective-on-master",
        expected_effective_types <= named_effective_types,
        (
            f"ruleset_id={ruleset_id!r}, "
            f"effective_types={sorted(named_effective_types)!r}"
        ),
    )

    overlapping = [
        rule
        for rule in typed_effective
        if rule.get("ruleset_id") != ruleset_id
        and rule.get("type") in CONTROLLED_RULE_TYPES
    ]
    record(
        "no-overlapping-effective-rule-ambiguity",
        not overlapping,
        f"overlapping_rules={overlapping!r}",
    )

    return tuple(diagnostics)


def collect_live_snapshot(repository: str) -> dict[str, Any]:
    repository_record = _gh_json(f"/repos/{repository}")
    ruleset_summaries = _gh_json(
        f"/repos/{repository}/rulesets?includes_parents=true"
    )
    if not isinstance(ruleset_summaries, list):
        raise VerificationFailure(
            "repository ruleset list has unexpected shape"
        )

    repository_rulesets: list[Mapping[str, Any]] = []
    for summary in ruleset_summaries:
        if not isinstance(summary, Mapping):
            continue
        if summary.get("source_type") not in (
            None,
            "Repository",
        ):
            continue
        ruleset_id = summary.get("id")
        if not isinstance(ruleset_id, int):
            raise VerificationFailure(
                "ruleset summary lacks integer id"
            )
        detail = _gh_json(
            f"/repos/{repository}/rulesets/{ruleset_id}"
        )
        if not isinstance(detail, Mapping):
            raise VerificationFailure(
                f"ruleset {ruleset_id} has unexpected shape"
            )
        repository_rulesets.append(detail)

    effective_rules = _gh_json(
        f"/repos/{repository}/rules/branches/master?per_page=100"
    )
    if not isinstance(effective_rules, list):
        raise VerificationFailure(
            "effective rules response has unexpected shape"
        )

    return {
        "repository": repository,
        "default_branch": repository_record.get(
            "default_branch"
        ),
        "repository_rulesets": repository_rulesets,
        "effective_rules_for_master": effective_rules,
    }


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise VerificationFailure(
            f"cannot read JSON file {path}: {error}"
        ) from error
    except json.JSONDecodeError as error:
        raise VerificationFailure(
            f"invalid JSON file {path}: {error}"
        ) from error
    if not isinstance(document, Mapping):
        raise VerificationFailure(
            f"JSON root must be an object: {path}"
        )
    return document


def _parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Verify the effective hosted integration boundary for master."
        )
    )
    parser.add_argument(
        "--characterization",
        type=Path,
        required=True,
        help="Phase 8.1 hosted-boundary evidence JSON",
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        help=(
            "Optional remote-state fixture. When omitted, retrieve the "
            "current hosted state through gh api."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional destination for complete verification evidence",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)

    try:
        characterization = _load_json(arguments.characterization)

        if arguments.snapshot is None:
            repository = _repository()
            snapshot: Mapping[str, Any] = collect_live_snapshot(
                repository
            )
            source = "live"
        else:
            snapshot = _load_json(arguments.snapshot)
            source = str(arguments.snapshot)

        diagnostics = verify_snapshot(
            snapshot,
            characterization,
        )

        context, integration_id, check_source, inspected_commit = (
            _observed_identity(characterization)
        )

        result = {
            "schema": "gitdrift-master-ruleset-verification-v1",
            "source": source,
            "repository": snapshot.get("repository"),
            "default_branch": snapshot.get("default_branch"),
            "ruleset_name": RULESET_NAME,
            "target_ref": TARGET_REF,
            "required_check": {
                "context": context,
                "integration_id": integration_id,
                "source": check_source,
                "inspected_commit": inspected_commit,
            },
            "repository_rulesets": snapshot.get(
                "repository_rulesets"
            ),
            "effective_rules_for_master": snapshot.get(
                "effective_rules_for_master"
            ),
            "diagnostics": [
                diagnostic.to_dict()
                for diagnostic in diagnostics
            ],
        }

        serialized = (
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n"
        )

        if arguments.output is not None:
            arguments.output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            arguments.output.write_text(
                serialized,
                encoding="utf-8",
                newline="\n",
            )

        print(serialized, end="")

        blocking = [
            diagnostic
            for diagnostic in diagnostics
            if diagnostic.outcome != "pass"
        ]
        return 1 if blocking else 0

    except VerificationFailure as error:
        print(
            json.dumps(
                {
                    "schema": (
                        "gitdrift-master-ruleset-verification-v1"
                    ),
                    "diagnostics": [
                        {
                            "requirement": (
                                "verification-execution"
                            ),
                            "outcome": "unresolved",
                            "detail": str(error),
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
