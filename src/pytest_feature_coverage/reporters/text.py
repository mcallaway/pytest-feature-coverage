"""Text format coverage reporter (FR-007)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..matrix import CoverageReport


def render_text(report: CoverageReport) -> list[str]:
    """Render coverage report as text lines."""
    lines: list[str] = []

    for feature_file in report.features:
        feat = feature_file.feature
        lines.append(f'Feature: {feat.name} ({feat.id})')

        feat_total = 0
        feat_covered = 0

        for comp_key in sorted(feature_file.components):
            comp = feature_file.components[comp_key]
            if not comp.requirements:
                lines.append(f'  {comp_key}')
                lines.append('    (no requirements)')
                continue

            lines.append(f'  {comp_key}')
            for num in sorted(comp.requirements):
                composite_id = f'{feat.name}.{comp_key}.{num}'
                entry = report.entries[composite_id]
                feat_total += 1
                if entry.is_covered:
                    feat_covered += 1
                    lines.append(f'    \u2713 {num}: {entry.description}')
                    for test_id in entry.covering_tests:
                        lines.append(f'         \u2192 {test_id}')
                else:
                    lines.append(f'    \u2717 {num}: {entry.description}')
                    lines.append('         \u2192 (no covering test)')

        if feat_total > 0:
            pct = (feat_covered / feat_total) * 100
            lines.append(f'  Coverage: {feat_covered}/{feat_total} ({pct:.1f}%)')
        else:
            lines.append('  Coverage: 0/0 (N/A)')
        lines.append('')

    if report.total_requirements > 0:
        lines.append(
            f'Overall: {report.covered_requirements}/{report.total_requirements} '
            f'requirements covered ({report.coverage_percentage:.1f}%)'
        )
    else:
        lines.append('Overall: 0/0 requirements covered (0.0%)')

    return lines
