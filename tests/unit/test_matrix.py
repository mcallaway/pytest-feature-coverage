"""Unit tests for coverage matrix computation."""

from __future__ import annotations


class TestCoverageMatrix:
    """T022: Unit tests for matrix computation."""

    def test_covered_requirement(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='001', name='app'),
            components={'CORE': ComponentModel(name='Core', requirements={1: 'Desc'})},
        )
        req_map = {'app.CORE.1': ['test.py::test_one']}
        report = compute_coverage([feature], req_map)

        assert report.total_requirements == 1
        assert report.covered_requirements == 1
        assert report.coverage_percentage == 100.0

    def test_uncovered_requirement(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='001', name='app'),
            components={
                'CORE': ComponentModel(
                    name='Core', requirements={1: 'Desc', 2: 'Other'}
                )
            },
        )
        req_map = {'app.CORE.1': ['test.py::test_one']}
        report = compute_coverage([feature], req_map)

        assert report.total_requirements == 2
        assert report.covered_requirements == 1
        assert report.coverage_percentage == 50.0

    def test_zero_req_component_excluded(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='001', name='app'),
            components={
                'CORE': ComponentModel(name='Core', requirements={1: 'Desc'}),
                'EMPTY': ComponentModel(name='Empty', requirements={}),
            },
        )
        req_map = {'app.CORE.1': ['test.py::test_one']}
        report = compute_coverage([feature], req_map)

        # EMPTY component doesn't count toward total
        assert report.total_requirements == 1
        assert report.coverage_percentage == 100.0

    def test_many_to_many(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
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
        # Multiple tests cover same req; one test covers multiple reqs
        req_map = {
            'app.CORE.1': ['test.py::t1', 'test.py::t2'],
            'app.CORE.2': ['test.py::t1'],
        }
        report = compute_coverage([feature], req_map)

        assert report.total_requirements == 2
        assert report.covered_requirements == 2
        assert report.entries['app.CORE.1'].covering_tests == [
            'test.py::t1',
            'test.py::t2',
        ]

    def test_empty_features(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage

        report = compute_coverage([], {})
        assert report.total_requirements == 0
        assert report.coverage_percentage == 0.0

    def test_deterministic_ordering(self) -> None:
        from pytest_feature_coverage.matrix import compute_coverage
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        # Features should be sorted by name
        feat_b = FeatureFileModel(
            feature=FeatureModel(id='2', name='bravo'),
            components={'Z': ComponentModel(name='Z', requirements={1: 'z'})},
        )
        feat_a = FeatureFileModel(
            feature=FeatureModel(id='1', name='alpha'),
            components={'A': ComponentModel(name='A', requirements={1: 'a'})},
        )
        report = compute_coverage([feat_b, feat_a], {})
        assert report.features[0].feature.name == 'alpha'
        assert report.features[1].feature.name == 'bravo'
