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


def _is_active(config: pytest.Config) -> bool:
    """Check if the plugin is activated for this session."""
    return getattr(config, _PLUGIN_ACTIVE_ATTR, False)
