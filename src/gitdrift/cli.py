"""Thin process adapter for implemented Gitdrift operations."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .discovery import discover_capabilities


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gitdrift")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("discover", help="emit active capabilities as JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "discover":
        payload = discover_capabilities().to_dict()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    raise AssertionError(f"unhandled command: {args.command}")
