"""Markdown format coverage reporter (FR-009)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..matrix import CoverageReport


def render_markdown(report: CoverageReport) -> str:
    """Render coverage report as Markdown string."""
    lines: list[str] = []
    lines.append('# Feature Coverage Report')
    lines.append('')

    summary_rows: list[tuple[str, int, int, float]] = []

    for feature_file in report.features:
        feat = feature_file.feature
        lines.append(f'## {feat.name} ({feat.id})')
        lines.append('')

        feat_total = 0
        feat_covered = 0

        for comp_key in sorted(feature_file.components):
            comp = feature_file.components[comp_key]
            if not comp.requirements:
                continue

            lines.append(f'### {comp_key}')
            lines.append('')
            lines.append('| # | Requirement | Status | Tests |')
            lines.append('|---|-------------|--------|-------|')

            for num in sorted(comp.requirements):
                composite_id = f'{feat.name}.{comp_key}.{num}'
                entry = report.entries[composite_id]
                feat_total += 1
                if entry.is_covered:
                    feat_covered += 1
                    status = '\u2713'
                    tests = ', '.join(f'`{t}`' for t in entry.covering_tests)
                else:
                    status = '\u2717'
                    tests = '\u2014'
                lines.append(f'| {num} | {entry.description} | {status} | {tests} |')

            lines.append('')

        pct = (feat_covered / feat_total * 100) if feat_total > 0 else 0.0
        summary_rows.append((feat.name, feat_covered, feat_total, pct))

    # Summary table
    lines.append('### Summary')
    lines.append('')
    lines.append('| Feature | Covered | Total | % |')
    lines.append('|---------|---------|-------|---|')
    for name, covered, total, pct in summary_rows:
        lines.append(f'| {name} | {covered} | {total} | {pct:.1f}% |')
    lines.append(
        f'| **Overall** | **{report.covered_requirements}** '
        f'| **{report.total_requirements}** '
        f'| **{report.coverage_percentage:.1f}%** |'
    )

    return '\n'.join(lines)
