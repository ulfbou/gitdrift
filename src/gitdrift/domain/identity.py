"""Versioned canonicalization and stable identity functions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

IDENTITY_SCHEME = "gitdrift-sha256-json-v1"


def _canonical(value: Any) -> Any:
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {
            str(key): _canonical(item)
            for key, item in sorted(
                value.items(),
                key=lambda pair: str(pair[0]),
            )
        }
    if isinstance(value, (set, frozenset)):
        items = [_canonical(item) for item in value]
        return sorted(
            items,
            key=lambda item: json.dumps(
                item,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        return [_canonical(item) for item in value]
    if isinstance(value, bytes):
        return {
            "$bytes_sha256": hashlib.sha256(value).hexdigest(),
            "$bytes_length": len(value),
        }
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(
        f"unsupported canonical identity value: {type(value).__name__}"
    )


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _canonical(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def stable_id(kind: str, semantic_inputs: Any) -> str:
    if not kind or any(character.isspace() for character in kind):
        raise ValueError("identity kind must be a non-empty token")

    digest = hashlib.sha256(
        canonical_bytes(
            {
                "kind": kind,
                "inputs": semantic_inputs,
                "scheme": IDENTITY_SCHEME,
            }
        )
    ).hexdigest()

    return f"{kind}:{digest}"
