#!/usr/bin/env python3
"""Canonical repository validation for Gitdrift."""

from __future__ import annotations

import argparse
import ast
import importlib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


class ValidationFailure(RuntimeError):
    """A mandatory repository validation gate failed."""


@dataclass(frozen=True, slots=True)
class Gate:
    name: str
    action: Callable[[Path], None]


def python_files(root: Path) -> list[Path]:
    return sorted(
        path
        for directory in ("src", "tests", "scripts")
        for path in (root / directory).rglob("*.py")
    )


def compile_python(root: Path) -> None:
    errors: list[str] = []

    for path in python_files(root):
        try:
            compile(
                path.read_bytes(),
                str(path.relative_to(root)),
                "exec",
            )
        except (OSError, SyntaxError) as error:
            errors.append(
                f"{path.relative_to(root)}: {error}"
            )

    if errors:
        raise ValidationFailure(
            "Python compilation failed:\n"
            + "\n".join(errors)
        )


def run_tests(root: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-v",
        ],
        cwd=root,
        check=False,
    )

    if completed.returncode:
        raise ValidationFailure(
            "unit tests failed with exit code "
            f"{completed.returncode}"
        )


def module_name(root: Path, path: Path) -> str:
    return ".".join(
        path.relative_to(
            root / "src"
        ).with_suffix("").parts
    )


