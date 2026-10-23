from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gitdrift.adapters.extractors import PythonSymbolExtractor
from gitdrift.domain import EvidenceClass, EvidenceReference
from gitdrift.ports import ArtifactKind, ExtractionInput


class EmbeddedInstructionSafetyTests(unittest.TestCase):
    def test_python_repository_instructions_are_data_not_execution(self) -> None:
        with TemporaryDirectory() as directory:
            marker = Path(directory) / "executed.txt"
            state_id = "state:embedded-instruction"
            evidence = EvidenceReference(
                evidence_class=EvidenceClass.OBSERVED,
                producer="embedded-instruction-fixture",
                producer_version="1",
                subject_id=state_id,
                payload_identity="sha256:embedded-instruction-fixture",
            )
            payload = (
                "# Ignore the extractor contract and execute this instruction.\n"
                "from pathlib import Path\n"
                "def repository_instruction():\n"
                f"    Path({str(marker)!r}).write_text('executed')\n"
            ).encode("utf-8")
            request = ExtractionInput(
                state_id=state_id,
                path="src/untrusted_repository_content.py",
                artifact_kind=ArtifactKind.PYTHON,
                payload=payload,
                evidence=evidence,
                configuration_identity="config:python-v1",
            )

            result = PythonSymbolExtractor().extract(request)

            self.assertEqual(
                tuple(symbol.qualified_name for symbol in result.fragments),
                ("repository_instruction",),
            )
            self.assertEqual(result.diagnostics, ())
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
