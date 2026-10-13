import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "scripts"
    / "validation"
    / "validate.py"
)

SPEC = importlib.util.spec_from_file_location(
    "gitdrift_validation",
    SCRIPT,
)

assert SPEC
assert SPEC.loader

validation = importlib.util.module_from_spec(
    SPEC
)

sys.modules[SPEC.name] = validation
SPEC.loader.exec_module(validation)


class ValidationScriptTests(unittest.TestCase):
    def repository(
        self,
    ) -> tuple[
        tempfile.TemporaryDirectory[str],
        Path,
    ]:
        temporary = (
            tempfile.TemporaryDirectory()
        )
        root = Path(temporary.name)

        (
            root
            / "src"
            / "gitdrift"
            / "domain"
        ).mkdir(parents=True)

        (root / "tests").mkdir()
        (root / "scripts").mkdir()
        (root / "docs").mkdir()

        return temporary, root

    def test_compilation_reports_syntax_failure(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        (
            root
            / "src"
            / "gitdrift"
            / "broken.py"
        ).write_text(
            "def broken(:\n",
            encoding="utf-8",
        )

        with self.assertRaises(
            validation.ValidationFailure
        ):
            validation.compile_python(root)

    def test_domain_adapter_import_is_rejected(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        (
            root
            / "src"
            / "gitdrift"
            / "domain"
            / "bad.py"
        ).write_text(
            "from gitdrift.adapters "
            "import git\n",
            encoding="utf-8",
        )

        with self.assertRaises(
            validation.ValidationFailure
        ):
            validation.architectural_imports(
                root
            )

    def test_broken_relative_document_link_is_rejected(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        (
            root
            / "docs"
            / "README.md"
        ).write_text(
            "[missing](missing.md)\n",
            encoding="utf-8",
        )

        with self.assertRaises(
            validation.ValidationFailure
        ):
            validation.documentation_links(
                root
            )

    def test_existing_relative_document_link_passes(
        self,
    ) -> None:
        temporary, root = self.repository()
        self.addCleanup(temporary.cleanup)

        (
            root
            / "docs"
            / "target.md"
        ).write_text(
            "# Target\n",
            encoding="utf-8",
        )

        (
            root
            / "docs"
            / "README.md"
        ).write_text(
            "[target](target.md)\n",
            encoding="utf-8",
        )

        validation.documentation_links(root)


if __name__ == "__main__":
    unittest.main()
