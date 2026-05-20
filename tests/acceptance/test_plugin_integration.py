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


class TestReqMarkersCollected:
    """T020: req() markers collected and associated correctly."""

    def test_markers_are_collected(self, pytester):
        """req() markers map tests to requirements."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'app.feature.yaml').write_text(
            'feature:\n'
            "  id: '001'\n"
            '  name: app\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: First requirement\n'
            '      2: Second requirement\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_first():
                pass

            @pytest.mark.req("app.CORE.2")
            def test_second():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(passed=2)


class TestOrphanMarkerWarning:
    """T021: Orphan marker emits warning."""

    def test_orphan_marker_warns(self, pytester):
        """Orphan req() emits warning by default."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'app.feature.yaml').write_text(
            'feature:\n'
            "  id: '001'\n"
            '  name: app\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: First requirement\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.99")
            def test_orphan():
                pass
        """)
        result = pytester.runpytest('--feature-coverage', '-W', 'all')
        result.assert_outcomes(passed=1)
        result.stdout.fnmatch_lines(['*app.CORE.99*'])

    def test_orphan_marker_strict_errors(self, pytester):
        """Orphan req() errors in strict mode."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'app.feature.yaml').write_text(
            'feature:\n'
            "  id: '001'\n"
            '  name: app\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: First requirement\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
            feature_coverage_strict = true
        """)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.99")
            def test_orphan():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.stderr.fnmatch_lines(['*orphan*app.CORE.99*'])


class TestTextReport:
    """T027: Full text report output matches expected format."""

    def test_text_report_output(self, pytester):
        """Full end-to-end text report with covered and uncovered reqs."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'app.feature.yaml').write_text(
            'feature:\n'
            "  id: '001'\n"
            '  name: app\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: First requirement\n'
            '      2: Second requirement\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_covers_first():
                pass
        """)
        result = pytester.runpytest('--feature-coverage', '-v')
        result.assert_outcomes(passed=1)
        result.stdout.fnmatch_lines(
            [
                '*Feature Coverage*',
                '*Feature: app (001)*',
                '*CORE*',
                '*1: First requirement*',
                '*2: Second requirement*',
                '*Coverage: 1/2 (50.0%)*',
                '*Overall: 1/2 requirements covered (50.0%)*',
            ]
        )


class TestDeterminism:
    """T028: Determinism — identical output on repeated runs."""

    def test_deterministic_output(self, pytester):
        """Two runs produce identical coverage section output."""
        features_dir = pytester.mkdir('features')
        (features_dir / 'app.feature.yaml').write_text(
            'feature:\n'
            "  id: '001'\n"
            '  name: app\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: A\n'
            '      2: B\n'
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
        result1 = pytester.runpytest('--feature-coverage')
        result2 = pytester.runpytest('--feature-coverage')

        def extract_coverage_section(lines):
            start = None
            for i, line in enumerate(lines):
                if 'Feature Coverage' in line:
                    start = i
                    break
            if start is None:
                return []
            # Take lines after the header until the next separator or end
            section = []
            for line in lines[start + 1 :]:
                if line.startswith('===='):
                    break
                section.append(line)
            return section

        section1 = extract_coverage_section(result1.stdout.lines)
        section2 = extract_coverage_section(result2.stdout.lines)
        assert section1 == section2
        assert len(section1) > 0


class TestNoYAMLFilesFound:
    """T029: No YAML files found emits clear message."""

    def test_empty_directory_no_error(self, pytester):
        """Empty features directory produces report with 0/0."""
        pytester.mkdir('features')
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
        result.stdout.fnmatch_lines(['*Overall: 0/0*'])


class TestJSONOutput:
    """T038: JSON output is valid and matches contract."""

    def test_json_output(self, pytester):
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
        result = pytester.runpytest(
            '--feature-coverage', '--feature-coverage-format=json'
        )
        result.assert_outcomes(passed=1)
        # Find JSON in output
        import json

        stdout = '\n'.join(result.stdout.lines)
        # Extract JSON block (starts with {)
        start = stdout.index('{')
        end = stdout.rindex('}') + 1
        data = json.loads(stdout[start:end])
        assert data['overall']['covered'] == 1
        assert data['overall']['total'] == 1
        assert data['features'][0]['name'] == 'app'


class TestMarkdownOutput:
    """T039: Markdown output matches contract format."""

    def test_markdown_output(self, pytester):
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
        result = pytester.runpytest(
            '--feature-coverage', '--feature-coverage-format=markdown'
        )
        result.assert_outcomes(passed=1)
        result.stdout.fnmatch_lines(
            [
                '*# Feature Coverage Report*',
                '*## app (001)*',
                '*### CORE*',
                '*| 1 | First |*',
                '*| **Overall** |*',
            ]
        )


class TestConfigResolution:
    """T040: INI option precedence — config defaults, CLI overrides."""

    def test_ini_format_default(self, pytester):
        """INI feature_coverage_format is used when CLI not provided."""
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
            feature_coverage_format = json
        """)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_one():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(passed=1)
        # JSON output should be present
        stdout = '\n'.join(result.stdout.lines)
        assert '"features"' in stdout

    def test_cli_overrides_ini(self, pytester):
        """CLI --feature-coverage-format overrides INI setting."""
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
            feature_coverage_format = json
        """)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_one():
                pass
        """)
        result = pytester.runpytest(
            '--feature-coverage', '--feature-coverage-format=text'
        )
        result.assert_outcomes(passed=1)
        result.stdout.fnmatch_lines(['*Feature: app (001)*'])

    def test_ini_min_threshold(self, pytester):
        """INI feature_coverage_min is used when CLI not provided."""
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
            feature_coverage_min = 100
        """)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_one():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        assert result.ret != 0
        result.stdout.fnmatch_lines(['*below minimum*'])
