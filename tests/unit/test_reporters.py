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


class TestJsonReporter:
    """T033: Unit tests for JSON reporter."""

    def test_json_structure(self) -> None:
        import json

        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.reporters.json import render_json
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='001', name='app'),
            components={
                'CORE': ComponentModel(
                    name='Core', requirements={1: 'First', 2: 'Second'}
                )
            },
        )
        report = compute_coverage([feature], {'app.CORE.1': ['test.py::t1']})
        data = json.loads(render_json(report))

        assert 'features' in data
        assert 'overall' in data
        assert 'orphan_markers' in data
        assert data['overall'] == {'covered': 1, 'total': 2, 'percentage': 50.0}
        assert data['features'][0]['name'] == 'app'
        assert data['features'][0]['components'][0]['key'] == 'CORE'
        req = data['features'][0]['components'][0]['requirements'][0]
        assert req['composite_id'] == 'app.CORE.1'
        assert req['covered'] is True
        assert req['covering_tests'] == ['test.py::t1']


class TestMarkdownReporter:
    """T034: Unit tests for Markdown reporter."""

    def test_markdown_structure(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.reporters.markdown import render_markdown
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='001', name='app'),
            components={
                'CORE': ComponentModel(
                    name='Core', requirements={1: 'First', 2: 'Second'}
                )
            },
        )
        report = compute_coverage([feature], {'app.CORE.1': ['test.py::t1']})
        md = render_markdown(report)

        assert '# Feature Coverage Report' in md
        assert '## app (001)' in md
        assert '### CORE' in md
        assert '| 1 | First | \u2713 |' in md
        assert '| 2 | Second | \u2717 |' in md
        assert '| **Overall** |' in md
