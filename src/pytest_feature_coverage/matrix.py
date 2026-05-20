"""Coverage matrix computation (FR-005)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schema import FeatureFileModel


@dataclass
class CoverageEntry:
    """A single requirement's coverage status."""

    composite_id: str
    number: int
    description: str
    covering_tests: list[str] = field(default_factory=list)

    @property
    def is_covered(self) -> bool:
        return len(self.covering_tests) > 0


@dataclass
class CoverageReport:
    """Complete coverage computation result."""

    features: list[FeatureFileModel]
    entries: dict[str, CoverageEntry]
    total_requirements: int
    covered_requirements: int
    orphan_markers: list[str] = field(default_factory=list)

    @property
    def coverage_percentage(self) -> float:
        if self.total_requirements == 0:
            return 0.0
        return (self.covered_requirements / self.total_requirements) * 100


def compute_coverage(
    features: list[FeatureFileModel],
    req_map: dict[str, list[str]],
) -> CoverageReport:
    """Compute the coverage matrix from loaded features and scanned markers."""
    # Sort features alphabetically by name for determinism
    sorted_features = sorted(features, key=lambda f: f.feature.name)

    entries: dict[str, CoverageEntry] = {}
    total = 0

    for feature_file in sorted_features:
        name = feature_file.feature.name
        for comp_key in sorted(feature_file.components):
            comp = feature_file.components[comp_key]
            for num in sorted(comp.requirements):
                composite_id = f'{name}.{comp_key}.{num}'
                covering = req_map.get(composite_id, [])
                entries[composite_id] = CoverageEntry(
                    composite_id=composite_id,
                    number=num,
                    description=comp.requirements[num],
                    covering_tests=covering,
                )
                total += 1

    covered = sum(1 for e in entries.values() if e.is_covered)

    return CoverageReport(
        features=sorted_features,
        entries=entries,
        total_requirements=total,
        covered_requirements=covered,
    )
