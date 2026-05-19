"""Unit tests for reporters."""

from __future__ import annotations


class TestTextReporter:
    """T023: Unit tests for text reporter output format."""

    def test_covered_requirement_shows_checkmark(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.reporters.text import render_text
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='001', name='app'),
            components={
                'CORE': ComponentModel(name='Core', requirements={1: 'Does thing'})
            },
        )
        report = compute_coverage([feature], {'app.CORE.1': ['test.py::test_one']})
        lines = render_text(report)
        text = '\n'.join(lines)

        assert '\u2713 1: Does thing' in text
        assert 'test.py::test_one' in text

    def test_uncovered_requirement_shows_x(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.reporters.text import render_text
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='001', name='app'),
            components={
                'CORE': ComponentModel(name='Core', requirements={1: 'Does thing'})
            },
        )
        report = compute_coverage([feature], {})
        lines = render_text(report)
        text = '\n'.join(lines)

        assert '\u2717 1: Does thing' in text
        assert '(no covering test)' in text

    def test_overall_line(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.reporters.text import render_text
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='001', name='app'),
            components={
                'CORE': ComponentModel(name='Core', requirements={1: 'A', 2: 'B'})
            },
        )
        report = compute_coverage([feature], {'app.CORE.1': ['t.py::t1']})
        lines = render_text(report)
        text = '\n'.join(lines)

        assert 'Overall: 1/2 requirements covered (50.0%)' in text

    def test_feature_header(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.reporters.text import render_text
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='042', name='my-feature'),
            components={'X': ComponentModel(name='X', requirements={1: 'y'})},
        )
        report = compute_coverage([feature], {})
        lines = render_text(report)

        assert 'Feature: my-feature (042)' in lines