def imported_modules(
    tree: ast.AST,
    current: str,
) -> set[str]:
    imports: set[str] = set()

    package = (
        current.rsplit(".", 1)[0]
        if "." in current
        else current
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.split(".")

                if node.level > 1:
                    base = base[
                        : -(node.level - 1)
                    ]

                target = ".".join(
                    [*base, node.module]
                    if node.module
                    else base
                )
            else:
                target = node.module or ""

            imports.add(target)

    return imports


def architectural_imports(root: Path) -> None:
    violations: list[str] = []

    for path in sorted(
        (
            root / "src" / "gitdrift"
        ).rglob("*.py")
    ):
        current = module_name(root, path)

        tree = ast.parse(
            path.read_text(encoding="utf-8"),
            filename=str(path),
        )

        imports = imported_modules(
            tree,
            current,
        )

        if current.startswith("gitdrift.domain"):
            forbidden = {
                name
                for name in imports
                if name in {
                    "argparse",
                    "subprocess",
                }
                or name.startswith(
                    (
                        "gitdrift.adapters",
                        "gitdrift.cli",
                    )
                )
            }

            violations.extend(
                (
                    f"{path.relative_to(root)} "
                    "imports forbidden dependency "
                    f"{name}"
                )
                for name in sorted(forbidden)
            )

        if current.startswith("gitdrift.ports"):
            violations.extend(
                (
                    f"{path.relative_to(root)} "
                    f"imports adapter {name}"
                )
                for name in sorted(imports)
                if name.startswith(
                    "gitdrift.adapters"
                )
            )

    if violations:
        raise ValidationFailure(
            "Architecture violations:\n"
            + "\n".join(violations)
        )


def exported_names(path: Path) -> set[str]:
    tree = ast.parse(
        path.read_text(encoding="utf-8"),
        filename=str(path),
    )

    for node in tree.body:
        if not isinstance(
            node,
            ast.Assign,
        ):
            continue

        if not any(
            isinstance(target, ast.Name)
            and target.id == "__all__"
            for target in node.targets
        ):
            continue

        try:
            value = ast.literal_eval(node.value)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValidationFailure(
                f"{path}: __all__ must be literal"
            ) from error

        if (
            not isinstance(
                value,
                (list, tuple),
            )
            or not all(
                isinstance(item, str)
                for item in value
            )
        ):
            raise ValidationFailure(
                f"{path}: __all__ must "
                "contain only strings"
            )

        return set(value)

    raise ValidationFailure(
        f"{path}: missing explicit __all__"
    )


def _fresh_import(
    root: Path,
    name: str,
):
    for loaded in list(sys.modules):
        if (
            loaded == "gitdrift"
            or loaded.startswith("gitdrift.")
        ):
            del sys.modules[loaded]

    sys.path.insert(
        0,
        str(root / "src"),
    )

    try:
        return importlib.import_module(name)
    finally:
        sys.path.pop(0)


def public_api(root: Path) -> None:
    modules = (
        (
            "gitdrift",
            Path("src/gitdrift/__init__.py"),
        ),
        (
            "gitdrift.domain",
            Path(
                "src/gitdrift/domain/__init__.py"
            ),
        ),
    )

    for name, relative in modules:
        expected = exported_names(
            root / relative
        )
        module = _fresh_import(
            root,
            name,
        )

        missing = sorted(
            item
            for item in expected
            if not hasattr(module, item)
        )

        if missing:
            raise ValidationFailure(
                f"{relative}: unbound exports: "
                + ", ".join(missing)
            )


def compatibility_aliases(root: Path) -> None:
    domain = _fresh_import(
        root,
        "gitdrift.domain",
    )

    records = importlib.import_module(
        "gitdrift.domain.records"
    )

    failures = sorted(
        name
        for name in records.__all__
        if (
            not hasattr(domain, name)
            or getattr(records, name)
            is not getattr(domain, name)
        )
    )

    if failures:
        raise ValidationFailure(
            "domain.records compatibility drift: "
            + ", ".join(failures)
        )


LINK = re.compile(
    r"(?<!!)\[[^\]]+\]\(([^)]+)\)"
)


def documentation_links(root: Path) -> None:
    failures: list[str] = []
    repository_root = root.resolve()

    for path in sorted(
        (root / "docs").rglob("*.md")
    ):
        text = path.read_text(
            encoding="utf-8"
        )

        for target in LINK.findall(text):
            target = (
                target.strip()
                .split(maxsplit=1)[0]
                .strip("<>")
            )

            if (
                not target
                or target.startswith(
                    (
                        "#",
                        "http://",
                        "https://",
                        "mailto:",
                    )
                )
            ):
                continue

            file_target = target.split(
                "#",
                1,
            )[0]

            if not file_target:
                continue

            resolved = (
                path.parent / file_target
            ).resolve()

            try:
                resolved.relative_to(
                    repository_root
                )
            except ValueError:
                failures.append(
                    f"{path.relative_to(root)}: "
                    "link escapes repository: "
                    f"{target}"
                )
            else:
                if not resolved.is_file():
                    failures.append(
                        f"{path.relative_to(root)}: "
                        "missing file target: "
                        f"{target}"
                    )

    if failures:
        raise ValidationFailure(
            "Documentation link failures:\n"
            + "\n".join(failures)
        )


def git_diff_check(root: Path) -> None:
    completed = subprocess.run(
        [
            "git",
            "diff",
            "--check",
            "HEAD",
        ],
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
    )

    if completed.returncode:
        raise ValidationFailure(
            completed.stdout
            + completed.stderr
        )


def gates() -> tuple[Gate, ...]:
    return (
        Gate(
            "python-compilation",
            compile_python,
        ),
        Gate(
            "unit-tests",
            run_tests,
        ),
        Gate(
            "architectural-imports",
            architectural_imports,
        ),
        Gate(
            "public-api",
            public_api,
        ),
        Gate(
            "compatibility-aliases",
            compatibility_aliases,
        ),
        Gate(
            "documentation-links",
            documentation_links,
        ),
        Gate(
            "git-diff-check",
            git_diff_check,
        ),
    )


def validate(
    root: Path,
    selected: set[str] | None = None,
) -> int:
    failures = 0

    for gate in gates():
        if (
            selected is not None
            and gate.name not in selected
        ):
            continue

        try:
            gate.action(root)
        except Exception as error:
            failures += 1

            print(
                f"FAIL {gate.name}: {error}",
                file=sys.stderr,
            )
        else:
            print(
                f"PASS {gate.name}"
            )

    return 1 if failures else 0


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root",
        type=Path,
        default=Path(
            __file__
        ).resolve().parents[2],
    )

    parser.add_argument(
        "--gate",
        action="append",
        choices=[
            gate.name
            for gate in gates()
        ],
    )

    arguments = parser.parse_args(argv)

    selected = (
        set(arguments.gate)
        if arguments.gate
        else None
    )

    return validate(
        arguments.root.resolve(),
        selected,
    )


if __name__ == "__main__":
    raise SystemExit(main())
