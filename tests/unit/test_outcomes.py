"""Unit tests for OutcomeTracker (execution-aware pass/fail tracking)."""

from __future__ import annotations

import pytest


class TestOutcomeTrackerPassingNodeids:
    """Tests for OutcomeTracker.record / passing_nodeids."""

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.1')
    def test_clean_pass_is_covering(self) -> None:
        from pytest_feature_coverage.outcomes import OutcomeTracker

        tracker = OutcomeTracker()
        tracker.record('t.py::test_a', 'setup', 'passed', None)
        tracker.record('t.py::test_a', 'call', 'passed', None)
        tracker.record('t.py::test_a', 'teardown', 'passed', None)
        assert tracker.passing_nodeids() == {'t.py::test_a'}

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.2')
    def test_failing_call_is_not_covering(self) -> None:
        from pytest_feature_coverage.outcomes import OutcomeTracker

        tracker = OutcomeTracker()
        tracker.record('t.py::test_a', 'setup', 'passed', None)
        tracker.record('t.py::test_a', 'call', 'failed', None)
        tracker.record('t.py::test_a', 'teardown', 'passed', None)
        assert tracker.passing_nodeids() == set()

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.3')
    def test_plain_skip_is_not_covering(self) -> None:
        from pytest_feature_coverage.outcomes import OutcomeTracker

        tracker = OutcomeTracker()
        tracker.record('t.py::test_a', 'setup', 'passed', None)
        tracker.record('t.py::test_a', 'call', 'skipped', None)
        tracker.record('t.py::test_a', 'teardown', 'passed', None)
        assert tracker.passing_nodeids() == set()

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.4')
    def test_expected_xfail_is_not_covering(self) -> None:
        """Expected xfail reports as a "skipped" call outcome with wasxfail set."""
        from pytest_feature_coverage.outcomes import OutcomeTracker

        tracker = OutcomeTracker()
        tracker.record('t.py::test_a', 'setup', 'passed', None)
        tracker.record('t.py::test_a', 'call', 'skipped', 'reason: expected to fail')
        tracker.record('t.py::test_a', 'teardown', 'passed', None)
        assert tracker.passing_nodeids() == set()

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.5')
    def test_unexpected_xpass_is_not_covering(self) -> None:
        """Non-strict xpass reports outcome="passed" but with wasxfail set."""
        from pytest_feature_coverage.outcomes import OutcomeTracker

        tracker = OutcomeTracker()
        tracker.record('t.py::test_a', 'setup', 'passed', None)
        tracker.record('t.py::test_a', 'call', 'passed', 'reason: expected to fail')
        tracker.record('t.py::test_a', 'teardown', 'passed', None)
        assert tracker.passing_nodeids() == set()

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.6')
    def test_setup_error_is_not_covering(self) -> None:
        """A failing setup means no call report is ever generated."""
        from pytest_feature_coverage.outcomes import OutcomeTracker

        tracker = OutcomeTracker()
        tracker.record('t.py::test_a', 'setup', 'failed', None)
        assert tracker.passing_nodeids() == set()

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.7')
    def test_teardown_error_overrides_prior_passing_call(self) -> None:
        from pytest_feature_coverage.outcomes import OutcomeTracker

        tracker = OutcomeTracker()
        tracker.record('t.py::test_a', 'setup', 'passed', None)
        tracker.record('t.py::test_a', 'call', 'passed', None)
        tracker.record('t.py::test_a', 'teardown', 'failed', None)
        assert tracker.passing_nodeids() == set()

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.7')
    def test_teardown_skip_overrides_prior_passing_call(self) -> None:
        """A fixture finalizer that skips during teardown is not a clean pass."""
        from pytest_feature_coverage.outcomes import OutcomeTracker

        tracker = OutcomeTracker()
        tracker.record('t.py::test_a', 'setup', 'passed', None)
        tracker.record('t.py::test_a', 'call', 'passed', None)
        tracker.record('t.py::test_a', 'teardown', 'skipped', None)
        assert tracker.passing_nodeids() == set()

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.8')
    def test_node_ids_tracked_independently(self) -> None:
        from pytest_feature_coverage.outcomes import OutcomeTracker

        tracker = OutcomeTracker()
        tracker.record('t.py::test_pass', 'setup', 'passed', None)
        tracker.record('t.py::test_pass', 'call', 'passed', None)
        tracker.record('t.py::test_pass', 'teardown', 'passed', None)
        tracker.record('t.py::test_fail', 'setup', 'passed', None)
        tracker.record('t.py::test_fail', 'call', 'failed', None)
        tracker.record('t.py::test_fail', 'teardown', 'passed', None)
        assert tracker.passing_nodeids() == {'t.py::test_pass'}

    @pytest.mark.req('feature-coverage-plugin.EXECUTION_COVERAGE.8')
    def test_no_reports_recorded_yields_empty_set(self) -> None:
        from pytest_feature_coverage.outcomes import OutcomeTracker

        assert OutcomeTracker().passing_nodeids() == set()
