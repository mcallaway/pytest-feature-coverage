"""Integration tests for --feature-coverage-filter option."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def _write_two_feature_yaml(pytester) -> None:
    """Write two feature YAML files and a matching test file."""
    features_dir = pytester.mkdir('features')
    (features_dir / 'alpha.feature.yaml').write_text(
        'feature:\n'
        '  id: "001"\n'
        '  name: alpha-service\n'
        'components:\n'
        '  CORE:\n'
        '    name: Core logic\n'
        '    requirements:\n'
        '      1: Alpha does something\n'
        '      2: Alpha does something else\n'
    )
    (features_dir / 'beta.feature.yaml').write_text(
        'feature:\n'
        '  id: "002"\n'
        '  name: beta-service\n'
        'components:\n'
        '  CORE:\n'
        '    name: Core logic\n'
        '    requirements:\n'
        '      1: Beta does something\n'
    )
    pytester.makeini("""
        [pytest]
        feature_yaml_paths = features
    """)
    pytester.makepyfile("""
        import pytest

        @pytest.mark.req("alpha-service.CORE.1")
        def test_alpha():
            pass

        @pytest.mark.req("beta-service.CORE.1")
        def test_beta():
            pass
    """)


class TestHelpOutput:
    """COVERAGE_FILTER.7: option appears in --help."""

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.7')
    def test_filter_option_appears_in_help(self, pytester) -> None:
        """--feature-coverage-filter appears in pytest --help output."""
        result = pytester.runpytest('--help')
        result.stdout.fnmatch_lines(
            [
                '*--feature-coverage-filter*',
            ]
        )


class TestFilteredOutput:
    """COVERAGE_FILTER.1/2/5/8: filtered output for known fixture set."""

    @pytest.mark.req(
        'feature-coverage-plugin.COVERAGE_FILTER.1',
        'feature-coverage-plugin.COVERAGE_FILTER.2',
        'feature-coverage-plugin.COVERAGE_FILTER.8',
    )
    def test_filter_shows_only_matching_feature(self, pytester) -> None:
        """Filter to 'alpha' shows only alpha-service; Overall is scoped to it."""
        _write_two_feature_yaml(pytester)
        result = pytester.runpytest(
            '--feature-coverage',
            '--feature-coverage-filter',
            'alpha',
        )
        result.assert_outcomes(passed=2)
        result.stdout.fnmatch_lines(
            [
                '*Feature: alpha-service (001)*',
                '*Overall: 1/2 requirements covered (50.0%)*',
            ]
        )
        # beta-service must NOT appear
        assert 'beta-service' not in result.stdout.str()

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.5')
    def test_no_filter_shows_all_features(self, pytester) -> None:
        """Without filter all features appear (regression guard)."""
        _write_two_feature_yaml(pytester)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(passed=2)
        result.stdout.fnmatch_lines(
            [
                '*Feature: alpha-service (001)*',
                '*Feature: beta-service (002)*',
            ]
        )

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.9')
    def test_filter_matching_zero_features_produces_empty_report(
        self, pytester
    ) -> None:
        """Filter with no matches produces Overall: 0/0 and exits zero."""
        _write_two_feature_yaml(pytester)
        result = pytester.runpytest(
            '--feature-coverage',
            '--feature-coverage-filter',
            'nonexistent-xyz',
        )
        result.assert_outcomes(passed=2)
        result.stdout.fnmatch_lines(['*Overall: 0/0*'])
        assert result.ret == 0

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.3')
    def test_threshold_evaluated_against_filtered_percentage(self, pytester) -> None:
        """Threshold passes when filtered subset meets min even if full set does not."""
        _write_two_feature_yaml(pytester)
        # alpha: 1/2 covered; beta: 0/1 covered -- full set = 1/3 = 33%
        # filtered to alpha only: 1/2 = 50% -- above threshold of 40% -- must exit 0
        result = pytester.runpytest(
            '--feature-coverage',
            '--feature-coverage-filter',
            'alpha',
            '--feature-coverage-min',
            '40',
        )
        assert result.ret == 0

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.8')
    @pytest.mark.parametrize('fmt', ['json', 'markdown'])
    def test_filter_respected_by_non_text_reporters(self, pytester, fmt) -> None:
        """JSON and markdown reporters scope output to the filtered feature set."""
        _write_two_feature_yaml(pytester)
        result = pytester.runpytest(
            '--feature-coverage',
            '--feature-coverage-filter',
            'alpha',
            f'--feature-coverage-format={fmt}',
        )
        result.assert_outcomes(passed=2)
        assert 'alpha-service' in result.stdout.str()
        assert 'beta-service' not in result.stdout.str()

    @pytest.mark.req('feature-coverage-plugin.COVERAGE_FILTER.6')
    def test_orphan_checking_uses_full_feature_set(self, pytester) -> None:
        """A req() for a filtered-out feature is NOT an orphan."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'alpha.feature.yaml').write_text(
            'feature:\n'
            '  id: "001"\n'
            '  name: alpha-service\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: Alpha req\n'
        )
        (features_dir / 'beta.feature.yaml').write_text(
            'feature:\n'
            '  id: "002"\n'
            '  name: beta-service\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: Beta req\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        # test covers beta req but we filter to alpha only in the report
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("beta-service.CORE.1")
            def test_beta_req():
                pass
        """)
        result = pytester.runpytest(
            '--feature-coverage',
            '--feature-coverage-filter',
            'alpha',
            '-W',
            'all',
        )
        # beta-service.CORE.1 is valid (loaded from YAML); must NOT produce an orphan warning
        assert 'beta-service.CORE.1' not in result.stdout.str()
        # The warning message uses "does not match any known requirement" phrasing
        assert 'does not match any known requirement' not in result.stdout.str()
