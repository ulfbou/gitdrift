# Gitdrift

Gitdrift is an evidence-first Python library product for repository evolution analysis, with a thin CLI adapter.

This development skeleton establishes package and machine-contract boundaries only. It does not yet implement repository acquisition, state-awareness analysis, semantic extraction, obligation evaluation, case construction, or native investigation serialization.

## Current executable surface

```bash
python -m gitdrift discover
```

The command emits a machine-readable capability document describing only the active skeleton. Deferred capabilities are reported as unavailable and cannot be mistaken for implemented analysis.
