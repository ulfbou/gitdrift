"""Responsibility-owned canonical validation gates."""
from __future__ import annotations
import ast
import importlib
import os
import re
import subprocess
import sys
from pathlib import Path
from .model import Gate, ValidationFailure, ValidationScope


def python_files(root: Path, scope: ValidationScope) -> list[Path]:
    return sorted(
        path for directory in ("src", "tests", "scripts")
        for path in (root / directory).rglob("*.py")
        if scope.includes(path.relative_to(root))
    )

def _disposition(root: Path, relative: Path, scope: ValidationScope) -> str:
    change = scope.change_for(relative)
    if change is not None and change.status == "D":
        return "deleted"
    path = root / relative
    if path.is_symlink():
        return "symlink"
    if not path.exists():
        return "unavailable"
    if path.is_dir():
        return "directory"
    if not path.is_file():
        return "non-regular"
    data = path.read_bytes()
    if b"\0" in data:
        return "binary"
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return "undecodable"
    return "text"

def changed_file_coverage(root: Path, scope: ValidationScope = ValidationScope()) -> None:
    if scope.changes is None:
        return
    failures: list[str] = []
    print(f"INFO changed-file-scope count={len(scope.changes)}")
    for change in scope.changes:
        portable = change.path.as_posix()
        disposition = _disposition(root, change.path, scope)
        print(
            f"INFO changed-file status={change.status} disposition={disposition} "
            f"source={change.source} path={portable}"
        )
        if portable.endswith((".dx", ".dx.txt")) and change.status != "D":
            failures.append(
                "DX carrier is inside the analyzed repository; "
                f"write carriers to $CARRIER_SOURCE_DIR instead: {portable}"
            )
        elif disposition == "unavailable":
            failures.append(f"changed path could not be dispositioned: {portable}")
    if failures:
        raise ValidationFailure("Changed-file coverage failed:\n" + "\n".join(failures))

def compile_python(root: Path, scope: ValidationScope = ValidationScope()) -> None:
    errors: list[str] = []
    for path in python_files(root, scope):
        try:
            compile(path.read_bytes(), str(path.relative_to(root)), "exec")
        except (OSError, SyntaxError) as error:
            errors.append(f"{path.relative_to(root)}: {error}")
    if errors:
        raise ValidationFailure("Python compilation failed:\n" + "\n".join(errors))

def run_tests(root: Path, scope: ValidationScope = ValidationScope()) -> None:
    environment = os.environ.copy()
    source_path = str(root / "src")
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = source_path if not existing else os.pathsep.join((source_path, existing))
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=root, env=environment, check=False,
    )
    if completed.returncode:
        raise ValidationFailure(f"unit tests failed with exit code {completed.returncode}")

def module_name(root: Path, path: Path) -> str:
    return ".".join(path.relative_to(root / "src").with_suffix("").parts)

def imported_modules(tree: ast.AST, current: str) -> set[str]:
    imports: set[str] = set()
    package = current.rsplit(".", 1)[0] if "." in current else current
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.split(".")
                if node.level > 1:
                    base = base[: -(node.level - 1)]
                target = ".".join([*base, node.module] if node.module else base)
            else:
                target = node.module or ""
            imports.add(target)
    return imports

def architectural_imports(root: Path, scope: ValidationScope = ValidationScope()) -> None:
    violations: list[str] = []
    for path in sorted((root / "src" / "gitdrift").rglob("*.py")):
        if not scope.includes(path.relative_to(root)):
            continue
        current = module_name(root, path)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = imported_modules(tree, current)
        if current.startswith("gitdrift.domain"):
            forbidden = {name for name in imports if name in {"argparse", "subprocess"} or name.startswith(("gitdrift.adapters", "gitdrift.cli"))}
            violations.extend(f"{path.relative_to(root)} imports forbidden dependency {name}" for name in sorted(forbidden))
        if current.startswith("gitdrift.ports"):
            violations.extend(f"{path.relative_to(root)} imports adapter {name}" for name in sorted(imports) if name.startswith("gitdrift.adapters"))
    if violations:
        raise ValidationFailure("Architecture violations:\n" + "\n".join(violations))

