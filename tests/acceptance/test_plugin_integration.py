"""Acceptance tests for plugin integration using pytester."""

from __future__ import annotations


class TestValidYAMLLoads:
    """T013: Valid YAML loads without error."""

    def test_valid_yaml_loads_and_plugin_activates(self, pytester):
        """Plugin activates and loads valid YAML without errors."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'myfeature.feature.yaml').write_text(
            'feature:\n'
            '  id: "001"\n'
            '  name: my-feature\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core logic\n'
            '    requirements:\n'
            '      1: Does something\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        pytester.makepyfile("""
            def test_placeholder():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(passed=1)


class TestInvalidYAMLFailsCollection:
    """T014: Invalid YAML fails collection with clear error."""

    def test_invalid_yaml_schema_fails(self, pytester):
        """Invalid schema produces UsageError mentioning the file."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'bad.feature.yaml').write_text(
            'feature:\n  id: "001"\n  # missing name field\ncomponents: {}\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        pytester.makepyfile("""
            def test_placeholder():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.stderr.fnmatch_lines(['*ERROR*bad.feature.yaml*'])

    def test_malformed_yaml_fails(self, pytester):
        """Malformed YAML syntax produces clear error."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'broken.feature.yaml').write_text(': [[[invalid yaml')
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        pytester.makepyfile("""
            def test_placeholder():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.stderr.fnmatch_lines(['*ERROR*broken.feature.yaml*'])


class TestMissingConfig:
    """T015: Missing feature_yaml_paths config emits error."""

    def test_missing_feature_yaml_paths_errors(self, pytester):
        """Plugin errors when feature_yaml_paths is not configured."""
        pytester.makepyfile("""
            def test_placeholder():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.stderr.fnmatch_lines(['*feature_yaml_paths*'])

    def test_plugin_inactive_without_flag(self, pytester):
        """Plugin is inert when --feature-coverage is not passed."""
        pytester.makepyfile("""
            def test_placeholder():
                pass
        """)
        # No --feature-coverage flag, no config needed
        result = pytester.runpytest()
        result.assert_outcomes(passed=1)
