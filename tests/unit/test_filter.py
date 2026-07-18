"""Unit tests for --feature-coverage-filter option."""

from __future__ import annotations

import types

import pytest

from pytest_feature_coverage.plugin import _compute_and_store_report
from pytest_feature_coverage.schema import (
    ComponentModel,
    FeatureFileModel,
    FeatureModel,
)


_PLUGIN_STATE_ATTR = '_feature_coverage_state'


def _make_feature(name: str, feature_id: str = '001') -> FeatureFileModel:
    return FeatureFileModel(
        feature=FeatureModel(id=feature_id, name=name),
        components={
            'CORE': ComponentModel(name='Core', requirements={1: 'A', 2: 'B'}),
        },
    )


def _make_config(
    features: list[FeatureFileModel], filters: list[str] | None
) -> types.SimpleNamespace:
    config = types.SimpleNamespace()
    config.getoption = lambda opt, **_kw: (
        filters if opt == '--feature-coverage-filter' else None
    )
    setattr(
        config, _PLUGIN_STATE_ATTR, {'features': features, 'req_map': {}, 'orphans': []}
    )
    return config


class TestSingleFilter:
    """COVERAGE_FILTER.1: substring filter narrows the report."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.1')
    def test_single_filter_shows_only_matching_feature(self) -> None:
        alpha = _make_feature('alpha')
        beta = _make_feature('beta', '002')
        config = _make_config([alpha, beta], ['alpha'])
        _compute_and_store_report(config)
        report = getattr(config, _PLUGIN_STATE_ATTR)['report']
        assert len(report.features) == 1
        assert report.features[0].feature.name == 'alpha'

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.1')
    def test_substring_match_shows_all_features_containing_substring(self) -> None:
        jinja = _make_feature('jinja-template-adapter')
        jinja_ext = _make_feature('jinja-extra', '002')
        bigquery = _make_feature('bigquery-domain-view', '003')
        config = _make_config([jinja, jinja_ext, bigquery], ['jinja'])
        _compute_and_store_report(config)
        report = getattr(config, _PLUGIN_STATE_ATTR)['report']
        names = {f.feature.name for f in report.features}
        assert names == {'jinja-template-adapter', 'jinja-extra'}


class TestMultipleFilters:
    """COVERAGE_FILTER.4: multiple filters combine as OR."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.4')
    def test_multiple_filters_are_combined_as_or(self) -> None:
        alpha = _make_feature('alpha')
        beta = _make_feature('beta', '002')
        gamma = _make_feature('gamma', '003')
        config = _make_config([alpha, beta, gamma], ['alpha', 'beta'])
        _compute_and_store_report(config)
        report = getattr(config, _PLUGIN_STATE_ATTR)['report']
        names = {f.feature.name for f in report.features}
        assert names == {'alpha', 'beta'}


class TestCaseInsensitiveMatch:
    """COVERAGE_FILTER.1: matching is case-insensitive."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.1')
    def test_filter_is_case_insensitive(self) -> None:
        feature = _make_feature('Jinja-Template-Adapter')
        other = _make_feature('bigquery', '002')
        config = _make_config([feature, other], ['JINJA'])
        _compute_and_store_report(config)
        report = getattr(config, _PLUGIN_STATE_ATTR)['report']
        assert len(report.features) == 1
        assert report.features[0].feature.name == 'Jinja-Template-Adapter'


class TestZeroMatchFilter:
    """COVERAGE_FILTER.9: 0 matching features produces empty report."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.9')
    def test_filter_matching_zero_features_gives_empty_report(self) -> None:
        alpha = _make_feature('alpha')
        config = _make_config([alpha], ['xyz-no-match'])
        _compute_and_store_report(config)
        report = getattr(config, _PLUGIN_STATE_ATTR)['report']
        assert report.features == []
        assert report.total_requirements == 0
        assert report.covered_requirements == 0
        assert report.coverage_percentage == 0.0


