"""Gate orchestration with stable diagnostics and aggregate exit semantics."""
from __future__ import annotations
import sys
from pathlib import Path
from .gates import gates
from .model import ValidationScope

def validate(root: Path, selected: set[str] | None = None, scope: ValidationScope | None = None) -> int:
    failures = 0
    active_scope = scope or ValidationScope()
    for gate in gates():
        if selected is not None and gate.name not in selected:
            continue
        try:
            gate.action(root, active_scope)
        except Exception as error:
            failures += 1
            print(f"FAIL {gate.name}: {error}", file=sys.stderr)
        else:
            print(f"PASS {gate.name}")
    return 1 if failures else 0
