import unittest

from gitdrift.domain import (
    RepositoryState,
    StateKind,
    canonical_bytes,
    stable_id,
)


class IdentityTests(unittest.TestCase):
    def test_mapping_and_set_order_do_not_change_identity(
        self,
    ) -> None:
        left = stable_id(
            "example",
            {"b": {"y", "x"}, "a": 1},
        )
        right = stable_id(
            "example",
            {"a": 1, "b": {"x", "y"}},
        )

        self.assertEqual(left, right)

    def test_comparison_direction_changes_identity(self) -> None:
        self.assertNotEqual(
            stable_id(
                "comparison",
                {"left": "a", "right": "b"},
            ),
            stable_id(
                "comparison",
                {"left": "b", "right": "a"},
            ),
        )

    def test_mutable_locator_does_not_control_state_identity(
        self,
    ) -> None:
        left = RepositoryState(
            StateKind.BRANCH_TIP,
            "repo",
            "commit:1",
            ("refs/heads/main",),
        )
        right = RepositoryState(
            StateKind.BRANCH_TIP,
            "repo",
            "commit:1",
            ("refs/heads/release",),
        )

        self.assertEqual(left.id, right.id)

    def test_exact_bytes_have_content_sensitive_canonical_form(
        self,
    ) -> None:
        self.assertNotEqual(
            canonical_bytes(b"a"),
            canonical_bytes(b"b"),
        )


if __name__ == "__main__":
    unittest.main()
