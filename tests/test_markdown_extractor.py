from __future__ import annotations

import unittest

from gitdrift.adapters.extractors import MarkdownSectionExtractor
from gitdrift.domain import EvidenceClass, EvidenceReference
from gitdrift.ports import ArtifactKind, ExtractionInput


def extraction_input(
    payload: bytes,
    *,
    artifact_kind: ArtifactKind = ArtifactKind.MARKDOWN,
    path: str = "docs/example.md",
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
        configuration_identity="config:markdown-v1",
    )


class MarkdownExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = MarkdownSectionExtractor()

    def test_capability_is_versioned_and_explicit(self) -> None:
        capability = self.extractor.capability

        self.assertEqual(
            capability.extractor_id,
            "gitdrift-markdown-sections",
        )
        self.assertEqual(capability.version, "1.0.0")
        self.assertEqual(
            capability.accepted_artifact_kinds,
            (ArtifactKind.MARKDOWN,),
        )
        self.assertEqual(
            capability.produced_fact_kinds,
            ("markdown-section",),
        )
        self.assertEqual(
            capability.determinism,
            "deterministic",
        )
        self.assertEqual(capability.cost, "linear")
        self.assertEqual(
            capability.configuration_schema_id,
            "gitdrift-markdown-sections-config-v1",
        )

    def test_extracts_atx_and_setext_sections_in_order(self) -> None:
        request = extraction_input(
            b"# Root\n"
            b"intro\n"
            b"## Child\n"
            b"body\n"
            b"Setext\n"
            b"------\n"
            b"tail\n"
        )

        result = self.extractor.extract(request)

        self.assertEqual(
            tuple(fragment.heading for fragment in result.fragments),
            ("Root", "Child", "Setext"),
        )
        self.assertEqual(
            tuple(fragment.heading_level for fragment in result.fragments),
            (1, 2, 2),
        )
        self.assertEqual(
            tuple(fragment.address for fragment in result.fragments),
            ("root", "root/child", "root/setext"),
        )
        self.assertEqual(
            result.fragments[1].parent_address,
            "root",
        )
        self.assertEqual(
            result.completeness.values,
            {
                next(
                    dimension
                    for dimension in result.completeness.values
                    if dimension.value == "semantic-extraction"
                ): "complete",
                next(
                    dimension
                    for dimension in result.completeness.values
                    if dimension.value == "artifact-coverage"
                ): "complete",
            },
        )

    def test_facts_retain_exact_input_evidence(self) -> None:
        request = extraction_input(b"# Evidence\nbody\n")

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
            fact.producer_version,
            self.extractor.capability.version,
        )
        self.assertEqual(
            fact.derivation_class,
            "deterministic",
        )
        self.assertEqual(
            result.fragments[0].fact_id,
            fact.id,
        )

    def test_repeated_execution_is_deterministic(self) -> None:
        request = extraction_input(
            b"# Root\n"
            b"## Child\n"
            b"content\n"
        )

        first = self.extractor.extract(request)
        second = self.extractor.extract(request)

        self.assertEqual(first, second)

    def test_fenced_heading_like_text_is_not_extracted(self) -> None:
        request = extraction_input(
            b"# Real\n"
            b"```markdown\n"
            b"# Not a section\n"
            b"```\n"
            b"## Also real\n"
        )

        result = self.extractor.extract(request)

        self.assertEqual(
            tuple(fragment.heading for fragment in result.fragments),
            ("Real", "Also real"),
        )

    def test_duplicate_heading_addresses_are_explicit(self) -> None:
        request = extraction_input(
            b"# Root\n"
            b"## Repeat\n"
            b"first\n"
            b"## Repeat\n"
            b"second\n"
        )

        result = self.extractor.extract(request)

        self.assertEqual(
            tuple(fragment.address for fragment in result.fragments),
            ("root", "root/repeat", "root/repeat~2"),
        )
        self.assertEqual(
            len({fragment.id for fragment in result.fragments}),
            3,
        )

    def test_empty_and_heading_free_markdown_is_complete(self) -> None:
        for payload in (b"", b"paragraph only\n"):
            with self.subTest(payload=payload):
                result = self.extractor.extract(
                    extraction_input(payload)
                )
                self.assertEqual(result.fragments, ())
                self.assertEqual(result.facts, ())
                self.assertEqual(result.diagnostics, ())

    def test_invalid_utf8_preserves_exact_evidence(self) -> None:
        request = extraction_input(b"# heading\n\xff")

        result = self.extractor.extract(request)

        self.assertEqual(result.fragments, ())
        self.assertEqual(result.facts, ())
        self.assertEqual(
            result.diagnostics[0].code,
            "GD-EXTRACT-MARKDOWN-UTF8",
        )
        self.assertEqual(
            result.diagnostics[0].affected_ids,
            (request.id, request.evidence.id),
        )
        self.assertIn(
            "exact input evidence remains retained",
            result.completeness.limitations[0],
        )

    def test_unsupported_kind_is_not_semantic_absence(self) -> None:
        request = extraction_input(
            b"print('not markdown')\n",
            artifact_kind=ArtifactKind.PYTHON,
            path="src/example.py",
        )

        result = self.extractor.extract(request)

        self.assertEqual(result.fragments, ())
        self.assertEqual(result.facts, ())
        self.assertEqual(
            result.diagnostics[0].code,
            "GD-EXTRACT-MARKDOWN-UNSUPPORTED",
        )
        self.assertEqual(
            result.diagnostics[0].category,
            "unsupported-input",
        )

    def test_input_path_must_remain_inside_workspace(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "workspace-relative",
        ):
            extraction_input(
                b"# Outside\n",
                path="../outside.md",
            )

    def test_input_evidence_must_identify_state(self) -> None:
        evidence = EvidenceReference(
            evidence_class=EvidenceClass.OBSERVED,
            producer="fixture",
            producer_version="1",
            subject_id="state:other",
            payload_identity="sha256:exact-input",
        )

        with self.assertRaisesRegex(
            ValueError,
            "must identify the input state",
        ):
            ExtractionInput(
                state_id="state:expected",
                path="README.md",
                artifact_kind=ArtifactKind.MARKDOWN,
                payload=b"# Heading\n",
                evidence=evidence,
                configuration_identity="config:markdown-v1",
            )


if __name__ == "__main__":
    unittest.main()
