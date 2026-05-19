"""YAML feature file schema and loading (FR-001 through FR-004, FR-011, FR-014)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Sequence


class FeatureFileLoadError(Exception):
    """Raised when a feature YAML file cannot be loaded or validated."""


class DuplicateFeatureError(Exception):
    """Raised when two feature files define the same feature name."""


class FeatureModel(BaseModel):
    """Top-level feature identity."""

    id: str
    name: str


class ComponentModel(BaseModel):
    """A component within a feature containing numbered requirements."""

    name: str
    requirements: dict[int, str] = {}


class FeatureFileModel(BaseModel):
    """Root schema for a *.feature.yaml file."""

    feature: FeatureModel
    components: dict[str, ComponentModel]


def load_feature_file(path: Path) -> FeatureFileModel:
    """Load and validate a single feature YAML file.

    Raises FeatureFileLoadError with file path context on any failure.
    """
    if not path.exists():
        msg = f'Feature file not found: {path}'
        raise FeatureFileLoadError(msg)

    try:
        raw = yaml.safe_load(path.read_text(encoding='utf-8'))
    except yaml.YAMLError as e:
        msg = f'Invalid YAML in {path}: {e}'
        raise FeatureFileLoadError(msg) from e

    if raw is None:
        msg = f'Empty feature file: {path}'
        raise FeatureFileLoadError(msg)

    try:
        return FeatureFileModel.model_validate(raw)
    except Exception as e:
        msg = f'Validation error in {path}: {e}'
        raise FeatureFileLoadError(msg) from e


def load_all_features(directories: Sequence[Path]) -> list[FeatureFileModel]:
    """Discover and load all *.feature.yaml files from given directories.

    Raises DuplicateFeatureError if two files define the same feature name.
    Raises FeatureFileLoadError for any file-level issues.
    """
    results: list[FeatureFileModel] = []
    seen_names: dict[str, Path] = {}

    for directory in directories:
        for path in sorted(directory.glob('*.feature.yaml')):
            model = load_feature_file(path)
            name = model.feature.name

            if name in seen_names:
                msg = (
                    f"Duplicate feature name '{name}' found in "
                    f'{path} and {seen_names[name]}'
                )
                raise DuplicateFeatureError(msg)

            seen_names[name] = path
            results.append(model)

    return results
