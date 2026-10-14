from __future__ import annotations

import unittest

from gitdrift.adapters.extractors import PythonSymbolExtractor
from gitdrift.domain import EvidenceClass, EvidenceReference
from gitdrift.ports import ArtifactKind, ExtractionInput


def extraction_input(
    payload: bytes,
    *,
    artifact_kind: ArtifactKind = ArtifactKind.PYTHON,
    path: str = "src/example.py",
) -> ExtractionInput:
    state_id = "state:example"
    evidence = EvidenceReference(
        evidence_class=EvidenceClass.OBSERVED,
        producer="fixture",
        producer_version="1",
        subject_id=state_id,
        payload_identity="sha256:exact-input",
    )
    return ExtractionInput(
        state_id=state_id,
        path=path,
        artifact_kind=artifact_kind,
        payload=payload,
        evidence=evidence,
        configuration_identity="config:python-v1",
    )


class PythonSymbolExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = PythonSymbolExtractor()

    def test_capability_is_versioned_and_explicit(self) -> None:
        capability = self.extractor.capability
        self.assertEqual(
            capability.extractor_id,
            "gitdrift-python-symbols",
        )
        self.assertEqual(capability.version, "1.0.0")
        self.assertEqual(
            capability.accepted_artifact_kinds,
            (ArtifactKind.PYTHON,),
        )
        self.assertEqual(
            capability.produced_fact_kinds,
            ("python-symbol",),
        )
        self.assertEqual(
            capability.configuration_schema_id,
            "gitdrift-python-symbols-config-v1",
        )

    def test_extracts_nested_sync_and_async_symbols(self) -> None:
        request = extraction_input(
            b"class Outer:\n"
            b"    def method(self):\n"
            b"        def nested():\n"
            b"            return 1\n"
            b"        return nested()\n"
            b"\n"
            b"async def top():\n"
            b"    return None\n"
        )
        result = self.extractor.extract(request)
        self.assertEqual(
            tuple(
                symbol.qualified_name
                for symbol in result.fragments
            ),
            (
                "Outer",
                "Outer.method",
                "Outer.method.nested",
                "top",
            ),
        )
        self.assertEqual(
            tuple(symbol.kind for symbol in result.fragments),
            ("class", "function", "function", "function"),
        )
        self.assertEqual(
            tuple(
                symbol.is_async
                for symbol in result.fragments
            ),
            (False, False, False, True),
        )
        self.assertEqual(
            result.fragments[2].parent_qualified_name,
            "Outer.method",
        )

    def test_facts_retain_exact_input_evidence(self) -> None:
        request = extraction_input(
            b"def example():\n"
            b"    return 1\n"
        )
        result = self.extractor.extract(request)
        self.assertEqual(len(result.facts), 1)
        fact = result.facts[0]
        self.assertEqual(
            fact.input_evidence_ids,
            (request.evidence.id,),
        )
        self.assertEqual(fact.state_id, request.state_id)
        self.assertEqual(
            fact.producer,
            self.extractor.capability.extractor_id,
        )
        self.assertEqual(
            result.fragments[0].fact_id,
            fact.id,
        )
        self.assertTrue(
            result.fragments[0].content_identity.startswith(
                "sha256:"
            )
        )

    def test_repeated_execution_is_deterministic(self) -> None:
        request = extraction_input(
            b"class Example:\n"
            b"    async def run(self):\n"
            b"        return None\n"
        )
        self.assertEqual(
            self.extractor.extract(request),
            self.extractor.extract(request),
        )

    def test_symbol_free_python_is_complete(self) -> None:
        result = self.extractor.extract(
            extraction_input(b"VALUE = 1\n")
        )
        self.assertEqual(result.fragments, ())
        self.assertEqual(result.facts, ())
        self.assertEqual(result.diagnostics, ())

    def test_invalid_utf8_preserves_exact_evidence(self) -> None:
        request = extraction_input(
            b"def valid():\n    pass\n\xff"
        )
        result = self.extractor.extract(request)
        self.assertEqual(result.fragments, ())
        self.assertEqual(
            result.diagnostics[0].code,
            "GD-EXTRACT-PYTHON-UTF8",
        )
        self.assertEqual(
            result.diagnostics[0].affected_ids,
            (request.id, request.evidence.id),
        )
        self.assertIn(
            "exact input evidence remains retained",
            result.completeness.limitations[0],
        )

    def test_malformed_python_is_not_false_absence(self) -> None:
        request = extraction_input(b"def broken(:\n")
        result = self.extractor.extract(request)
        self.assertEqual(result.fragments, ())
        self.assertEqual(result.facts, ())
        self.assertEqual(
            result.diagnostics[0].code,
            "GD-EXTRACT-PYTHON-SYNTAX",
        )
        self.assertIn(
            "exact input evidence remains retained",
            result.completeness.limitations[0],
        )

    def test_unsupported_kind_is_not_false_absence(self) -> None:
        request = extraction_input(
            b"# Heading\n",
            artifact_kind=ArtifactKind.MARKDOWN,
            path="docs/example.md",
        )
        result = self.extractor.extract(request)
        self.assertEqual(result.fragments, ())
        self.assertEqual(
            result.diagnostics[0].code,
            "GD-EXTRACT-PYTHON-UNSUPPORTED",
        )

    def test_input_path_must_be_workspace_relative(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "workspace-relative",
        ):
            extraction_input(
                b"def outside():\n    pass\n",
                path="../outside.py",
            )


if __name__ == "__main__":
    unittest.main()
