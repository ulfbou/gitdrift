"""Versioned deterministic Python symbol extraction."""
from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass

from gitdrift.domain import (
    CompletenessDeclaration,
    CompletenessDimension,
    DerivationClass,
    DiagnosticRecord,
    Fact,
)
from gitdrift.ports.extraction import (
    ArtifactKind,
    ExtractedSymbol,
    ExtractionInput,
    ExtractionResult,
    ExtractorCapability,
    ExtractorCost,
    ExtractorDeterminism,
)

_EXTRACTOR_ID = "gitdrift-python-symbols"
_EXTRACTOR_VERSION = "1.0.0"
_CONFIGURATION_SCHEMA = "gitdrift-python-symbols-config-v1"


@dataclass(frozen=True, slots=True)
class _Symbol:
    kind: str
    name: str
    qualified_name: str
    parent_qualified_name: str | None
    start_line: int
    end_line: int
    is_async: bool


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self._parents: list[str] = []
        self.symbols: list[_Symbol] = []

    def _record(
        self,
        node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
        *,
        kind: str,
        is_async: bool,
    ) -> None:
        qualified_name = ".".join((*self._parents, node.name))
        self.symbols.append(
            _Symbol(
                kind=kind,
                name=node.name,
                qualified_name=qualified_name,
                parent_qualified_name=(
                    ".".join(self._parents)
                    if self._parents
                    else None
                ),
                start_line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                is_async=is_async,
            )
        )
        self._parents.append(node.name)
        self.generic_visit(node)
        self._parents.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._record(node, kind="class", is_async=False)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record(node, kind="function", is_async=False)

    def visit_AsyncFunctionDef(
        self,
        node: ast.AsyncFunctionDef,
    ) -> None:
        self._record(node, kind="function", is_async=True)


class PythonSymbolExtractor:
    """Extract Python symbols without importing or executing source."""

    @property
    def capability(self) -> ExtractorCapability:
        return ExtractorCapability(
            extractor_id=_EXTRACTOR_ID,
            version=_EXTRACTOR_VERSION,
            accepted_artifact_kinds=(ArtifactKind.PYTHON,),
            produced_fact_kinds=("python-symbol",),
            determinism=ExtractorDeterminism.DETERMINISTIC,
            cost=ExtractorCost.LINEAR,
            configuration_schema_id=_CONFIGURATION_SCHEMA,
            limitations=(
                "Symbols are derived from the Python AST without execution.",
                "Dynamic and runtime-generated symbols are not inferred.",
                "Symbol presence is structural evidence, not authority.",
            ),
        )

    def extract(
        self,
        request: ExtractionInput,
    ) -> ExtractionResult:
        if request.artifact_kind is not ArtifactKind.PYTHON:
            return self._unavailable(
                request,
                code="GD-EXTRACT-PYTHON-UNSUPPORTED",
                limitation=(
                    "The selected extractor does not support artifact kind "
                    f"{request.artifact_kind.value}."
                ),
            )

        try:
            text = request.payload.decode("utf-8")
        except UnicodeDecodeError:
            return self._unavailable(
                request,
                code="GD-EXTRACT-PYTHON-UTF8",
                limitation=(
                    "Python extraction requires valid UTF-8; "
                    "exact input evidence remains retained."
                ),
            )

        try:
            tree = ast.parse(
                text,
                filename=request.path,
                type_comments=True,
            )
        except (SyntaxError, ValueError) as error:
            return self._unavailable(
                request,
                code="GD-EXTRACT-PYTHON-SYNTAX",
                limitation=(
                    "Python syntax could not be parsed; exact input "
                    "evidence remains retained "
                    f"({type(error).__name__})."
                ),
            )

        visitor = _SymbolVisitor()
        visitor.visit(tree)
        lines = text.splitlines(keepends=True)

        facts: list[Fact] = []
        symbols: list[ExtractedSymbol] = []

        for symbol in visitor.symbols:
            payload = "".join(
                lines[symbol.start_line - 1 : symbol.end_line]
            ).encode("utf-8")
            content_identity = (
                "sha256:" + hashlib.sha256(payload).hexdigest()
            )
            fact = Fact(
                subject=(
                    f"{request.path}#{symbol.qualified_name}"
                ),
                assertion=(
                    f"python-symbol kind={symbol.kind} "
                    f"qualified_name={symbol.qualified_name!r} "
                    f"async={symbol.is_async}"
                ),
                state_id=request.state_id,
                producer=self.capability.extractor_id,
                producer_version=self.capability.version,
                method="python-ast-symbols-v1",
                derivation_class=DerivationClass.DETERMINISTIC,
                confidence_class="deterministic",
                input_evidence_ids=(request.evidence.id,),
                limitations=self.capability.limitations,
            )
            facts.append(fact)
            symbols.append(
                ExtractedSymbol(
                    extraction_input_id=request.id,
                    kind=symbol.kind,
                    qualified_name=symbol.qualified_name,
                    name=symbol.name,
                    parent_qualified_name=(
                        symbol.parent_qualified_name
                    ),
                    start_line=symbol.start_line,
                    end_line=symbol.end_line,
                    is_async=symbol.is_async,
                    content_identity=content_identity,
                    fact_id=fact.id,
                )
            )

        return ExtractionResult(
            capability=self.capability,
            extraction_input=request,
            fragments=tuple(symbols),
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

    def _unavailable(
        self,
        request: ExtractionInput,
        *,
        code: str,
        limitation: str,
    ) -> ExtractionResult:
        return ExtractionResult(
            capability=self.capability,
            extraction_input=request,
            fragments=(),
            facts=(),
            diagnostics=(
                DiagnosticRecord(
                    code=code,
                    severity="warning",
                    category="unsupported-input",
                    affected_ids=(
                        request.id,
                        request.evidence.id,
                    ),
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
                limitations=(limitation,),
            ),
        )
