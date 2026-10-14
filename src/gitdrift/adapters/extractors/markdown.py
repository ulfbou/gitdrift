"""Versioned deterministic Markdown section extraction."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

from gitdrift.domain import (
    CompletenessDeclaration,
    CompletenessDimension,
    DerivationClass,
    DiagnosticRecord,
    Fact,
)
from gitdrift.ports.extraction import (
    ArtifactKind,
    ExtractedFragment,
    ExtractionInput,
    ExtractionResult,
    ExtractorCapability,
    ExtractorCost,
    ExtractorDeterminism,
)

_ATX = re.compile(
    r"^(?P<indent> {0,3})(?P<marks>#{1,6})"
    r"(?:[ \t]+(?P<title>.*?)[ \t]*#*[ \t]*|[ \t]*)$"
)
_SETEXT = re.compile(r"^ {0,3}(?P<marks>=+|-+)[ \t]*$")
_FENCE = re.compile(r"^ {0,3}(?P<marks>`{3,}|~{3,})(?P<rest>.*)$")

_EXTRACTOR_ID = "gitdrift-markdown-sections"
_EXTRACTOR_VERSION = "1.0.0"
_CONFIGURATION_SCHEMA = "gitdrift-markdown-sections-config-v1"


@dataclass(frozen=True, slots=True)
class _Heading:
    level: int
    title: str
    line: int


def _slug(value: str) -> str:
    normalized = value.strip().casefold()
    slug = re.sub(r"[^\w\-\s]", "", normalized, flags=re.UNICODE)
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug or "section"


def _headings(lines: tuple[str, ...]) -> Iterable[_Heading]:
    in_fence = False
    fence_character = ""
    fence_length = 0
    previous_candidate: tuple[int, str] | None = None

    for number, line in enumerate(lines, start=1):
        fence = _FENCE.match(line)
        if fence:
            marks = fence.group("marks")
            if not in_fence:
                in_fence = True
                fence_character = marks[0]
                fence_length = len(marks)
            elif (
                marks[0] == fence_character
                and len(marks) >= fence_length
                and not fence.group("rest").strip()
            ):
                in_fence = False
                fence_character = ""
                fence_length = 0
            previous_candidate = None
            continue

        if in_fence:
            previous_candidate = None
            continue

        atx = _ATX.match(line)
        if atx:
            title = (atx.group("title") or "").strip()
            if title:
                yield _Heading(
                    len(atx.group("marks")),
                    title,
                    number,
                )
            previous_candidate = None
            continue

        setext = _SETEXT.match(line)
        if setext and previous_candidate is not None:
            previous_line, title = previous_candidate
            yield _Heading(
                1 if setext.group("marks")[0] == "=" else 2,
                title.strip(),
                previous_line,
            )
            previous_candidate = None
            continue

        if line.strip():
            previous_candidate = (number, line)
        else:
            previous_candidate = None


class MarkdownSectionExtractor:
    """Extract ATX and Setext sections from exact UTF-8 Markdown."""

    @property
    def capability(self) -> ExtractorCapability:
        return ExtractorCapability(
            extractor_id=_EXTRACTOR_ID,
            version=_EXTRACTOR_VERSION,
            accepted_artifact_kinds=(ArtifactKind.MARKDOWN,),
            produced_fact_kinds=("markdown-section",),
            determinism=ExtractorDeterminism.DETERMINISTIC,
            cost=ExtractorCost.LINEAR,
            configuration_schema_id=_CONFIGURATION_SCHEMA,
            limitations=(
                "HTML headings are not interpreted as Markdown sections.",
                "Heading text is structural evidence, not semantic authority.",
            ),
        )

    def extract(self, request: ExtractionInput) -> ExtractionResult:
        if request.artifact_kind is not ArtifactKind.MARKDOWN:
            return self._unsupported(request)

        try:
            text = request.payload.decode("utf-8")
        except UnicodeDecodeError:
            return self._undecodable(request)

        lines = tuple(text.splitlines())
        headings = tuple(_headings(lines))

        addresses: dict[str, int] = {}
        hierarchy: list[tuple[int, str]] = []
        facts: list[Fact] = []
        fragments: list[ExtractedFragment] = []

        for index, heading in enumerate(headings):
            while hierarchy and hierarchy[-1][0] >= heading.level:
                hierarchy.pop()

            parent_address = hierarchy[-1][1] if hierarchy else None
            base_address = (
                f"{parent_address}/{_slug(heading.title)}"
                if parent_address is not None
                else _slug(heading.title)
            )
            occurrence = addresses.get(base_address, 0) + 1
            addresses[base_address] = occurrence
            address = (
                base_address
                if occurrence == 1
                else f"{base_address}~{occurrence}"
            )

            next_line = (
                headings[index + 1].line
                if index + 1 < len(headings)
                else len(lines) + 1
            )
            end_line = max(heading.line, next_line - 1)
            section_text = "\n".join(
                lines[heading.line - 1 : end_line]
            )
            content_identity = (
                "sha256:"
                + hashlib.sha256(
                    section_text.encode("utf-8")
                ).hexdigest()
            )

            fact = Fact(
                subject=f"{request.path}#{address}",
                assertion=(
                    f"markdown-section level={heading.level} "
                    f"heading={heading.title!r}"
                ),
                state_id=request.state_id,
                producer=self.capability.extractor_id,
                producer_version=self.capability.version,
                method="commonmark-heading-structure-v1",
                derivation_class=DerivationClass.DETERMINISTIC,
                confidence_class="deterministic",
                input_evidence_ids=(request.evidence.id,),
                limitations=self.capability.limitations,
            )
            facts.append(fact)

            fragments.append(
                ExtractedFragment(
                    extraction_input_id=request.id,
                    kind="markdown-section",
                    address=address,
                    heading_level=heading.level,
                    heading=heading.title,
                    parent_address=parent_address,
                    start_line=heading.line,
                    end_line=end_line,
                    content_identity=content_identity,
                    fact_id=fact.id,
                )
            )
            hierarchy.append((heading.level, address))

        return ExtractionResult(
            capability=self.capability,
            extraction_input=request,
            fragments=tuple(fragments),
            facts=tuple(facts),
            diagnostics=(),
            completeness=CompletenessDeclaration(
                {
                    CompletenessDimension.SEMANTIC_EXTRACTION: (
                        "complete"
                    ),
                    CompletenessDimension.ARTIFACT_COVERAGE: (
                        "complete"
                    ),
                }
            ),
        )

    def _unsupported(
        self,
        request: ExtractionInput,
    ) -> ExtractionResult:
        return ExtractionResult(
            capability=self.capability,
            extraction_input=request,
            fragments=(),
            facts=(),
            diagnostics=(
                DiagnosticRecord(
                    code="GD-EXTRACT-MARKDOWN-UNSUPPORTED",
                    severity="warning",
                    category="unsupported-input",
                    affected_ids=(request.id, request.evidence.id),
                    completeness_effects={
                        CompletenessDimension.SEMANTIC_EXTRACTION: (
                            "unavailable"
                        )
                    },
                ),
            ),
            completeness=CompletenessDeclaration(
                {
                    CompletenessDimension.SEMANTIC_EXTRACTION: (
                        "unavailable"
                    ),
                    CompletenessDimension.ARTIFACT_COVERAGE: (
                        "complete"
                    ),
                },
                limitations=(
                    "The selected extractor does not support "
                    f"artifact kind {request.artifact_kind.value}.",
                ),
            ),
        )

    def _undecodable(
        self,
        request: ExtractionInput,
    ) -> ExtractionResult:
        return ExtractionResult(
            capability=self.capability,
            extraction_input=request,
            fragments=(),
            facts=(),
            diagnostics=(
                DiagnosticRecord(
                    code="GD-EXTRACT-MARKDOWN-UTF8",
                    severity="warning",
                    category="unsupported-input",
                    affected_ids=(request.id, request.evidence.id),
                    completeness_effects={
                        CompletenessDimension.SEMANTIC_EXTRACTION: (
                            "unavailable"
                        )
                    },
                ),
            ),
            completeness=CompletenessDeclaration(
                {
                    CompletenessDimension.SEMANTIC_EXTRACTION: (
                        "unavailable"
                    ),
                    CompletenessDimension.ARTIFACT_COVERAGE: (
                        "complete"
                    ),
                },
                limitations=(
                    "Markdown extraction requires valid UTF-8; "
                    "exact input evidence remains retained.",
                ),
            ),
        )
