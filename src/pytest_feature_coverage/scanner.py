"""Scan test items for req() markers and detect orphans (FR-005, FR-006, FR-010)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    import pytest


def scan_requirements(items: Sequence[pytest.Item]) -> dict[str, list[str]]:
    """Collect all req() marker arguments mapped to test node IDs.

    Returns a dict of {requirement_id: [node_id, ...]}.
    """
    req_map: dict[str, list[str]] = {}

    for item in items:
        for marker in item.iter_markers(name='req'):
            for req_id in marker.args:
                req_map.setdefault(req_id, []).append(item.nodeid)

    return req_map


def find_orphans(req_map: dict[str, list[str]], known_ids: Iterable[str]) -> list[str]:
    """Find req() IDs that don't match any known requirement.

    Returns sorted list of orphan IDs.
    """
    known = set(known_ids)
    return sorted(rid for rid in req_map if rid not in known)
