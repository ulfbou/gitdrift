#!/usr/bin/env python3
"""Canonical repository validation for Gitdrift."""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.validation.gates import (
        architectural_imports, changed_file_coverage, compatibility_aliases,
        compile_python, documentation_links, gates, git_diff_check,
        public_api, run_tests,
    )
    from scripts.validation.model import ChangedPath, Gate, ValidationFailure, ValidationScope
    from scripts.validation.orchestration import validate
    from scripts.validation.scope import changed_paths
else:
    from .gates import (
        architectural_imports, changed_file_coverage, compatibility_aliases,
        compile_python, documentation_links, gates, git_diff_check,
        public_api, run_tests,
    )
    from .model import ChangedPath, Gate, ValidationFailure, ValidationScope
    from .orchestration import validate
    from .scope import changed_paths

__all__ = [
    "ChangedPath", "Gate", "ValidationFailure", "ValidationScope",
    "architectural_imports", "changed_file_coverage", "changed_paths",
    "compatibility_aliases", "compile_python", "documentation_links",
    "gates", "git_diff_check", "public_api", "run_tests", "validate",
]

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--gate", action="append", choices=[gate.name for gate in gates()])
    parser.add_argument("--base-ref", help="validate every file changed from BASE_REF through HEAD")
    parser.add_argument("--include-staged", action="store_true")
    parser.add_argument("--include-unstaged", action="store_true", help="include unstaged and untracked files")
    arguments = parser.parse_args(argv)
    root = arguments.root.resolve()
    scope = changed_paths(
        root, base_ref=arguments.base_ref,
        include_staged=arguments.include_staged,
        include_unstaged=arguments.include_unstaged,
    )
    return validate(root, set(arguments.gate) if arguments.gate else None, scope)

if __name__ == "__main__":
    raise SystemExit(main())
