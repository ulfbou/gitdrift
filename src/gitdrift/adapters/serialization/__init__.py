"""Canonical native investigation serialization adapters."""

from .json import CanonicalNativeJsonSerializer, load_native_schema

__all__ = [
    "CanonicalNativeJsonSerializer",
    "load_native_schema",
]
