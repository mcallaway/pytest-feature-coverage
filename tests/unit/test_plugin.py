"""Unit tests for plugin helper functions."""

from __future__ import annotations

import types

import pytest


_PLUGIN_ACTIVE_ATTR = '_feature_coverage_active'
_PLUGIN_STATE_ATTR = '_feature_coverage_state'


class TestIsActive:
    """Tests for _is_active."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_REPORT.1')
    def test_returns_true_when_flag_set(self) -> None:
        from pytest_feature_coverage.plugin import _is_active

        config = types.SimpleNamespace()
        setattr(config, _PLUGIN_ACTIVE_ATTR, True)
        assert _is_active(config) is True

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_REPORT.1')
    def test_returns_false_when_flag_absent(self) -> None:
        from pytest_feature_coverage.plugin import _is_active

        assert _is_active(types.SimpleNamespace()) is False


class TestGetThreshold:
    """Tests for _get_threshold."""

    @pytest.mark.req('feature-coverage-plugin.CI_THRESHOLD.1')
    def test_returns_cli_value_when_provided(self) -> None:
        from pytest_feature_coverage.plugin import _get_threshold

        config = types.SimpleNamespace()
        config.getoption = lambda *_a, **_kw: 80
        assert _get_threshold(config) == 80

    @pytest.mark.req('feature-coverage-plugin.CI_THRESHOLD.2')
    def test_falls_back_to_ini_when_cli_absent(self) -> None:
        from pytest_feature_coverage.plugin import _get_threshold

        config = types.SimpleNamespace()
        config.getoption = lambda *_a, **_kw: None
        config.getini = lambda *_a, **_kw: '75'
        assert _get_threshold(config) == 75


class TestGetKnownRequirementIds:
    """Tests for _get_known_requirement_ids."""

    @pytest.mark.req('feature-coverage-plugin.REQ_MARKER.3')
    def test_builds_ids_from_loaded_features(self) -> None:
        from pytest_feature_coverage.plugin import _get_known_requirement_ids
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
        config = types.SimpleNamespace()
        setattr(config, _PLUGIN_STATE_ATTR, {'features': [feature]})
        assert _get_known_requirement_ids(config) == {'app.CORE.1', 'app.CORE.2'}

    @pytest.mark.req('feature-coverage-plugin.REQ_MARKER.3')
    def test_returns_empty_set_when_no_state(self) -> None:
        from pytest_feature_coverage.plugin import _get_known_requirement_ids

        assert _get_known_requirement_ids(types.SimpleNamespace()) == set()

    @pytest.mark.req('feature-coverage-plugin.REQ_MARKER.3')
    def test_accumulates_ids_from_multiple_features(self) -> None:
        from pytest_feature_coverage.plugin import _get_known_requirement_ids
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        features = [
            FeatureFileModel(
                feature=FeatureModel(id='001', name='alpha'),
                components={'A': ComponentModel(name='A', requirements={1: 'x'})},
            ),
            FeatureFileModel(
                feature=FeatureModel(id='002', name='beta'),
                components={
                    'B': ComponentModel(name='B', requirements={1: 'y', 2: 'z'})
                },
            ),
        ]
        config = types.SimpleNamespace()
        setattr(config, _PLUGIN_STATE_ATTR, {'features': features})
        assert _get_known_requirement_ids(config) == {
            'alpha.A.1',
            'beta.B.1',
            'beta.B.2',
        }


class TestComputeAndStoreReport:
    """Tests for _compute_and_store_report."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_REPORT.1')
    def test_computes_and_stores_report(self) -> None:
        from pytest_feature_coverage.plugin import _compute_and_store_report
        from pytest_feature_coverage.schema import (
            ComponentModel,
            FeatureFileModel,
            FeatureModel,
        )

        feature = FeatureFileModel(
            feature=FeatureModel(id='001', name='app'),
            components={'CORE': ComponentModel(name='Core', requirements={1: 'Desc'})},
        )
        state: dict = {
            'features': [feature],
            'req_map': {'app.CORE.1': ['t.py::t']},
            'orphans': ['some.orphan.1'],
        }
        config = types.SimpleNamespace()
        setattr(config, _PLUGIN_STATE_ATTR, state)
        _compute_and_store_report(config)
        assert state['report'].covered_requirements == 1
        assert state['report'].orphan_markers == ['some.orphan.1']

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_REPORT.1')
    def test_skips_recomputation_when_report_already_present(self) -> None:
        from pytest_feature_coverage.plugin import _compute_and_store_report

        sentinel = object()
        state: dict = {'features': [], 'report': sentinel}
        config = types.SimpleNamespace()
        setattr(config, _PLUGIN_STATE_ATTR, state)
        _compute_and_store_report(config)
        assert state['report'] is sentinel
