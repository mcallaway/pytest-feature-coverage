"""pytest-feature-coverage: connect tests to requirements in YAML feature files."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import pytest

if TYPE_CHECKING:
    from .outcomes import OutcomeTracker

_PLUGIN_ACTIVE_ATTR = '_feature_coverage_active'
_PLUGIN_STATE_ATTR = '_feature_coverage_state'


def pytest_addoption(parser: pytest.Parser) -> None:  # pragma: no cover
    """Register CLI options and INI settings for feature coverage."""
    group = parser.getgroup('feature-coverage', 'Feature coverage reporting')
    group.addoption(
        '--feature-coverage',
        action='store_true',
        default=False,
        help='Enable feature coverage reporting',
    )
    group.addoption(
        '--feature-coverage-format',
        choices=['text', 'json', 'markdown'],
        default=None,
        help='Output format for the coverage report (default: text)',
    )
    group.addoption(
        '--feature-coverage-min',
        type=int,
        default=None,
        help='Minimum coverage percentage; exit non-zero if below (default: 0)',
    )
    group.addoption(
        '--feature-coverage-filter',
        action='append',
        default=None,
        metavar='TEXT',
        help='Only show features whose name contains TEXT (case-insensitive). '
        'Repeatable; multiple values combine as OR. Default: show all features.',
    )

    parser.addini(
        'feature_yaml_paths',
        type='paths',
        help='Directories to search for *.feature.yaml files (required)',
    )
    parser.addini(
        'feature_coverage_format',
        default='text',
        help='Default output format (text, json, markdown)',
    )
    parser.addini(
        'feature_coverage_min',
        default='0',
        help='Default minimum coverage threshold (0-100)',
    )
    parser.addini(
        'feature_coverage_strict',
        type='bool',
        default=False,
        help='Treat orphan req() markers as errors',
    )


def pytest_configure(config: pytest.Config) -> None:  # pragma: no cover
    """Register the req marker and determine if the plugin is active."""
    config.addinivalue_line(
        'markers',
        'req(*ids): Associate test with requirement IDs from feature YAML files',
    )

    # Determine activation: --feature-coverage must be explicitly passed
    active = config.getoption('--feature-coverage', default=False)
    setattr(config, _PLUGIN_ACTIVE_ATTR, active)

    if not active:
        return

    # Load feature YAML files
    from pathlib import Path

    from .schema import (
        DuplicateFeatureError,
        FeatureFileLoadError,
        load_all_features,
    )

    yaml_paths = config.getini('feature_yaml_paths')
    if not yaml_paths:
        import _pytest.config

        msg = (
            "feature-coverage: 'feature_yaml_paths' INI option is required "
            'when --feature-coverage is active'
        )
        raise _pytest.config.UsageError(msg)

    directories = [Path(p) for p in yaml_paths]

    try:
        features = load_all_features(directories)
    except (FeatureFileLoadError, DuplicateFeatureError) as e:
        import _pytest.config

        raise _pytest.config.UsageError(str(e)) from e

    from .outcomes import OutcomeTracker

    setattr(
        config,
        _PLUGIN_STATE_ATTR,
        {'features': features, 'outcomes': OutcomeTracker()},
    )


def _is_active(config: pytest.Config) -> bool:
    """Check if the plugin is activated for this session."""
    return getattr(config, _PLUGIN_ACTIVE_ATTR, False)


def _get_threshold(config: pytest.Config) -> int:
    """Resolve coverage threshold: CLI flag > INI option > default (0)."""
    threshold = config.getoption('--feature-coverage-min')
    if threshold is None:
        threshold = int(config.getini('feature_coverage_min'))
    return threshold


def _get_known_requirement_ids(config: pytest.Config) -> set[str]:
    """Build set of all composite requirement IDs from loaded features."""
    state = getattr(config, _PLUGIN_STATE_ATTR, {})
    features = state.get('features', [])
    ids: set[str] = set()
    for feature_file in features:
        name = feature_file.feature.name
        for comp_key, comp in feature_file.components.items():
            for num in comp.requirements:
                ids.add(f'{name}.{comp_key}.{num}')
    return ids


def pytest_collection_modifyitems(  # pragma: no cover
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Scan collected items for req() markers."""
    if not _is_active(config):
        return

    import warnings

    from .scanner import find_orphans, scan_requirements

    req_map = scan_requirements(items)
    known_ids = _get_known_requirement_ids(config)
    orphans = find_orphans(req_map, known_ids)

    state = getattr(config, _PLUGIN_STATE_ATTR)
    state['req_map'] = req_map
    state['orphans'] = orphans

    strict = config.getini('feature_coverage_strict')
    if orphans and strict:
        import _pytest.config

        msg = (
            f'feature-coverage: orphan req() markers found '
            f'(strict mode): {", ".join(orphans)}'
        )
        raise _pytest.config.UsageError(msg)
    elif orphans:
        for orphan in orphans:
            warnings.warn(
                f"feature-coverage: req('{orphan}') does not match any known requirement",
                stacklevel=1,
            )


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(  # pragma: no cover
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Record each finalized phase report's outcome for execution-aware coverage.

    Registered with tryfirst=True so this wrapper is outermost: its `yield`
    resumes only after other wrapper hooks (notably `_pytest.skipping`'s,
    which finalizes `report.outcome`/`report.wasxfail` for xfail/xpass) have
    already run, guaranteeing the report seen here reflects the final verdict.
    """
    report = yield

    config = item.config
    if _is_active(config):
        state = getattr(config, _PLUGIN_STATE_ATTR, None)
        if state is not None:
            tracker: OutcomeTracker = state['outcomes']
            wasxfail = getattr(report, 'wasxfail', None)
            tracker.record(report.nodeid, report.when, report.outcome, wasxfail)

    return report


def _apply_outcome_filter(
    req_map: dict[str, list[str]], passing_nodeids: set[str]
) -> dict[str, list[str]]:
    """Narrow each requirement's covering-test list to only passing node IDs."""
    return {
        req_id: [nodeid for nodeid in nodeids if nodeid in passing_nodeids]
        for req_id, nodeids in req_map.items()
    }


def _compute_and_store_report(config: pytest.Config) -> None:
    """Compute coverage report and store on config state."""
    from .matrix import compute_coverage

    state = getattr(config, _PLUGIN_STATE_ATTR)
    if 'report' in state:
        return

    features = state[
        'features'
    ]  # full list; never mutated (needed for orphan checking)

    filters = config.getoption('--feature-coverage-filter') or []
    if filters:
        lower_filters = [f.lower() for f in filters]
        features = [
            ff
            for ff in features
            if any(f in ff.feature.name.lower() for f in lower_filters)
        ]

    req_map = state.get('req_map', {})
    orphans = state.get('orphans', [])

    tracker: OutcomeTracker = state['outcomes']
    req_map = _apply_outcome_filter(req_map, tracker.passing_nodeids())

    report = compute_coverage(features, req_map)
    report.orphan_markers = orphans
    state['report'] = report


def pytest_sessionfinish(session: pytest.Session) -> None:  # pragma: no cover
    """Set exit code if coverage is below threshold."""
    if not _is_active(session.config):
        return

    config = session.config
    _compute_and_store_report(config)

    state = getattr(config, _PLUGIN_STATE_ATTR)
    report = state['report']
    threshold = _get_threshold(config)

    if threshold > 0 and report.coverage_percentage < threshold:
        state['_threshold_failed'] = True
        # Only escalate the exit status ourselves when pytest's own result
        # was otherwise a clean 0 (all collected tests passed). If pytest
        # already recorded a failure (e.g. TESTS_FAILED), leave it as-is --
        # FR-009 requires that pytest's own failure exit status is never
        # hidden or overwritten by the coverage threshold check.
        if session.exitstatus == 0:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(  # pragma: no cover
    terminalreporter: pytest.TerminalReporter,
    exitstatus: int,
    config: pytest.Config,
) -> None:
    """Print the feature coverage report."""
    if not _is_active(config):
        return

    from .reporters.text import render_text

    _compute_and_store_report(config)
    state = getattr(config, _PLUGIN_STATE_ATTR)
    report = state['report']

    # Determine format
    fmt = config.getoption('--feature-coverage-format') or config.getini(
        'feature_coverage_format'
    )

    if fmt == 'json':
        from .reporters.json import render_json

        terminalreporter.section('Feature Coverage')
        terminalreporter.write_line(render_json(report))
    elif fmt == 'markdown':
        from .reporters.markdown import render_markdown

        terminalreporter.section('Feature Coverage')
        terminalreporter.write_line(render_markdown(report))
    else:
        lines = render_text(report)
        terminalreporter.section('Feature Coverage')
        for line in lines:
            terminalreporter.write_line(line)

    if state.get('_threshold_failed'):
        terminalreporter.write_line(
            f'FAILED: Feature coverage {report.coverage_percentage:.1f}% '
            f'is below minimum {_get_threshold(config)}%'
        )
