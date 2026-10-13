# Hosted integration validation

## Status

Repository-governance implementation for ADR-002.

## Boundary

Local validation and hosted enforcement are distinct controls.

The canonical local validator is:

```bash
python scripts/validation/validate.py
```

The canonical GitHub Actions workflow invokes that validator for pull
requests targeting `master`.

Local validation establishes candidate quality before publication. It
does not prove that GitHub prevents an invalid candidate from entering
`master`.

Hosted enforcement is owned by the repository-level ruleset
`gitdrift-master-integration`.

The ruleset must:

- target only `refs/heads/master`;
- require pull requests;
- require the observed canonical GitHub Actions check;
- enable strict required-check behavior;
- prohibit deletion;
- prohibit non-fast-forward updates; and
- contain no bypass actors.

## Independent verification

```bash
python scripts/governance/verify-master-ruleset.py \
  --characterization \
  "$CARRIER_SOURCE_DIR/issue-8-phase-8.1-hosted-boundary.json"
```

The verifier retrieves the exact repository ruleset and all active
rules effectively applying to `master`.

Every mandatory requirement produces `pass`, `fail`, or `unresolved`.
Failed and unresolved mandatory requirements return nonzero.

The characterization evidence identifies the canonical required check
from a real GitHub Actions execution. The verifier does not assume that
a display label such as `validation/validate` is authoritative.

## Product separation

GitHub-specific governance tooling remains under
`scripts/governance/`, outside Gitdrift analytical product logic.

The canonical offline validator acquires no network dependency.
Hosted metadata remains outside the Gitdrift 0.1 analytical runtime
evidence model.
