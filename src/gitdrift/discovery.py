"""Truthful capability discovery for the active composition."""

from .contracts import CapabilityDocument
from .version import CAPABILITY_SCHEMA_VERSION, NATIVE_SCHEMA_VERSION, __version__


def discover_capabilities() -> CapabilityDocument:
    """Return implemented capabilities only, with deferred boundaries explicit."""
    return CapabilityDocument(
        capability_schema_version=CAPABILITY_SCHEMA_VERSION,
        package_version=__version__,
        native_schema_versions=(NATIVE_SCHEMA_VERSION,),
        available_profiles=(),
        unavailable_profiles=("state-awareness", "divergence", "file-lineage", "forensics"),
        available_operations=("capability-discovery",),
        unavailable_operations=(
            "repository-acquisition",
            "state-comparison",
            "semantic-extraction",
            "obligation-evaluation",
            "case-construction",
            "native-investigation-serialization",
            "ai-assessment",
            "sarif-export",
            "dx-export",
            "repository-mutation",
        ),
        output_formats=("capability-json",),
        limitations=(
            "Development skeleton only; no analytical profile is executable.",
            "The declared native schema identity has no investigation schema resource yet.",
        ),
    )
