from __future__ import annotations

import unittest

from gitdrift.application import build_case
from gitdrift.domain import (
    CompletenessDeclaration,
    CompletenessDimension,
)
from gitdrift.ports import CaseConstructionRequest


def request(
    *,
    unknowns: tuple[str, ...] = ("Is authority complete?",),
    judgment: str | None = None,
    available_record_ids: frozenset[str] | None = None,
) -> CaseConstructionRequest:
    known = frozenset(
        {
            "subject:one",
            "observation:one",
            "interpretation:one",
            "obligation:one",
            "evaluation:one",
            "assessment:one",
            "evidence:supporting",
            "evidence:counter",
            "reproduction:one",
        }
    )
    return CaseConstructionRequest(
        question=(
            "Did the candidate weaken obligation:one at state:candidate?"
        ),
        subject_ids=("subject:one",),
        observation_ids=("observation:one",),
        interpretation_ids=("interpretation:one",),
        obligation_ids=("obligation:one",),
        evaluation_ids=("evaluation:one",),
        assessment_ids=("assessment:one",),
        supporting_evidence_ids=("evidence:supporting",),
        counterevidence_ids=("evidence:counter",),
        alternatives=(
            "An equivalent representation may exist outside scope.",
        ),
        unknowns=unknowns,
        completeness=CompletenessDeclaration(
            {
                CompletenessDimension.ARTIFACT_COVERAGE: "complete",
                CompletenessDimension.SEMANTIC_EXTRACTION: "partial",
                CompletenessDimension.OBLIGATION_COVERAGE: "complete",
                CompletenessDimension.COUNTEREVIDENCE_SEARCH: "partial",
            }
        ),
        reproduction_id="reproduction:one",
        evidence_inventory_ids=(
            "observation:one",
            "interpretation:one",
            "evidence:supporting",
            "evidence:counter",
        ),
        available_record_ids=(
            known
            if available_record_ids is None
            else available_record_ids
        ),
        judgment=judgment,
    )


class CaseConstructionTests(unittest.TestCase):
    def test_constructs_every_required_case_dimension(self) -> None:
        result = build_case(request())
        case = result.case

        self.assertTrue(result.unresolved)
        self.assertEqual(case.subject_ids, ("subject:one",))
        self.assertEqual(case.observation_ids, ("observation:one",))
        self.assertEqual(
            case.interpretation_ids,
            ("interpretation:one",),
        )
        self.assertEqual(case.obligation_ids, ("obligation:one",))
        self.assertEqual(case.evaluation_ids, ("evaluation:one",))
        self.assertEqual(case.assessment_ids, ("assessment:one",))
        self.assertEqual(
            case.supporting_evidence_ids,
            ("evidence:supporting",),
        )
        self.assertEqual(
            case.counterevidence_ids,
            ("evidence:counter",),
        )
        self.assertTrue(case.alternatives)
        self.assertTrue(case.unknowns)
        self.assertEqual(
            case.reproduction_id,
            "reproduction:one",
        )
        self.assertEqual(
            set(case.evidence_inventory_ids),
            {
                "observation:one",
                "interpretation:one",
                "evidence:supporting",
                "evidence:counter",
            },
        )
        self.assertIsNone(case.judgment)

    def test_repeated_construction_is_deterministic(self) -> None:
        current = request()
        self.assertEqual(build_case(current), build_case(current))

    def test_input_order_does_not_control_case_identity(self) -> None:
        first = request()
        second = CaseConstructionRequest(
            question=first.question,
            subject_ids=first.subject_ids,
            observation_ids=first.observation_ids,
            interpretation_ids=first.interpretation_ids,
            obligation_ids=first.obligation_ids,
            evaluation_ids=first.evaluation_ids,
            assessment_ids=first.assessment_ids,
            supporting_evidence_ids=first.supporting_evidence_ids,
            counterevidence_ids=first.counterevidence_ids,
            alternatives=tuple(reversed(first.alternatives)),
            unknowns=tuple(reversed(first.unknowns)),
            completeness=first.completeness,
            reproduction_id=first.reproduction_id,
            evidence_inventory_ids=tuple(
                reversed(first.evidence_inventory_ids)
            ),
            available_record_ids=first.available_record_ids,
            judgment=first.judgment,
        )
        self.assertEqual(
            build_case(first).case.id,
            build_case(second).case.id,
        )

    def test_missing_reference_is_rejected_exactly(self) -> None:
        current = request()
        available = (
            current.available_record_ids - {"assessment:one"}
        )
        with self.assertRaisesRegex(
            ValueError,
            "assessment:one",
        ):
            build_case(
                request(available_record_ids=available)
            )

    def test_inventory_must_close_evidence_references(self) -> None:
        current = request()
        broken = CaseConstructionRequest(
            question=current.question,
            subject_ids=current.subject_ids,
            observation_ids=current.observation_ids,
            interpretation_ids=current.interpretation_ids,
            obligation_ids=current.obligation_ids,
            evaluation_ids=current.evaluation_ids,
            assessment_ids=current.assessment_ids,
            supporting_evidence_ids=current.supporting_evidence_ids,
            counterevidence_ids=current.counterevidence_ids,
            alternatives=current.alternatives,
            unknowns=current.unknowns,
            completeness=current.completeness,
            reproduction_id=current.reproduction_id,
            evidence_inventory_ids=(
                "observation:one",
                "interpretation:one",
                "evidence:supporting",
            ),
            available_record_ids=current.available_record_ids,
        )
        with self.assertRaisesRegex(
            ValueError,
            "evidence:counter",
        ):
            build_case(broken)

    def test_support_and_counterevidence_roles_cannot_collapse(
        self,
    ) -> None:
        current = request()
        collapsed = CaseConstructionRequest(
            question=current.question,
            subject_ids=current.subject_ids,
            observation_ids=current.observation_ids,
            interpretation_ids=current.interpretation_ids,
            obligation_ids=current.obligation_ids,
            evaluation_ids=current.evaluation_ids,
            assessment_ids=current.assessment_ids,
            supporting_evidence_ids=("evidence:supporting",),
            counterevidence_ids=("evidence:supporting",),
            alternatives=current.alternatives,
            unknowns=current.unknowns,
            completeness=current.completeness,
            reproduction_id=current.reproduction_id,
            evidence_inventory_ids=current.evidence_inventory_ids,
            available_record_ids=current.available_record_ids,
        )
        with self.assertRaisesRegex(ValueError, "distinct roles"):
            build_case(collapsed)

    def test_unknowns_prevent_final_judgment(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "unresolved unknowns",
        ):
            build_case(request(judgment="true-regression"))

    def test_resolved_case_may_retain_explicit_judgment(self) -> None:
        result = build_case(
            request(
                unknowns=(),
                judgment="insufficient-evidence",
            )
        )
        self.assertFalse(result.unresolved)
        self.assertEqual(
            result.case.judgment,
            "insufficient-evidence",
        )


if __name__ == "__main__":
    unittest.main()
