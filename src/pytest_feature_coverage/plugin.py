"""pytest-feature-coverage: connect tests to requirements in YAML feature files."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

_PLUGIN_ACTIVE_ATTR = '_feature_coverage_active'
_PLUGIN_STATE_ATTR = '_feature_coverage_state'


def pytest_addoption(parser: pytest.Parser) -> None:
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


def pytest_configure(config: pytest.Config) -> None:
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

    setattr(config, _PLUGIN_STATE_ATTR, {'features': features})


def _is_active(config: pytest.Config) -> bool:
    """Check if the plugin is activated for this session."""
    return getattr(config, _PLUGIN_ACTIVE_ATTR, False)


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


def pytest_collection_modifyitems(
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


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter, config: pytest.Config
) -> None:
    """Print the feature coverage report."""
    if not _is_active(config):
        return

    from .matrix import compute_coverage
    from .reporters.text import render_text

    state = getattr(config, _PLUGIN_STATE_ATTR)
    features = state['features']
    req_map = state.get('req_map', {})
    orphans = state.get('orphans', [])

    report = compute_coverage(features, req_map)
    report.orphan_markers = orphans
    state['report'] = report

    # Determine format
    fmt = config.getoption('--feature-coverage-format') or config.getini(
        'feature_coverage_format'
    )

    if fmt == 'text':
        lines = render_text(report)
    else:
        # JSON and markdown handled in later phases
        lines = render_text(report)

    terminalreporter.section('Feature Coverage')
    for line in lines:
        terminalreporter.write_line(line)
