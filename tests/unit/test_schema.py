"""Unit tests for schema validation and YAML loading."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


FIXTURES_DIR = Path(__file__).parent.parent / 'data'


class TestSchemaValidation:
    """T007: Unit tests for schema validation (valid YAML, missing fields, invalid types)."""

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.1')
    def test_valid_feature_file_loads(self, reference_yaml_content: dict) -> None:
        from pytest_feature_coverage.schema import FeatureFileModel

        model = FeatureFileModel.model_validate(reference_yaml_content)
        assert model.feature.name == 'sample-feature'
        assert model.feature.id == '001'
        assert len(model.components) == 4

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.1')
    def test_component_with_requirements(self, reference_yaml_content: dict) -> None:
        from pytest_feature_coverage.schema import FeatureFileModel

        model = FeatureFileModel.model_validate(reference_yaml_content)
        parsing = model.components['PARSING']
        assert parsing.name == 'Input parsing'
        assert parsing.requirements == {
            1: 'Parses valid input without error',
            2: 'Rejects malformed input with clear message',
            3: 'Handles empty input gracefully',
        }

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.1')
    def test_empty_requirements_component(self, reference_yaml_content: dict) -> None:
        from pytest_feature_coverage.schema import FeatureFileModel

        model = FeatureFileModel.model_validate(reference_yaml_content)
        empty = model.components['EMPTY']
        assert empty.requirements == {}

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_missing_feature_key_raises(self) -> None:
        from pydantic import ValidationError

        from pytest_feature_coverage.schema import FeatureFileModel

        with pytest.raises(ValidationError, match='feature'):
            FeatureFileModel.model_validate({'components': {}})

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_missing_components_key_raises(self) -> None:
        from pydantic import ValidationError

        from pytest_feature_coverage.schema import FeatureFileModel

        with pytest.raises(ValidationError, match='components'):
            FeatureFileModel.model_validate({'feature': {'id': '1', 'name': 'x'}})

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_missing_feature_name_raises(self) -> None:
        from pydantic import ValidationError

        from pytest_feature_coverage.schema import FeatureFileModel

        with pytest.raises(ValidationError, match='name'):
            FeatureFileModel.model_validate(
                {
                    'feature': {'id': '1'},
                    'components': {},
                }
            )

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_missing_feature_id_raises(self) -> None:
        from pydantic import ValidationError

        from pytest_feature_coverage.schema import FeatureFileModel

        with pytest.raises(ValidationError, match='id'):
            FeatureFileModel.model_validate(
                {
                    'feature': {'name': 'x'},
                    'components': {},
                }
            )

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_missing_component_name_raises(self) -> None:
        from pydantic import ValidationError

        from pytest_feature_coverage.schema import FeatureFileModel

        with pytest.raises(ValidationError, match='name'):
            FeatureFileModel.model_validate(
                {
                    'feature': {'id': '1', 'name': 'x'},
                    'components': {'FOO': {'requirements': {}}},
                }
            )

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_invalid_requirement_key_type_raises(self) -> None:
        from pydantic import ValidationError

        from pytest_feature_coverage.schema import FeatureFileModel

        with pytest.raises(ValidationError):
            FeatureFileModel.model_validate(
                {
                    'feature': {'id': '1', 'name': 'x'},
                    'components': {
                        'FOO': {
                            'name': 'Foo',
                            'requirements': {'not_an_int': 'desc'},
                        }
                    },
                }
            )


class TestYAMLLoading:
    """T008: Unit tests for YAML loading from directory (file discovery, path resolution)."""

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.1')
    def test_load_feature_file(self, reference_yaml_path: Path) -> None:
        from pytest_feature_coverage.schema import load_feature_file

        result = load_feature_file(reference_yaml_path)
        assert result.feature.name == 'sample-feature'
        assert len(result.components) == 4

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_load_feature_file_not_found(self, tmp_path: Path) -> None:
        from pytest_feature_coverage.schema import (
            FeatureFileLoadError,
            load_feature_file,
        )

        with pytest.raises(FeatureFileLoadError, match='not found'):
            load_feature_file(tmp_path / 'nonexistent.feature.yaml')

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_load_feature_file_empty_yaml(self, tmp_path: Path) -> None:
        from pytest_feature_coverage.schema import (
            FeatureFileLoadError,
            load_feature_file,
        )

        empty_file = tmp_path / 'empty.feature.yaml'
        empty_file.write_text('')
        with pytest.raises(FeatureFileLoadError, match='Empty feature file'):
            load_feature_file(empty_file)

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_load_feature_file_invalid_yaml(self, tmp_path: Path) -> None:
        from pytest_feature_coverage.schema import (
            FeatureFileLoadError,
            load_feature_file,
        )

        bad_file = tmp_path / 'bad.feature.yaml'
        bad_file.write_text(': invalid: yaml: [[[')
        with pytest.raises(FeatureFileLoadError):
            load_feature_file(bad_file)

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.2')
    def test_load_feature_file_validation_error(self, tmp_path: Path) -> None:
        from pytest_feature_coverage.schema import (
            FeatureFileLoadError,
            load_feature_file,
        )

        bad_file = tmp_path / 'bad.feature.yaml'
        bad_file.write_text(yaml.dump({'feature': {'id': '1'}, 'components': {}}))
        with pytest.raises(FeatureFileLoadError, match='bad.feature.yaml'):
            load_feature_file(bad_file)

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.1')
    def test_load_all_features_discovers_files(self, tmp_path: Path) -> None:
        from pytest_feature_coverage.schema import load_all_features

        # Create two feature files
        for name in ('a', 'b'):
            content = {
                'feature': {'id': name, 'name': f'feature-{name}'},
                'components': {},
            }
            (tmp_path / f'{name}.feature.yaml').write_text(yaml.dump(content))

        results = load_all_features([tmp_path])
        assert len(results) == 2
        names = {r.feature.name for r in results}
        assert names == {'feature-a', 'feature-b'}

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.1')
    def test_load_all_features_ignores_non_feature_yaml(self, tmp_path: Path) -> None:
        from pytest_feature_coverage.schema import load_all_features

        # Not a *.feature.yaml file
        (tmp_path / 'other.yaml').write_text(yaml.dump({'key': 'value'}))
        content = {
            'feature': {'id': '1', 'name': 'only-feature'},
            'components': {},
        }
        (tmp_path / 'real.feature.yaml').write_text(yaml.dump(content))

        results = load_all_features([tmp_path])
        assert len(results) == 1
        assert results[0].feature.name == 'only-feature'

    @pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.1')
    def test_load_all_features_multiple_directories(self, tmp_path: Path) -> None:
        from pytest_feature_coverage.schema import load_all_features

        dir_a = tmp_path / 'a'
        dir_b = tmp_path / 'b'
        dir_a.mkdir()
        dir_b.mkdir()

        for d, name in ((dir_a, 'feat-a'), (dir_b, 'feat-b')):
            content = {
                'feature': {'id': '1', 'name': name},
                'components': {},
            }
            (d / f'{name}.feature.yaml').write_text(yaml.dump(content))

        results = load_all_features([dir_a, dir_b])
        assert len(results) == 2


class TestDuplicateDetection:
    """T012: Duplicate feature name detection."""

    pytestmark = pytest.mark.req('feature-coverage-plugin.YAML_SCHEMA.3')

    def test_duplicate_feature_names_raises(self, tmp_path: Path) -> None:
        from pytest_feature_coverage.schema import (
            DuplicateFeatureError,
            load_all_features,
        )

        for i in range(2):
            content = {
                'feature': {'id': str(i), 'name': 'same-name'},
                'components': {},
            }
            (tmp_path / f'file{i}.feature.yaml').write_text(yaml.dump(content))

        with pytest.raises(DuplicateFeatureError, match='same-name'):
            load_all_features([tmp_path])

    def test_unique_feature_names_ok(self, tmp_path: Path) -> None:
        from pytest_feature_coverage.schema import load_all_features

        for i in range(2):
            content = {
                'feature': {'id': str(i), 'name': f'feature-{i}'},
                'components': {},
            }
            (tmp_path / f'file{i}.feature.yaml').write_text(yaml.dump(content))

        results = load_all_features([tmp_path])
        assert len(results) == 2
