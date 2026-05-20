"""JSON format coverage reporter (FR-012)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..matrix import CoverageReport


def render_json(report: CoverageReport) -> str:
    """Render coverage report as JSON string."""
    features_out = []

    for feature_file in report.features:
        feat = feature_file.feature
        components_out = []

        for comp_key in sorted(feature_file.components):
            comp = feature_file.components[comp_key]
            reqs_out = []
            for num in sorted(comp.requirements):
                composite_id = f'{feat.name}.{comp_key}.{num}'
                entry = report.entries.get(composite_id)
                reqs_out.append(
                    {
                        'number': num,
                        'description': comp.requirements[num],
                        'composite_id': composite_id,
                        'covered': entry.is_covered if entry else False,
                        'covering_tests': entry.covering_tests if entry else [],
                    }
                )

            components_out.append(
                {
                    'key': comp_key,
                    'name': comp.name,
                    'requirements': reqs_out,
                }
            )

        # Compute per-feature coverage
        feat_total = sum(len(c.requirements) for c in feature_file.components.values())
        feat_covered = sum(
            1
            for c_key, c in feature_file.components.items()
            for n in c.requirements
            if report.entries.get(f'{feat.name}.{c_key}.{n}', None)
            and report.entries[f'{feat.name}.{c_key}.{n}'].is_covered
        )
        feat_pct = (feat_covered / feat_total * 100) if feat_total > 0 else 0.0

        features_out.append(
            {
                'id': feat.id,
                'name': feat.name,
                'components': components_out,
                'coverage': {
                    'covered': feat_covered,
                    'total': feat_total,
                    'percentage': round(feat_pct, 1),
                },
            }
        )

    output = {
        'features': features_out,
        'overall': {
            'covered': report.covered_requirements,
            'total': report.total_requirements,
            'percentage': round(report.coverage_percentage, 1),
        },
        'orphan_markers': report.orphan_markers,
    }

    return json.dumps(output, indent=2)
