# Data Model: Feature Coverage Plugin

**Date**: 2025-05-19\
**Feature**: [spec.md](spec.md)

## Entities

### Feature

A top-level grouping defined in a `*.feature.yaml` file.

| Field | Type | Description                                                             |
| ----- | ---- | ----------------------------------------------------------------------- |
| id    | str  | Short identifier (e.g., `"002"`)                                        |
| name  | str  | Kebab-case name used in requirement IDs (e.g., `"contract-validation"`) |

**Identity**: Uniqueness determined by `name`. Two features with the same `name` across different YAML files is an error (FR-011).

### Component

A named grouping within a feature. Component names are used literally in requirement IDs.

| Field        | Type           | Description                                                   |
| ------------ | -------------- | ------------------------------------------------------------- |
| key          | str            | Dictionary key in YAML (e.g., `"STRUCTURE"`). Case-sensitive. |
| name         | str            | Human-readable display name                                   |
| requirements | dict[int, str] | Number → description mapping                                  |

**Identity**: Uniqueness scoped to parent feature. Two components in the same feature cannot share a key.

**Validation**: A component with zero requirements is valid (shows 0/0 in report, excluded from overall percentage).

### Requirement

A numbered statement within a component.

| Field        | Type          | Description                                 |
| ------------ | ------------- | ------------------------------------------- |
| number       | int           | Positive integer key within the component   |
| description  | str           | Human-readable requirement text             |
| composite_id | str (derived) | `"{feature.name}.{component.key}.{number}"` |

**Identity**: `composite_id` is globally unique. Duplicates across features trigger an error at collection time.

**Matching**: Case-sensitive. `req("contract-validation.STRUCTURE.1")` must exactly match the YAML-derived composite ID.

### CoverageEntry

A single row in the coverage matrix.

| Field          | Type           | Description                                     |
| -------------- | -------------- | ----------------------------------------------- |
| requirement    | Requirement    | The requirement being tracked                   |
| covering_tests | list[str]      | Node IDs of tests with matching `req()` markers |
| is_covered     | bool (derived) | `len(covering_tests) > 0`                       |

### CoverageReport

The complete coverage computation result.

| Field                | Type                     | Description                                           |
| -------------------- | ------------------------ | ----------------------------------------------------- |
| features             | list[Feature]            | All loaded features (sorted by name for determinism)  |
| entries              | dict[str, CoverageEntry] | Keyed by composite requirement ID                     |
| total_requirements   | int                      | Count of all requirements across all features         |
| covered_requirements | int                      | Count of requirements with at least one covering test |
| coverage_percentage  | float                    | `covered / total * 100` (0.0 if total == 0)           |
| orphan_markers       | list[str]                | `req()` IDs not matching any known requirement        |

## Relationships

```text
Feature 1──* Component 1──* Requirement
                                  │
                                  │ (many-to-many via req() markers)
                                  │
                            Test Item
```

- Feature → Component: one-to-many (dict in YAML)
- Component → Requirement: one-to-many (numbered dict in YAML)
- Requirement ↔ Test: many-to-many (a test may have multiple `req()` args; a requirement may be covered by multiple tests)

## YAML Schema (Pydantic Models)

```python
from pydantic import BaseModel

class FeatureModel(BaseModel):
    id: str
    name: str

class ComponentModel(BaseModel):
    name: str
    requirements: dict[int, str]  # number → description

class FeatureFileModel(BaseModel):
    feature: FeatureModel
    components: dict[str, ComponentModel]  # key → component
```

## Example YAML → Derived IDs

```yaml
feature:
  id: "002"
  name: contract-validation

components:
  STRUCTURE:
    name: Contract YAML structure
    requirements:
      1: Contract YAML files have all required fields
      2: Ontology class references point to existing LinkML classes
  VALIDATOR:
    name: Runtime validation
    requirements:
      1: Correctly extracts entity IDs from view data
```

Derived composite IDs:

- `contract-validation.STRUCTURE.1`
- `contract-validation.STRUCTURE.2`
- `contract-validation.VALIDATOR.1`

## State Transitions

N/A — this is a stateless, read-only computation. No persistence or mutation.

## Validation Rules

| Rule                                    | Trigger    | Severity                                          |
| --------------------------------------- | ---------- | ------------------------------------------------- |
| YAML doesn't match schema               | Collection | Error (fail collection)                           |
| Duplicate `feature.name` across files   | Collection | Error (fail collection)                           |
| Duplicate composite requirement ID      | Collection | Error (fail collection)                           |
| `req()` marker ID not in any YAML       | Collection | Warning (error if `feature_coverage_strict=true`) |
| Component with 0 requirements           | Collection | Valid (silent)                                    |
| No `feature_yaml_paths` configured      | Collection | Error (fail with message)                         |
| No YAML files found in configured paths | Report     | Warning message in report                         |
