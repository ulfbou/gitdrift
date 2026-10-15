"""Thin process adapter for implemented Gitdrift operations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections.abc import Sequence

from .discovery import discover_capabilities
from .profiles import StateAwarenessProfile, StateAwarenessRequest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gitdrift")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser(
        "discover",
        help="emit active capabilities as JSON",
    )
    state = subcommands.add_parser(
        "state-awareness",
        help="emit one canonical state-awareness investigation",
    )
    state.add_argument(
        "--repository",
        type=Path,
        required=True,
        help="explicit repository root",
    )
    state.add_argument(
        "--without-upstream",
        action="store_true",
        help="do not request the configured upstream endpoint",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "discover":
        payload = discover_capabilities().to_dict()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.command == "state-awareness":
        result = StateAwarenessProfile().run(
            StateAwarenessRequest(
                repository=args.repository,
                include_upstream=not args.without_upstream,
            )
        )
        sys.stdout.buffer.write(result.artifact.payload)
        return 0

    raise AssertionError(f"unhandled command: {args.command}")
