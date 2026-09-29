"""Acceptance tests: execution-aware feature coverage (see ADR-006).

A requirement is covered only when at least one associated test achieves a
clean pass (call phase ``outcome == "passed"`` with no ``wasxfail``, and no
phase reported ``outcome == "failed"``). These tests must fail against the
pre-fix, collection-only implementation (which grants coverage from mere
collection-time req() association, regardless of outcome) and pass once
the outcome-tracking mechanism is wired in.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration

_SINGLE_REQ_FEATURE_YAML = (
    'feature:\n'
    "  id: '001'\n"
    '  name: app\n'
    'components:\n'
    '  CORE:\n'
    '    name: Core\n'
    '    requirements:\n'
    '      1: A single requirement\n'
)


def _write_single_req_feature(pytester: pytest.Pytester) -> None:
    features_dir = pytester.mkdir('features')
    (features_dir / 'app.feature.yaml').write_text(_SINGLE_REQ_FEATURE_YAML)
    pytester.makeini("""
        [pytest]
        feature_yaml_paths = features
    """)


def _feature_coverage_section(result: pytest.RunResult) -> list[str]:
    """Return only the "Feature Coverage" terminal section's lines.

    Isolates the coverage report from unrelated pytest output (e.g. the
    FAILURES section, which legitimately mentions a failing test's name).
    """
    lines = result.outlines
    start = next(i for i, line in enumerate(lines) if 'Feature Coverage' in line) + 1
    end = next(i for i in range(start, len(lines)) if lines[i].startswith('='))
    return lines[start:end]


class TestUserStory1CoverageReflectsVerifiedRequirements:
    """spec.md User Story 1: coverage requires a clean pass, not mere association."""

    pytestmark = pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.9')

    def test_requirement_with_only_a_passing_test_is_covered(self, pytester):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_passes():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(passed=1)
        result.stdout.fnmatch_lines(['*Overall: 1/1 requirements covered (100.0%)*'])

    def test_requirement_with_only_a_failing_test_is_uncovered(self, pytester):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_fails():
                assert False
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(failed=1)
        result.stdout.fnmatch_lines(['*Overall: 0/1 requirements covered (0.0%)*'])

    def test_requirement_with_only_a_skipped_test_is_uncovered(self, pytester):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            @pytest.mark.skip(reason="not ready")
            def test_skipped():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(skipped=1)
        result.stdout.fnmatch_lines(['*Overall: 0/1 requirements covered (0.0%)*'])

    def test_requirement_with_only_an_xfail_test_is_uncovered(self, pytester):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            @pytest.mark.xfail(reason="known bug")
            def test_expected_to_fail():
                assert False
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(xfailed=1)
        result.stdout.fnmatch_lines(['*Overall: 0/1 requirements covered (0.0%)*'])

    def test_requirement_with_a_setup_error_is_uncovered(self, pytester):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.fixture
            def broken():
                raise RuntimeError("setup blew up")

            @pytest.mark.req("app.CORE.1")
            def test_needs_broken_fixture(broken):
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(errors=1)
        result.stdout.fnmatch_lines(['*Overall: 0/1 requirements covered (0.0%)*'])

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.5')
    def test_requirement_with_only_an_unexpected_xpass_test_is_uncovered(
        self, pytester
    ):
        """A non-strict xfail marker whose body actually passes (xpass) must
        not count as coverage (deliberate policy; see ADR-006). Verified here
        end-to-end with a real pytest run, not just unit-level state."""
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            @pytest.mark.xfail(reason="thought this failed", strict=False)
            def test_unexpectedly_passes():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(xpassed=1)
        result.stdout.fnmatch_lines(['*Overall: 0/1 requirements covered (0.0%)*'])


class TestUserStory2OnePassingTestIsEnough:
    """spec.md User Story 2: one clean pass among mixed outcomes still covers."""

    pytestmark = pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.10')

    def test_one_passing_and_one_failing_test_covers_and_lists_only_passing(
        self, pytester
    ):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_passes():
                pass

            @pytest.mark.req("app.CORE.1")
            def test_fails():
                assert False
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(passed=1, failed=1)
        result.stdout.fnmatch_lines(['*Overall: 1/1 requirements covered (100.0%)*'])
        section = _feature_coverage_section(result)
        assert any('test_passes' in line for line in section)
        assert not any('test_fails' in line for line in section)

    def test_one_passing_and_one_skipped_test_covers_and_lists_only_passing(
        self, pytester
    ):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_passes():
                pass

            @pytest.mark.req("app.CORE.1")
            @pytest.mark.skip(reason="not ready")
            def test_skipped():
                pass
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(passed=1, skipped=1)
        result.stdout.fnmatch_lines(['*Overall: 1/1 requirements covered (100.0%)*'])
        result.stdout.fnmatch_lines(['*test_passes*'])

    def test_parametrized_test_with_one_passing_case_covers_and_names_that_case(
        self, pytester
    ):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            @pytest.mark.parametrize("value", [1, 0])
            def test_parametrized(value):
                assert value == 1
        """)
        result = pytester.runpytest('--feature-coverage', '-v')
        result.assert_outcomes(passed=1, failed=1)
        result.stdout.fnmatch_lines(['*Overall: 1/1 requirements covered (100.0%)*'])
        result.stdout.fnmatch_lines(['*test_parametrized[[]1[]]*'])

    def test_parametrized_test_with_zero_passing_cases_is_uncovered(self, pytester):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            @pytest.mark.parametrize("value", [0, -1])
            def test_parametrized(value):
                assert value == 1
        """)
        result = pytester.runpytest('--feature-coverage')
        result.assert_outcomes(failed=2)
        result.stdout.fnmatch_lines(['*Overall: 0/1 requirements covered (0.0%)*'])


class TestUserStory3ThresholdReflectsExecutionAwareCoverage:
    """spec.md User Story 3: --feature-coverage-min is evaluated execution-aware."""

    pytestmark = pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.11')

    def test_threshold_100_exits_nonzero_when_only_test_fails(self, pytester):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_fails():
                assert False
        """)
        result = pytester.runpytest('--feature-coverage', '--feature-coverage-min=100')
        result.assert_outcomes(failed=1)
        assert result.ret != 0
        result.stdout.fnmatch_lines(['*FAILED: Feature coverage 0.0%*'])

    def test_threshold_failure_does_not_override_pytests_own_failure_exit_status(
        self, pytester
    ):
        """FR-009: a failing test's exit status must survive an *also*-failing
        threshold check, not be overwritten by the coverage-threshold logic."""
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_fails():
                assert False
        """)
        result = pytester.runpytest('--feature-coverage', '--feature-coverage-min=100')
        result.assert_outcomes(failed=1)
        assert result.ret == pytest.ExitCode.TESTS_FAILED

    def test_threshold_100_exits_zero_when_all_pass(self, pytester):
        _write_single_req_feature(pytester)
        pytester.makepyfile("""
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_passes():
                pass
        """)
        result = pytester.runpytest('--feature-coverage', '--feature-coverage-min=100')
        result.assert_outcomes(passed=1)
        assert result.ret == 0


class TestUserStory4ReportsAgreeAcrossFormats:
    """spec.md User Story 4: text/JSON/Markdown reports agree on facts."""

    pytestmark = pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.12')

    def test_text_json_markdown_agree_on_totals_and_covering_ids(self, pytester):
        features_dir = pytester.mkdir('features')
        (features_dir / 'app.feature.yaml').write_text(
            'feature:\n'
            "  id: '001'\n"
            '  name: app\n'
            'components:\n'
            '  CORE:\n'
            '    name: Core\n'
            '    requirements:\n'
            '      1: Covered only by a passing test\n'
            '      2: Covered by a mix, only passing test counts\n'
            '      3: Referenced only by a skipped test\n'
        )
        pytester.makeini("""
            [pytest]
            feature_yaml_paths = features
        """)
        test_source = """
            import pytest

            @pytest.mark.req("app.CORE.1")
            def test_one_passes():
                pass

            @pytest.mark.req("app.CORE.2")
            def test_two_passes():
                pass

            @pytest.mark.req("app.CORE.2")
            def test_two_fails():
                assert False

            @pytest.mark.req("app.CORE.3")
            @pytest.mark.skip(reason="not ready")
            def test_three_skipped():
                pass
        """
        pytester.makepyfile(test_source)

        text_result = pytester.runpytest(
            '--feature-coverage', '--feature-coverage-format=text'
        )
        text_result.assert_outcomes(passed=2, failed=1, skipped=1)

        pytester.makepyfile(test_source)
        json_result = pytester.runpytest(
            '--feature-coverage', '--feature-coverage-format=json'
        )
        json_result.assert_outcomes(passed=2, failed=1, skipped=1)

        pytester.makepyfile(test_source)
        md_result = pytester.runpytest(
            '--feature-coverage', '--feature-coverage-format=markdown'
        )
        md_result.assert_outcomes(passed=2, failed=1, skipped=1)

        text_result.stdout.fnmatch_lines(
            ['*Overall: 2/3 requirements covered (66.7%)*']
        )

        import json as json_module

        payload = json_module.loads('\n'.join(_feature_coverage_section(json_result)))
        assert payload['overall'] == {'covered': 2, 'total': 3, 'percentage': 66.7}
        covering = {
            req['composite_id']: req['covering_tests']
            for comp in payload['features'][0]['components']
            for req in comp['requirements']
        }
        assert covering['app.CORE.1'] == [
            'test_text_json_markdown_agree_on_totals_and_covering_ids.py::test_one_passes'
        ]
        assert covering['app.CORE.2'] == [
            'test_text_json_markdown_agree_on_totals_and_covering_ids.py::test_two_passes'
        ]
        assert covering['app.CORE.3'] == []

        md_result.stdout.fnmatch_lines(['*Overall*|*2*|*3*|*66.7%*'])
        md_result.stdout.fnmatch_lines(['*test_one_passes*'])
        md_result.stdout.fnmatch_lines(['*test_two_passes*'])
