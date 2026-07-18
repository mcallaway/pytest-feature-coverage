"""Unit tests for the requirement marker scanner."""

from __future__ import annotations

import types

import pytest


def _make_item(
    marker_args_list: list[tuple[str, ...]], nodeid: str = 'test_file.py::test_example'
) -> types.SimpleNamespace:
    """Create a stub pytest Item with req markers."""
    markers = [types.SimpleNamespace(args=args, kwargs={}) for args in marker_args_list]
    return types.SimpleNamespace(
        nodeid=nodeid,
        iter_markers=lambda name: iter(markers),
    )


class TestScanRequirements:
    """T016: Unit tests for scanner."""

    @pytest.mark.req('feature-coverage-plugin.REQ_MARKER.1')
    def test_single_marker_single_arg(self) -> None:
        from pytest_feature_coverage.scanner import scan_requirements

        item = _make_item([('feat.COMP.1',)])
        result = scan_requirements([item])
        assert result == {'feat.COMP.1': ['test_file.py::test_example']}

    @pytest.mark.req('feature-coverage-plugin.REQ_MARKER.2')
    def test_single_marker_multiple_args(self) -> None:
        from pytest_feature_coverage.scanner import scan_requirements

        item = _make_item([('feat.COMP.1', 'feat.COMP.2')])
        result = scan_requirements([item])
        assert 'feat.COMP.1' in result
        assert 'feat.COMP.2' in result
        assert result['feat.COMP.1'] == ['test_file.py::test_example']

    @pytest.mark.req('feature-coverage-plugin.REQ_MARKER.1')
    def test_multiple_markers(self) -> None:
        from pytest_feature_coverage.scanner import scan_requirements

        item = _make_item([('feat.A.1',), ('feat.B.2',)])
        result = scan_requirements([item])
        assert 'feat.A.1' in result
        assert 'feat.B.2' in result

    def test_no_markers(self) -> None:
        from pytest_feature_coverage.scanner import scan_requirements

        item = _make_item([])
        result = scan_requirements([item])
        assert result == {}

    @pytest.mark.req('feature-coverage-plugin.REQ_MARKER.1')
    def test_multiple_items_same_req(self) -> None:
        from pytest_feature_coverage.scanner import scan_requirements

        item1 = _make_item([('feat.COMP.1',)])
        item1.nodeid = 'test_a.py::test_one'
        item2 = _make_item([('feat.COMP.1',)])
        item2.nodeid = 'test_b.py::test_two'

        result = scan_requirements([item1, item2])
        assert result['feat.COMP.1'] == ['test_a.py::test_one', 'test_b.py::test_two']


class TestOrphanDetection:
    """T019: Orphan marker detection."""

    pytestmark = pytest.mark.req('feature-coverage-plugin.REQ_MARKER.3')

    def test_detects_orphans(self) -> None:
        from pytest_feature_coverage.scanner import find_orphans

        req_map = {'feat.COMP.1': ['test.py::t1'], 'feat.COMP.99': ['test.py::t2']}
        known_ids = {'feat.COMP.1'}
        orphans = find_orphans(req_map, known_ids)
        assert orphans == ['feat.COMP.99']

    def test_no_orphans(self) -> None:
        from pytest_feature_coverage.scanner import find_orphans

        req_map = {'feat.COMP.1': ['test.py::t1']}
        known_ids = {'feat.COMP.1'}
        orphans = find_orphans(req_map, known_ids)
        assert orphans == []
