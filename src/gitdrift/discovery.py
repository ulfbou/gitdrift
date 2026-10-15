"""Truthful capability discovery for the active composition."""

from .contracts import CapabilityDocument
from .version import CAPABILITY_SCHEMA_VERSION, NATIVE_SCHEMA_VERSION, __version__


def discover_capabilities() -> CapabilityDocument:
    """Return implemented capabilities only, with deferred boundaries explicit."""
    return CapabilityDocument(
        capability_schema_version=CAPABILITY_SCHEMA_VERSION,
        package_version=__version__,
        native_schema_versions=(NATIVE_SCHEMA_VERSION,),
        available_profiles=("state-awareness",),
        unavailable_profiles=("divergence", "file-lineage", "forensics"),
        available_operations=(
            "capability-discovery",
            "repository-acquisition",
            "state-comparison",
            "native-investigation-serialization",
        ),
        unavailable_operations=(
            "semantic-extraction",
            "obligation-evaluation",
            "case-construction",
            "ai-assessment",
            "sarif-export",
            "dx-export",
            "repository-mutation",
        ),
        output_formats=("capability-json",),
        limitations=(
            "State awareness executes repository acquisition, required "
            "state comparisons, and canonical native serialization.",
            "Semantic extraction, obligation evaluation, and case "
            "construction require explicit payload inputs and remain "
            "unavailable through this profile.",
        ),
    )
