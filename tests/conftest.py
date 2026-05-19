"""Shared test configuration for pytest-feature-coverage."""

from pathlib import Path

import pytest

# Enable pytester for acceptance tests that invoke pytest in a subprocess
pytest_plugins = ['pytester']

FIXTURES_DIR = Path(__file__).parent / 'data'


@pytest.fixture
def reference_yaml_path() -> Path:
    """Path to the reference feature YAML fixture."""
    return FIXTURES_DIR / 'reference.feature.yaml'


@pytest.fixture
def reference_yaml_content(reference_yaml_path: Path) -> str:
    """Raw content of the reference feature YAML fixture."""
    return reference_yaml_path.read_text()
