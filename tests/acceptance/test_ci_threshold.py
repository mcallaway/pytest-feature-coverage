"""Acceptance tests for CI coverage threshold (US4)."""

from __future__ import annotations


class TestCIThreshold:
    """T030: Acceptance tests for threshold behavior."""

    def test_below_threshold_fails(self, pytester):
        """Exit non-zero when coverage is below minimum."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'app.feature.yaml').write_text(
            'feature:\n'
            "  id: '001'\n"
            '  name: app\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: First\n'
            '      2: Second\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_one():
                pass
        """)
        result = pytester.runpytest('--feature-coverage', '--feature-coverage-min=100')
        assert result.ret != 0
        result.stdout.fnmatch_lines(['*below minimum*'])

    def test_above_threshold_passes(self, pytester):
        """Exit zero when coverage meets minimum."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'app.feature.yaml').write_text(
            'feature:\n'
            "  id: '001'\n"
            '  name: app\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: First\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_one():
                pass
        """)
        result = pytester.runpytest('--feature-coverage', '--feature-coverage-min=100')
        result.assert_outcomes(passed=1)
        assert result.ret == 0

    def test_zero_threshold_default(self, pytester):
        """Default threshold of 0 never fails."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'app.feature.yaml').write_text(
            'feature:\n'
            "  id: '001'\n"
            '  name: app\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: First\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        pytester.makepyfile("""
            def test_no_req():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(passed=1)
        assert result.ret == 0