class TestNoFilter:
    """COVERAGE_FILTER.5: no filter shows all features (regression guard)."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.5')
    def test_no_filter_shows_all_features(self) -> None:
        alpha = _make_feature('alpha')
        beta = _make_feature('beta', '002')
        config = _make_config([alpha, beta], None)
        _compute_and_store_report(config)
        report = getattr(config, _PLUGIN_STATE_ATTR)['report']
        assert len(report.features) == 2


class TestFilteredOverallPercentage:
    """COVERAGE_FILTER.2: Overall counts only filtered features' requirements."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.2')
    def test_overall_percentage_uses_only_filtered_features_requirements(self) -> None:
        # alpha: 2 reqs, 1 covered -- filtered in
        alpha = _make_feature('alpha')
        # beta: 2 reqs, 0 covered -- filtered out
        beta = _make_feature('beta', '002')
        req_map = {'alpha.CORE.1': ['test.py::test_a']}
        config = types.SimpleNamespace()
        config.getoption = lambda opt, **_kw: (
            ['alpha'] if opt == '--feature-coverage-filter' else None
        )
        setattr(
            config,
            _PLUGIN_STATE_ATTR,
            {
                'features': [alpha, beta],
                'req_map': req_map,
                'orphans': [],
            },
        )
        _compute_and_store_report(config)
        report = getattr(config, _PLUGIN_STATE_ATTR)['report']
        # Only alpha's 2 reqs are counted; 1 of 2 covered = 50%
        assert report.total_requirements == 2
        assert report.covered_requirements == 1
        assert report.coverage_percentage == 50.0


class TestOrphansUnaffectedByFilter:
    """COVERAGE_FILTER.6: orphan detection uses the full feature set."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.6')
    def test_orphan_markers_preserved_when_filter_active(self) -> None:
        alpha = _make_feature('alpha')
        beta = _make_feature('beta', '002')
        config = types.SimpleNamespace()
        config.getoption = lambda opt, **_kw: (
            ['alpha'] if opt == '--feature-coverage-filter' else None
        )
        setattr(
            config,
            _PLUGIN_STATE_ATTR,
            {
                'features': [alpha, beta],
                'req_map': {},
                'orphans': ['nonexistent.COMP.1'],
            },
        )
        _compute_and_store_report(config)
        report = getattr(config, _PLUGIN_STATE_ATTR)['report']
        # orphan_markers must be preserved regardless of filter
        assert report.orphan_markers == ['nonexistent.COMP.1']
        # filter still applies to feature output
        assert len(report.features) == 1
        assert report.features[0].feature.name == 'alpha'


class TestThresholdAgainstFilteredPercentage:
    """COVERAGE_FILTER.3: --feature-coverage-min evaluated against filtered Overall."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.3')
    def test_filtered_overall_is_used_for_threshold(self) -> None:
        # Verify the report percentage reflects only the filtered subset,
        # so the caller (_get_threshold / pytest_sessionfinish) gets the right value.
        alpha = _make_feature('alpha')
        beta = _make_feature('beta', '002')
        req_map = {
            'alpha.CORE.1': ['t::a'],
            'alpha.CORE.2': ['t::b'],
            'beta.CORE.1': ['t::c'],
            'beta.CORE.2': ['t::d'],
        }
        # filter to alpha only; 2/2 = 100%
        config = types.SimpleNamespace()
        config.getoption = lambda opt, **_kw: (
            ['alpha'] if opt == '--feature-coverage-filter' else None
        )
        setattr(
            config,
            _PLUGIN_STATE_ATTR,
            {
                'features': [alpha, beta],
                'req_map': req_map,
                'orphans': [],
            },
        )
        _compute_and_store_report(config)
        report = getattr(config, _PLUGIN_STATE_ATTR)['report']
        assert report.coverage_percentage == 100.0
        assert report.total_requirements == 2  # only alpha's reqs
