"""Shared test configuration for pytest-feature-coverage."""

from pathlib import Path

import pytest
import yaml

# Enable pytester for integration tests that invoke pytest in a subprocess
pytest_plugins = ['pytester']

FIXTURES_DIR = Path(__file__).parent / 'data'


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register feature-coverage INI options as fallbacks when the plugin is disabled.

    addini silently overwrites duplicate registrations, so this always registers
    the options — either as the primary registration (plugin disabled via
    -p no:feature_coverage) or as a harmless duplicate (plugin active).
    """
    for name, kwargs in (
        (
            'feature_yaml_paths',
            {'type': 'paths', 'help': 'Paths to *.feature.yaml dirs'},
        ),
        ('feature_coverage_format', {'default': 'text', 'help': 'Output format'}),
        (
            'feature_coverage_min',
            {'default': '0', 'help': 'Minimum coverage threshold'},
        ),
        (
            'feature_coverage_strict',
            {'type': 'bool', 'default': False, 'help': 'Strict mode'},
        ),
    ):
        parser.addini(name, **kwargs)


@pytest.fixture
def reference_yaml_path() -> Path:
    """Path to the reference feature YAML fixture."""
    return FIXTURES_DIR / 'reference.feature.yaml'


@pytest.fixture
def reference_yaml_content(reference_yaml_path: Path) -> dict:
    """Parsed content of the reference feature YAML fixture."""
    return yaml.safe_load(reference_yaml_path.read_text())
