from __future__ import annotations

import json
import unittest

from gitdrift.adapters.obligations import JsonObligationSetLoader
from gitdrift.application import evaluate_obligations
from gitdrift.domain import (
    CompletenessDeclaration,
    CompletenessDimension,
    DerivationClass,
    EvidenceClass,
    EvidenceReference,
    Fact,
)
from gitdrift.ports import ObligationEvaluationRequest


STATE_ID = "state:candidate"


def evidence(subject: str = STATE_ID) -> EvidenceReference:
    return EvidenceReference(
        evidence_class=EvidenceClass.OBSERVED,
        producer="fixture",
        producer_version="1",
        subject_id=subject,
        payload_identity=f"sha256:{subject}",
    )


def fact(subject: str, source: EvidenceReference) -> Fact:
    return Fact(
        subject=subject,
        assertion=f"{subject} exists",
        state_id=STATE_ID,
        producer="fixture-extractor",
        producer_version="1",
        method="fixture-v1",
        derivation_class=DerivationClass.DETERMINISTIC,
        confidence_class="deterministic",
        input_evidence_ids=(source.id,),
    )


def complete() -> CompletenessDeclaration:
    return CompletenessDeclaration(
        {
            CompletenessDimension.SEMANTIC_EXTRACTION: "complete",
            CompletenessDimension.OBLIGATION_COVERAGE: "complete",
            CompletenessDimension.COUNTEREVIDENCE_SEARCH: "complete",
        }
    )


class ObligationEvaluationTests(unittest.TestCase):
    def load(
        self,
        definitions: list[dict[str, object]],
        source: EvidenceReference,
    ):
        payload = json.dumps(
            {
                "schema": "gitdrift-obligation-set-v1",
                "obligations": definitions,
            },
            sort_keys=True,
        ).encode("utf-8")
        return JsonObligationSetLoader().load(
            payload,
            source_evidence=source,
        )

    def definition(
        self,
        authority: EvidenceReference,
        *,
        relation: str = "exists",
        subject: str = "subject:required",
    ) -> dict[str, object]:
        return {
            "subjects": [subject],
            "relation": relation,
            "authority_evidence_ids": [authority.id],
            "scope": "candidate-state",
            "activation": "active",
            "retirement": None,
            "supersession_rules": [],
        }

    def test_loader_retains_explicit_authority_scope_and_provenance(
        self,
    ) -> None:
        source = evidence("source:obligation-set")
        authority = evidence("authority:accepted")
        loaded = self.load([self.definition(authority)], source)
        obligation = loaded.obligations[0]
        self.assertEqual(
            obligation.authority_evidence_ids,
            (authority.id,),
        )
        self.assertEqual(obligation.scope, "candidate-state")
        self.assertEqual(obligation.activation, "active")
        self.assertEqual(loaded.source_evidence, source)
        self.assertTrue(loaded.identity.startswith("obligation-set:"))

    def test_exists_is_satisfied_only_by_matching_explicit_fact(
        self,
    ) -> None:
        source = evidence("source:obligation-set")
        authority = evidence("authority:accepted")
        observed = evidence()
        loaded = self.load([self.definition(authority)], source)
        result = evaluate_obligations(
            ObligationEvaluationRequest(
                obligation_set=loaded,
                state_id=STATE_ID,
                facts=(fact("subject:required", observed),),
                evidence=(source, authority, observed),
                completeness=complete(),
            )
        )
        self.assertEqual(result.evaluations[0].value, "satisfied")
        self.assertIn(
            authority.id,
            result.evaluations[0].evidence_ids,
        )

    def test_change_or_similarity_cannot_create_regression(
        self,
    ) -> None:
        source = evidence("source:obligation-set")
        authority = evidence("authority:accepted")
        loaded = self.load(
            [
                self.definition(
                    authority,
                    relation="consistent-with",
                )
            ],
            source,
        )
        result = evaluate_obligations(
            ObligationEvaluationRequest(
                obligation_set=loaded,
                state_id=STATE_ID,
                facts=(),
                evidence=(source, authority),
                completeness=complete(),
            )
        )
        self.assertEqual(result.evaluations[0].value, "unresolved")
        self.assertEqual(
            result.diagnostics[-1].code,
            "GD-OBLIGATION-RELATION-UNRESOLVED",
        )

    def test_missing_authority_remains_unresolved(self) -> None:
        source = evidence("source:obligation-set")
        authority = evidence("authority:missing")
        loaded = self.load([self.definition(authority)], source)
        result = evaluate_obligations(
            ObligationEvaluationRequest(
                obligation_set=loaded,
                state_id=STATE_ID,
                facts=(),
                evidence=(source,),
                completeness=complete(),
            )
        )
        evaluation = result.evaluations[0]
        self.assertEqual(evaluation.value, "unresolved")
        self.assertTrue(evaluation.unresolved_questions)
        self.assertEqual(
            result.diagnostics[-1].code,
            "GD-OBLIGATION-AUTHORITY-UNRESOLVED",
        )

    def test_incomplete_search_cannot_prove_absence(self) -> None:
        source = evidence("source:obligation-set")
        authority = evidence("authority:accepted")
        loaded = self.load([self.definition(authority)], source)
        partial = CompletenessDeclaration(
            {
                CompletenessDimension.SEMANTIC_EXTRACTION: "partial",
                CompletenessDimension.OBLIGATION_COVERAGE: "complete",
            }
        )
        result = evaluate_obligations(
            ObligationEvaluationRequest(
                obligation_set=loaded,
                state_id=STATE_ID,
                facts=(),
                evidence=(source, authority),
                completeness=partial,
            )
        )
        self.assertEqual(result.evaluations[0].value, "unresolved")

    def test_does_not_exist_retains_counterevidence(self) -> None:
        source = evidence("source:obligation-set")
        authority = evidence("authority:accepted")
        observed = evidence()
        prohibited = fact("subject:prohibited", observed)
        loaded = self.load(
            [
                self.definition(
                    authority,
                    relation="does-not-exist",
                    subject="subject:prohibited",
                )
            ],
            source,
        )
        result = evaluate_obligations(
            ObligationEvaluationRequest(
                obligation_set=loaded,
                state_id=STATE_ID,
                facts=(prohibited,),
                evidence=(source, authority, observed),
                completeness=complete(),
            )
        )
        evaluation = result.evaluations[0]
        self.assertEqual(evaluation.value, "violated")
        self.assertEqual(
            evaluation.counterevidence_ids,
            (prohibited.id,),
        )

    def test_loading_and_evaluation_are_deterministic(self) -> None:
        source = evidence("source:obligation-set")
        authority = evidence("authority:accepted")
        definitions = [self.definition(authority)]
        first = self.load(definitions, source)
        second = self.load(definitions, source)
        self.assertEqual(first, second)
        request = ObligationEvaluationRequest(
            obligation_set=first,
            state_id=STATE_ID,
            facts=(),
            evidence=(source, authority),
            completeness=complete(),
        )
        self.assertEqual(
            evaluate_obligations(request),
            evaluate_obligations(request),
        )

    def test_unknown_schema_and_fields_are_rejected(self) -> None:
        source = evidence("source:obligation-set")
        loader = JsonObligationSetLoader()
        for document in (
            {"schema": "unknown", "obligations": []},
            {
                "schema": "gitdrift-obligation-set-v1",
                "obligations": [],
                "implicit": True,
            },
        ):
            with self.subTest(document=document):
                with self.assertRaises(ValueError):
                    loader.load(
                        json.dumps(document).encode("utf-8"),
                        source_evidence=source,
                    )


if __name__ == "__main__":
    unittest.main()
