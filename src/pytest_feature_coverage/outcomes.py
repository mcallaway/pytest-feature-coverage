"""Execution-aware pass/fail tracking for feature coverage (see ADR-006).

Tracks, per collected test node ID, whether that node achieved a "clean
pass" during a pytest session: its ``call`` phase reported ``outcome ==
"passed"`` with no ``wasxfail`` (excludes unexpected xpass), and no phase
(``setup``/``call``/``teardown``) reported an ``outcome`` other than
``"passed"`` (this excludes both a ``"failed"`` phase and a ``"skipped"``
phase, e.g. a fixture finalizer calling ``pytest.skip()`` during teardown).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _NodeOutcome:
    """Accumulated setup/call/teardown verdict for one test node ID."""

    call_passed: bool = False
    errored: bool = False


class OutcomeTracker:
    """Owns the per-node-ID outcome state for a pytest session.

    A new instance is constructed exactly once per pytest session (see
    ``pytest_configure`` in ``plugin.py``). This class is not designed to be
    reused or reset across sessions -- there is no ``reset()``/``clear()``
    method by design, since state that outlives a single session would be
    stale by construction.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, _NodeOutcome] = {}

    def record(
        self, nodeid: str, when: str | None, outcome: str, wasxfail: str | None
    ) -> None:
        """Fold one finalized phase report into the node's running verdict."""
        node = self._nodes.setdefault(nodeid, _NodeOutcome())

        if outcome != 'passed':
            # Any non-"passed" phase (failed, or skipped -- including an
            # unhandled xfail, which reports as "skipped") disqualifies the
            # node, even if it happens during setup/teardown after an
            # already-passing call phase (e.g. a fixture finalizer that
            # calls pytest.skip()).
            node.errored = True
        elif when == 'call' and wasxfail is None:
            node.call_passed = True

    def passing_nodeids(self) -> set[str]:
        """Return the node IDs that achieved a clean pass."""
        return {
            nodeid
            for nodeid, node in self._nodes.items()
            if node.call_passed and not node.errored
        }