def exported_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except (TypeError, ValueError) as error:
                raise ValidationFailure(f"{path}: __all__ must be literal") from error
            if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) for item in value):
                raise ValidationFailure(f"{path}: __all__ must contain only strings")
            return set(value)
    raise ValidationFailure(f"{path}: missing explicit __all__")

def _fresh_import(root: Path, name: str):
    for loaded in list(sys.modules):
        if loaded == "gitdrift" or loaded.startswith("gitdrift."):
            del sys.modules[loaded]
    sys.path.insert(0, str(root / "src"))
    try:
        return importlib.import_module(name)
    finally:
        sys.path.pop(0)

def public_api(root: Path, scope: ValidationScope = ValidationScope()) -> None:
    for name, relative in (("gitdrift", Path("src/gitdrift/__init__.py")), ("gitdrift.domain", Path("src/gitdrift/domain/__init__.py"))):
        expected = exported_names(root / relative)
        module = _fresh_import(root, name)
        missing = sorted(item for item in expected if not hasattr(module, item))
        if missing:
            raise ValidationFailure(f"{relative}: unbound exports: " + ", ".join(missing))

def compatibility_aliases(root: Path, scope: ValidationScope = ValidationScope()) -> None:
    domain = _fresh_import(root, "gitdrift.domain")
    records = importlib.import_module("gitdrift.domain.records")
    failures = sorted(name for name in records.__all__ if not hasattr(domain, name) or getattr(records, name) is not getattr(domain, name))
    if failures:
        raise ValidationFailure("domain.records compatibility drift: " + ", ".join(failures))

LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
def documentation_links(root: Path, scope: ValidationScope = ValidationScope()) -> None:
    failures: list[str] = []
    repository_root = root.resolve()
    for path in sorted((root / "docs").rglob("*.md")):
        if not scope.includes(path.relative_to(root)):
            continue
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            target = target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_target = target.split("#", 1)[0]
            if not file_target:
                continue
            resolved = (path.parent / file_target).resolve()
            try:
                resolved.relative_to(repository_root)
            except ValueError:
                failures.append(f"{path.relative_to(root)}: link escapes repository: {target}")
            else:
                if not resolved.is_file():
                    failures.append(f"{path.relative_to(root)}: missing file target: {target}")
    if failures:
        raise ValidationFailure("Documentation link failures:\n" + "\n".join(failures))

def git_diff_check(root: Path, scope: ValidationScope = ValidationScope()) -> None:
    commands: list[list[str]] = []
    if scope.paths is None:
        commands.append(["git", "diff", "--check", "HEAD"])
    else:
        paths = [path.as_posix() for path in sorted(scope.paths)]
        if scope.base_ref is not None:
            commands.append(["git", "diff", "--check", f"{scope.base_ref}...HEAD", "--", *paths])
        if scope.include_staged:
            commands.append(["git", "diff", "--cached", "--check", "--", *paths])
        if scope.include_unstaged:
            commands.append(["git", "diff", "--check", "--", *paths])
    for command in commands:
        completed = subprocess.run(command, cwd=root, check=False, text=True, capture_output=True)
        if completed.returncode:
            raise ValidationFailure(completed.stdout + completed.stderr)

def gates() -> tuple[Gate, ...]:
    return (
        Gate("changed-file-coverage", changed_file_coverage),
        Gate("python-compilation", compile_python),
        Gate("unit-tests", run_tests),
        Gate("architectural-imports", architectural_imports),
        Gate("public-api", public_api),
        Gate("compatibility-aliases", compatibility_aliases),
        Gate("documentation-links", documentation_links),
        Gate("git-diff-check", git_diff_check),
    )
