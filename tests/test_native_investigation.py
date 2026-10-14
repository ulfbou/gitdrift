from __future__ import annotations

import json
import unittest
from pathlib import Path

from gitdrift.adapters.serialization import (
    CanonicalNativeJsonSerializer,
    load_native_schema,
)
from gitdrift.adapters.sinks import MemoryByteSink
from gitdrift.application import serialize_and_deliver
from gitdrift.domain import (
    ArtifactSnapshot,
    CompletenessDeclaration,
    CompletenessDimension,
    Investigation,
    ReferenceClosureError,
    RepositoryState,
    ReproductionManifest,
    StateKind,
)
from gitdrift.ports import (
    NATIVE_SCHEMA_ID,
    NATIVE_SCHEMA_VERSION,
    OutputSinkError,
)


GOLDEN = (
    Path(__file__).parent
    / "fixtures"
    / "native"
    / "investigation-v1.golden.json"
)


def investigation() -> Investigation:
    state = RepositoryState(
        StateKind.COMMIT,
        "repo:fixture",
        "commit:abc;tree:def",
    )
    snapshot = ArtifactSnapshot(
        state.id,
        "README.md",
        "sha256:readme",
    )
    manifest = ReproductionManifest(
        repository_id="repo:fixture",
        state_ids=(state.id,),
        configuration_identity="configuration:fixture",
        capability_identity="capability:fixture",
        native_schema_version=NATIVE_SCHEMA_VERSION,
        producer_version="0.0.0",
        budgets={"bytes": 4096},
    )
    return Investigation(
        manifest=manifest,
        states=(state,),
        snapshots=(snapshot,),
        completeness=CompletenessDeclaration(
            {
                CompletenessDimension.STATE_CAPTURE: "complete",
                CompletenessDimension.ARTIFACT_COVERAGE: "complete",
            }
        ),
    )


class NativeInvestigationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.serializer = CanonicalNativeJsonSerializer()

    def test_packaged_schema_has_independent_identity(self) -> None:
        schema = load_native_schema()
        self.assertEqual(schema["$id"], NATIVE_SCHEMA_ID)
        self.assertEqual(
            schema["x-gitdrift-schema-version"],
            NATIVE_SCHEMA_VERSION,
        )

    def test_serialization_is_canonical_and_deterministic(self) -> None:
        current = investigation()
        first = self.serializer.serialize(current)
        second = self.serializer.serialize(current)

        self.assertEqual(first, second)
        self.assertTrue(first.payload.endswith(b"\n"))
        self.assertEqual(first.schema_id, NATIVE_SCHEMA_ID)
        self.assertEqual(
            first.schema_version,
            NATIVE_SCHEMA_VERSION,
        )

        document = json.loads(first.payload)
        self.assertEqual(document["schema"], NATIVE_SCHEMA_ID)
        self.assertEqual(
            document["investigation_id"],
            first.investigation_id,
        )
        self.assertEqual(
            first.payload,
            (
                json.dumps(
                    document,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8"),
        )

    def test_record_order_does_not_control_artifact_identity(self) -> None:
        original = investigation()
        state = original.states[0]
        other = RepositoryState(
            StateKind.EXPLICIT_SNAPSHOT,
            "repo:fixture",
            "snapshot:other",
        )
        manifest = ReproductionManifest(
            repository_id="repo:fixture",
            state_ids=tuple(sorted((state.id, other.id))),
            configuration_identity="configuration:fixture",
            capability_identity="capability:fixture",
            native_schema_version=NATIVE_SCHEMA_VERSION,
            producer_version="0.0.0",
        )
        first = Investigation(
            manifest=manifest,
            states=(state, other),
        )
        second = Investigation(
            manifest=manifest,
            states=(other, state),
        )

        left = self.serializer.serialize(first)
        right = self.serializer.serialize(second)
        self.assertEqual(left, right)

    def test_reference_closure_precedes_artifact_success(self) -> None:
        broken = Investigation(
            manifest=ReproductionManifest(
                repository_id="repo:fixture",
                state_ids=("state:missing",),
                configuration_identity="configuration:fixture",
                capability_identity="capability:fixture",
                native_schema_version=NATIVE_SCHEMA_VERSION,
                producer_version="0.0.0",
            )
        )
        with self.assertRaises(ReferenceClosureError):
            self.serializer.serialize(broken)

    def test_sink_receives_exact_complete_payload(self) -> None:
        sink = MemoryByteSink()
        result = serialize_and_deliver(
            investigation(),
            self.serializer,
            sink,
        )
        self.assertEqual(sink.payload, result.artifact.payload)

    def test_sink_failure_retains_no_partial_artifact(self) -> None:
        sink = MemoryByteSink(fail=True)
        with self.assertRaises(OutputSinkError):
            serialize_and_deliver(
                investigation(),
                self.serializer,
                sink,
            )
        self.assertIsNone(sink.payload)

    def test_golden_native_artifact_matches_semantically(self) -> None:
        current = json.loads(
            self.serializer.serialize(investigation()).payload
        )
        expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(current, expected)


if __name__ == "__main__":
    unittest.main()
